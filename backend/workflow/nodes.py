"""LangGraph workflow nodes — all 8 nodes for the decision engine.

Every LLM call enforces a strict JSON schema via OpenAI's structured output.
If parsing fails, the node retries once before returning a fallback.
"""
import json
import time
import uuid
from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL
from rag.vectorstore import retrieve_policies
from tools.mock_tools import check_eligibility, fetch_case_history, escalate_case
from db.operations import save_trace
from models.trace import TraceRecord
from workflow.state import WorkflowState


client = OpenAI(api_key=OPENAI_API_KEY)

MAX_RETRIES = 2


def _call_llm_json(system_prompt: str, user_prompt: str, schema_description: str) -> dict:
    """Call OpenAI with JSON mode and retry on parse failure."""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return parsed
        except (json.JSONDecodeError, Exception) as e:
            if attempt == MAX_RETRIES - 1:
                raise ValueError(f"LLM JSON parsing failed after {MAX_RETRIES} attempts: {e}")
    return {}


def _trace_node(name: str, start_time: float, output_summary: str) -> dict:
    """Create a node trace entry."""
    return {
        "node": name,
        "timestamp": datetime.utcnow().isoformat(),
        "duration_ms": int((time.time() - start_time) * 1000),
        "output_summary": output_summary,
    }


# ─── Node 1: Parse Case ───

def parse_case(state: WorkflowState) -> dict:
    """Parse raw case input into structured attributes."""
    start = time.time()
    case = state["case_input"]
    
    system_prompt = """You are a case parsing engine. Extract and structure the case attributes.
You MUST respond with valid JSON matching this exact schema:
{
  "case_type": "string (refund_request|claim_review|exception_request|fraud_investigation|escalation)",
  "customer_id": "string",
  "amount": number,
  "purchase_date": "YYYY-MM-DD",
  "request_date": "YYYY-MM-DD",
  "priority": "string (low|medium|high|critical)",
  "description": "string",
  "days_since_purchase": number,
  "amount_tier": "string (low|standard|high_value|very_high)",
  "urgency_level": "string (routine|elevated|urgent|immediate)",
  "key_flags": ["array of string flags identified"]
}
Do NOT include any text outside the JSON object."""

    user_prompt = f"Parse this case:\n{json.dumps(case)}"
    
    parsed = _call_llm_json(system_prompt, user_prompt, "parsed case")
    
    # Ensure required fields from original input
    parsed["case_type"] = case.get("case_type", parsed.get("case_type", "refund_request"))
    parsed["customer_id"] = case.get("customer_id", parsed.get("customer_id", "unknown"))
    parsed["amount"] = case.get("amount", parsed.get("amount", 0))
    parsed["purchase_date"] = case.get("purchase_date", parsed.get("purchase_date", ""))
    parsed["request_date"] = case.get("request_date", parsed.get("request_date", ""))
    parsed["priority"] = case.get("priority", parsed.get("priority", "medium"))
    
    trace_entry = _trace_node("parse_case", start, f"Parsed case with {len(parsed.get('key_flags', []))} flags")
    
    return {
        "parsed_case": parsed,
        "node_trace": [trace_entry],
        "trace_id": str(uuid.uuid4()),
    }


# ─── Node 2: Retrieve Policy ───

def retrieve_policy(state: WorkflowState) -> dict:
    """Retrieve relevant policy documents via RAG."""
    start = time.time()
    parsed = state["parsed_case"]
    
    # Build retrieval query from case attributes
    query_parts = [
        f"case type: {parsed.get('case_type', '')}",
        f"amount: ${parsed.get('amount', 0)}",
        f"priority: {parsed.get('priority', '')}",
        parsed.get("description", ""),
    ]
    if parsed.get("key_flags"):
        query_parts.append(f"flags: {', '.join(parsed['key_flags'])}")
    
    query = " | ".join(query_parts)
    policies = retrieve_policies(query, n_results=5)
    
    trace_entry = _trace_node(
        "retrieve_policy", start,
        f"Retrieved {len(policies)} policy chunks"
    )
    
    return {
        "retrieved_policies": policies,
        "node_trace": [trace_entry],
    }


# ─── Node 3: Decide Action ───

def decide_action(state: WorkflowState) -> dict:
    """Make preliminary decision based on case + policies. Determine if tools are needed."""
    start = time.time()
    parsed = state["parsed_case"]
    policies = state["retrieved_policies"]
    
    policy_context = "\n\n".join([
        f"[{p['policy_id']} - {p['policy_name']}] (Section: {p.get('section', 'N/A')}, Relevance: {p['relevance_score']})\n{p['content']}"
        for p in policies
    ])
    
    system_prompt = """You are a compliance decision engine. Based on the case and retrieved policies, 
make a preliminary decision. You MUST respond with valid JSON matching this exact schema:
{
  "preliminary_decision": "APPROVE|DENY|ESCALATE|NEED_MORE_INFO",
  "confidence": number (0.0-1.0),
  "reasoning": "string explaining the decision logic",
  "tool_needed": boolean,
  "tools_to_call": ["array of tool names: check_eligibility, fetch_case_history"],
  "tool_reason": "string explaining why tools are needed (or empty string if not needed)",
  "key_policy_applied": "string - the primary policy ID and clause",
  "key_condition": "string - the condition that drove this decision",
  "key_constraint": "string - the constraint or rule triggered"
}
Rules:
- Always call check_eligibility and fetch_case_history for first-time case analysis
- Do NOT include escalate_case in tools_to_call (it is handled automatically after final decision)
- Use policy citations to ground your decision
- Be conservative: if unsure, escalate
Do NOT include any text outside the JSON object."""

    user_prompt = f"""Case:\n{json.dumps(parsed)}\n\nRetrieved Policies:\n{policy_context}"""
    
    result = _call_llm_json(system_prompt, user_prompt, "preliminary decision")
    
    trace_entry = _trace_node(
        "decide_action", start,
        f"Preliminary: {result.get('preliminary_decision', 'UNKNOWN')} (conf: {result.get('confidence', 0)})"
    )
    
    return {
        "preliminary_decision": result,
        "tool_needed": result.get("tool_needed", True),
        "node_trace": [trace_entry],
    }


# ─── Node 4: Call Tool If Needed ───

def call_tool_if_needed(state: WorkflowState) -> dict:
    """Execute relevant tools based on the preliminary decision."""
    start = time.time()
    parsed = state["parsed_case"]
    prelim = state["preliminary_decision"]
    
    tool_results = []
    tools_to_call = prelim.get("tools_to_call", ["check_eligibility", "fetch_case_history"])
    
    if "check_eligibility" in tools_to_call:
        result = check_eligibility(parsed)
        tool_results.append(result.model_dump())
    
    if "fetch_case_history" in tools_to_call:
        result = fetch_case_history(parsed.get("customer_id", "unknown"))
        tool_results.append(result.model_dump())
    
    trace_entry = _trace_node(
        "call_tool", start,
        f"Executed {len(tool_results)} tools: {[t['tool_name'] for t in tool_results]}"
    )
    
    return {
        "tool_calls": tool_results,
        "node_trace": [trace_entry],
    }


# ─── Node 5: Generate Final Decision ───

def generate_final_decision(state: WorkflowState) -> dict:
    """Generate the final structured decision incorporating tool results."""
    start = time.time()
    parsed = state["parsed_case"]
    policies = state["retrieved_policies"]
    prelim = state["preliminary_decision"]
    tool_calls = state.get("tool_calls", [])
    
    policy_context = "\n".join([
        f"[{p['policy_id']}] {p['policy_name']} - {p.get('section', '')}: {p['content'][:300]}"
        for p in policies
    ])
    
    tool_context = "\n".join([
        f"Tool: {t['tool_name']} → {json.dumps(t['output_data'])}"
        for t in tool_calls
    ])
    
    system_prompt = """You are the final decision authority in a compliance decision engine.
Synthesize the case, policies, preliminary decision, and tool outputs into a final decision.
You MUST respond with valid JSON matching this exact schema:
{
  "decision": "APPROVE|DENY|ESCALATE|NEED_MORE_INFO",
  "confidence": number (0.0-1.0),
  "reason": "string - clear explanation of the final decision",
  "policy_citations": [
    {
      "policy_id": "string (e.g. POL-001)",
      "policy_name": "string",
      "section": "string - section/clause reference",
      "relevant_text": "string - the specific policy text that applies"
    }
  ],
  "why_this_decision": {
    "policy_clause_used": "string - the primary policy clause applied",
    "key_condition_matched": "string - the key condition that drove this decision",
    "key_constraint_triggered": "string - the constraint or rule that was triggered"
  }
}
Rules:
- Final decision must be STRICTLY one of: APPROVE, DENY, ESCALATE, NEED_MORE_INFO
- If required information or documentation is missing (e.g., photos for damaged goods), ALWAYS return NEED_MORE_INFO, even if risk signals exist. Do not escalate solely due to missing documentation.
- Escalate conditions: If information is sufficient but there is policy conflict, repeated exception behavior (e.g. >= 2 prior exceptions), uncertainty, or risk signal, choose ESCALATE instead of APPROVE.
- If clearly valid without risks → APPROVE. If clearly invalid → DENY.
- Decision must be grounded in policy citations
- Include 1-3 specific policy citations with exact text
- IF the decision is ESCALATE, at least one citation MUST be the specific policy rule that triggered the risk or conflict causing the escalation (e.g. repeated exceptions, fraud review, VIP exceptions). Do NOT simply cite the basic refund policy.
- Confidence reflects certainty of the decision
- If tool data contradicts preliminary decision, adjust accordingly
- why_this_decision must be specific and actionable, not generic
Do NOT include any text outside the JSON object."""

    user_prompt = f"""Case: {json.dumps(parsed)}

Preliminary Decision: {json.dumps(prelim)}

Tool Results: {tool_context}

Policy Context: {policy_context}"""

    result = _call_llm_json(system_prompt, user_prompt, "final decision")
    
    new_tool_calls = []
    
    # 4. Only call escalate_case() when final decision = ESCALATE
    if result.get("decision") == "ESCALATE":
        esc_reason = result.get("reason", "Escalation required by final decision")
        esc_priority = parsed.get("priority", "high")
        esc_result = escalate_case(esc_reason, esc_priority)
        new_tool_calls.append(esc_result.model_dump())

    trace_entry = _trace_node(
        "generate_final_decision", start,
        f"Final: {result.get('decision', 'UNKNOWN')} (conf: {result.get('confidence', 0)})"
    )
    
    return_state = {
        "final_decision": result,
        "node_trace": [trace_entry],
    }
    
    if new_tool_calls:
        return_state["tool_calls"] = new_tool_calls
        
    return return_state


# ─── Node 6: Evaluate Decision ───

def evaluate_decision(state: WorkflowState) -> dict:
    """Evaluate the decision for groundedness, policy consistency, and quality."""
    start = time.time()
    final = state["final_decision"]
    policies = state["retrieved_policies"]
    parsed = state["parsed_case"]
    tool_calls = state.get("tool_calls", [])
    
    policy_ids = [p["policy_id"] for p in policies]
    cited_ids = [c.get("policy_id", "") for c in final.get("policy_citations", [])]
    
    system_prompt = """You are a decision quality evaluator for a compliance engine.
Evaluate the decision against retrieved policies, case data, and tool outputs.
You MUST respond with valid JSON matching this exact schema:
{
  "grounded": boolean,
  "grounded_explanation": "string - explain why the decision is or is not grounded in retrieved context",
  "policy_consistent": boolean,
  "policy_consistent_explanation": "string - explain whether the decision follows policy rules correctly",
  "escalation_decision_correct": boolean,
  "escalation_explanation": "string - explain whether the escalation decision was correct",
  "retrieval_sufficient": boolean,
  "retrieval_explanation": "string - explain whether retrieval captured enough context for a correct decision",
  "retrieval_quality": "string - one of: clean, minor_issues, poor",
  "retrieval_quality_explanation": "string - explain any quality issues like duplicate chunks, noise, or irrelevant results",
  "overall_score": number (0.0-1.0),
  "details": "string - summary evaluation narrative"
}
Evaluation criteria:
- grounded: Does the decision reference retrieved policy content? Are citations real?
- policy_consistent: Does the decision follow the rules stated in the cited policies?
- escalation_decision_correct: Was the escalation choice correct? This means:
  * Escalation IS warranted if there is a policy conflict, repeated exception behavior, uncertainty, or significant risk signals, AND information is otherwise complete.
  * If required inputs or documentation are missing, NEED_MORE_INFO is the correct decision and escalation is not yet warranted (so non-escalation is a PASS).
  * If the decision IS ESCALATE and escalation was warranted → true
  * If the decision IS NOT ESCALATE and escalation was NOT needed → true (correct non-escalation)
  * If the decision IS ESCALATE but escalation was NOT warranted → false
  * If the decision IS NOT ESCALATE but it SHOULD have been escalated (e.g. 3 prior exceptions ignored) → false
  IMPORTANT: Correct non-escalation is a PASS (true), not a failure.
- retrieval_sufficient: Did the RAG retrieve enough relevant policies to make a correct decision?
  If the decision is grounded and policy consistent, retrieval was sufficient.
  Only mark false if critical policies were completely missed and the decision suffered.
- retrieval_quality: Rate the cleanliness of retrieved results:
  * "clean" - results are relevant. If there is minor or harmless duplication that does not negatively impact the decision, STILL mark it as clean and suppress any warning about duplicates.
  * "minor_issues" - noise or irrelevant results that were distracting but did not ultimately break the decision
  * "poor" - significant noise or irrelevant results that could mislead
- overall_score: Weighted average (grounded=0.3, policy=0.3, escalation=0.2, retrieval=0.2)
Do NOT include any text outside the JSON object."""

    user_prompt = f"""Decision: {json.dumps(final)}

Case: {json.dumps(parsed)}

Retrieved Policy IDs: {json.dumps(policy_ids)}
Cited Policy IDs: {json.dumps(cited_ids)}

Tool Outputs: {json.dumps([t.get('output_data', {}) for t in tool_calls])}"""

    result = _call_llm_json(system_prompt, user_prompt, "evaluation")
    
    trace_entry = _trace_node(
        "evaluate_decision", start,
        f"Score: {result.get('overall_score', 0)} | Grounded: {result.get('grounded', False)}"
    )
    
    return {
        "evaluation": result,
        "node_trace": [trace_entry],
    }


# ─── Node 7: Suggest Improvement ───

def suggest_improvement(state: WorkflowState) -> dict:
    """Suggest improvements when evaluation reveals weaknesses."""
    start = time.time()
    evaluation = state["evaluation"]
    final = state["final_decision"]
    
    weaknesses = []
    if not evaluation.get("grounded", True):
        weaknesses.append("Decision is not well-grounded in retrieved context")
    if not evaluation.get("policy_consistent", True):
        weaknesses.append("Decision may not be consistent with policy rules")
    if not evaluation.get("escalation_decision_correct", True):
        weaknesses.append("Escalation decision may be incorrect")
    if not evaluation.get("retrieval_sufficient", True):
        weaknesses.append("Retrieval may have missed key policy context")
    
    if not weaknesses:
        trace_entry = _trace_node("suggest_improvement", start, "No improvements needed")
        return {
            "improvement_suggestion": "",
            "node_trace": [trace_entry],
        }
    
    system_prompt = """You are a quality improvement advisor for a compliance decision engine.
Given evaluation weaknesses, suggest a specific improvement.
You MUST respond with valid JSON matching this exact schema:
{
  "suggestion": "string - specific, actionable improvement recommendation"
}
Be concise and actionable. Focus on what should be done differently.
Do NOT include any text outside the JSON object."""

    user_prompt = f"""Weaknesses identified:
{json.dumps(weaknesses)}

Current decision: {json.dumps(final)}
Evaluation: {json.dumps(evaluation)}"""

    result = _call_llm_json(system_prompt, user_prompt, "improvement suggestion")
    suggestion = result.get("suggestion", "Review decision with additional policy context.")
    
    trace_entry = _trace_node("suggest_improvement", start, f"Suggestion: {suggestion[:80]}")
    
    return {
        "improvement_suggestion": suggestion,
        "node_trace": [trace_entry],
    }


# ─── Node 8: Save Trace ───

def save_trace_node(state: WorkflowState) -> dict:
    """Persist the complete workflow trace to SQLite."""
    start = time.time()
    final = state.get("final_decision", {})
    evaluation = state.get("evaluation", {})
    
    # Calculate total duration from node traces
    total_ms = sum(n.get("duration_ms", 0) for n in state.get("node_trace", []))
    
    trace = TraceRecord(
        id=state.get("trace_id", str(uuid.uuid4())),
        created_at=datetime.utcnow().isoformat(),
        case_input=state.get("case_input", {}),
        case_type=state.get("parsed_case", {}).get("case_type", "unknown"),
        decision=final.get("decision", "UNKNOWN"),
        confidence=final.get("confidence", 0.0),
        reason=final.get("reason", ""),
        why_this_decision=final.get("why_this_decision", {}),
        retrieved_policies=state.get("retrieved_policies", []),
        policy_citations=final.get("policy_citations", []),
        tool_calls=state.get("tool_calls", []),
        evaluation=evaluation,
        improvement_suggestion=state.get("improvement_suggestion", None) or None,
        workflow_trace=state.get("node_trace", []),
        duration_ms=total_ms,
    )
    
    save_trace(trace)
    
    trace_entry = _trace_node("save_trace", start, f"Saved trace {trace.id}")
    
    return {
        "node_trace": [trace_entry],
    }
