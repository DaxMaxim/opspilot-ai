"""LangGraph StateGraph definition for the decision workflow."""
from langgraph.graph import StateGraph, START, END
from workflow.state import WorkflowState
from workflow.nodes import (
    parse_case,
    retrieve_policy,
    decide_action,
    call_tool_if_needed,
    generate_final_decision,
    evaluate_decision,
    suggest_improvement,
    save_trace_node,
)


def should_call_tools(state: WorkflowState) -> str:
    """Conditional edge: route to tool calling or skip to final decision."""
    if state.get("tool_needed", True):
        return "call_tool"
    return "generate_final"


def should_suggest_improvement(state: WorkflowState) -> str:
    """Conditional edge: suggest improvement if evaluation is weak."""
    evaluation = state.get("evaluation", {})
    score = evaluation.get("overall_score", 1.0)
    
    # Trigger improvement if any criterion fails or score is below 0.7
    if score < 0.7:
        return "suggest"
    if not evaluation.get("grounded", True):
        return "suggest"
    if not evaluation.get("policy_consistent", True):
        return "suggest"
    if not evaluation.get("retrieval_sufficient", True):
        return "suggest"
    
    return "skip"


def build_workflow() -> StateGraph:
    """Build and compile the LangGraph decision workflow.
    
    Graph:
        START → parse_case → retrieve_policy → decide_action
            → [tool_needed?] → call_tool → generate_final_decision
            → [!tool_needed?] → generate_final_decision
        generate_final_decision → evaluate_decision
            → [weak?] → suggest_improvement → save_trace → END
            → [strong?] → save_trace → END
    """
    graph = StateGraph(WorkflowState)
    
    # Add all nodes
    graph.add_node("parse_case", parse_case)
    graph.add_node("retrieve_policy", retrieve_policy)
    graph.add_node("decide_action", decide_action)
    graph.add_node("call_tool", call_tool_if_needed)
    graph.add_node("generate_final_decision", generate_final_decision)
    graph.add_node("evaluate_decision", evaluate_decision)
    graph.add_node("suggest_improvement", suggest_improvement)
    graph.add_node("save_trace", save_trace_node)
    
    # Linear edges
    graph.add_edge(START, "parse_case")
    graph.add_edge("parse_case", "retrieve_policy")
    graph.add_edge("retrieve_policy", "decide_action")
    
    # Conditional: tool calling
    graph.add_conditional_edges(
        "decide_action",
        should_call_tools,
        {
            "call_tool": "call_tool",
            "generate_final": "generate_final_decision",
        },
    )
    graph.add_edge("call_tool", "generate_final_decision")
    
    # After final decision → evaluate
    graph.add_edge("generate_final_decision", "evaluate_decision")
    
    # Conditional: improvement suggestion
    graph.add_conditional_edges(
        "evaluate_decision",
        should_suggest_improvement,
        {
            "suggest": "suggest_improvement",
            "skip": "save_trace",
        },
    )
    graph.add_edge("suggest_improvement", "save_trace")
    
    # Terminal
    graph.add_edge("save_trace", END)
    
    return graph.compile()


# Pre-compiled workflow instance
workflow = build_workflow()
