"""LangGraph workflow state schema."""
from typing import TypedDict, Annotated
import operator


class WorkflowState(TypedDict):
    """Complete state flowing through the LangGraph decision workflow."""
    
    # Input
    case_input: dict
    
    # Parsed structured case attributes
    parsed_case: dict
    
    # Retrieved policy documents from RAG
    retrieved_policies: list[dict]
    
    # Preliminary decision from the decision node
    preliminary_decision: dict
    
    # Tool invocations — uses operator.add reducer to append
    tool_calls: Annotated[list[dict], operator.add]
    tool_needed: bool
    
    # Final structured decision
    final_decision: dict
    
    # Evaluation results
    evaluation: dict
    improvement_suggestion: str
    
    # Node-by-node execution trace — uses operator.add reducer to append
    node_trace: Annotated[list[dict], operator.add]
    
    # Trace identifier
    trace_id: str
