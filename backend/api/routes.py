"""FastAPI API routes for the decision engine."""
import time
from fastapi import APIRouter, HTTPException, Query
from models.case import CaseInput
from models.decision import DecisionOutput, RetrievedPolicy, PolicyCitation, ToolCallResult, EvaluationResult, WhyThisDecision
from models.trace import TraceListResponse, TraceListItem
from db.operations import get_trace, list_traces
from rag.vectorstore import seed_vector_store

router = APIRouter(prefix="/api")


@router.post("/cases/review")
async def review_case(case: CaseInput):
    """Run the full decision workflow on a case.
    
    Invokes the LangGraph workflow, which:
    1. Parses the case
    2. Retrieves relevant policies
    3. Makes a preliminary decision
    4. Calls tools if needed
    5. Generates final structured decision
    6. Evaluates decision quality
    7. Suggests improvements if weak
    8. Saves the complete trace
    """
    # Import here to avoid circular imports during module loading
    from workflow.graph import workflow
    
    start = time.time()
    
    try:
        # Run the LangGraph workflow
        result = workflow.invoke({
            "case_input": case.model_dump(),
            "parsed_case": {},
            "retrieved_policies": [],
            "preliminary_decision": {},
            "tool_calls": [],
            "tool_needed": True,
            "final_decision": {},
            "evaluation": {},
            "improvement_suggestion": "",
            "node_trace": [],
            "trace_id": "",
        })
        
        final = result.get("final_decision", {})
        evaluation = result.get("evaluation", {})
        
        # Build structured response
        response = DecisionOutput(
            decision=final.get("decision", "NEED_MORE_INFO"),
            confidence=final.get("confidence", 0.0),
            reason=final.get("reason", "Unable to determine"),
            why_this_decision=WhyThisDecision(
                policy_clause_used=final.get("why_this_decision", {}).get("policy_clause_used", "N/A"),
                key_condition_matched=final.get("why_this_decision", {}).get("key_condition_matched", "N/A"),
                key_constraint_triggered=final.get("why_this_decision", {}).get("key_constraint_triggered", "N/A"),
            ),
            policy_citations=[
                PolicyCitation(**c) for c in final.get("policy_citations", [])
            ],
            retrieved_policies=[
                RetrievedPolicy(
                    policy_id=p.get("policy_id", ""),
                    policy_name=p.get("policy_name", ""),
                    content=p.get("content", ""),
                    relevance_score=p.get("relevance_score", 0.0),
                )
                for p in result.get("retrieved_policies", [])
            ],
            tool_calls=[
                ToolCallResult(**t) for t in result.get("tool_calls", [])
            ],
            evaluation=EvaluationResult(
                grounded=evaluation.get("grounded", False),
                grounded_explanation=evaluation.get("grounded_explanation", ""),
                policy_consistent=evaluation.get("policy_consistent", False),
                policy_consistent_explanation=evaluation.get("policy_consistent_explanation", ""),
                escalation_decision_correct=evaluation.get("escalation_decision_correct", True),
                escalation_explanation=evaluation.get("escalation_explanation", ""),
                retrieval_sufficient=evaluation.get("retrieval_sufficient", True),
                retrieval_explanation=evaluation.get("retrieval_explanation", ""),
                retrieval_quality=evaluation.get("retrieval_quality", "clean"),
                retrieval_quality_explanation=evaluation.get("retrieval_quality_explanation", ""),
                overall_score=evaluation.get("overall_score", 0.5),
                details=evaluation.get("details", ""),
            ),
            improvement_suggestion=result.get("improvement_suggestion") or None,
            trace_id=result.get("trace_id", ""),
        )
        
        return response.model_dump()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/traces")
async def get_traces(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List all traces with pagination."""
    items, total = list_traces(page=page, limit=limit)
    return TraceListResponse(
        traces=items,
        total=total,
        page=page,
        limit=limit,
    ).model_dump()


@router.get("/traces/{trace_id}")
async def get_trace_detail(trace_id: str):
    """Get full trace detail by ID."""
    trace = get_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.model_dump()


@router.post("/seed")
async def seed_data():
    """Seed the vector store with policy documents."""
    try:
        count = seed_vector_store()
        return {"status": "seeded", "chunks_indexed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "opspilot-ai-backend"}
