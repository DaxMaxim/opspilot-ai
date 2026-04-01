"""Pydantic models for decision output and evaluation."""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class PolicyCitation(BaseModel):
    """A specific policy clause cited in the decision."""
    policy_id: str = Field(description="Policy document ID (e.g. POL-001)")
    policy_name: str = Field(description="Policy name")
    section: str = Field(description="Section or clause reference")
    relevant_text: str = Field(description="The specific policy text cited")


class RetrievedPolicy(BaseModel):
    """A policy chunk retrieved from the vector store."""
    policy_id: str
    policy_name: str
    content: str
    relevance_score: float = Field(ge=0, le=1)


class ToolCallResult(BaseModel):
    """Result from a mock tool invocation."""
    tool_name: str
    input_data: dict
    output_data: dict
    execution_time_ms: int


class EvaluationResult(BaseModel):
    """Structured evaluation of the decision quality."""
    grounded: bool = Field(description="Whether the decision is grounded in retrieved context")
    grounded_explanation: str = Field(description="Why grounded or not")
    policy_consistent: bool = Field(description="Whether the decision aligns with policy rules")
    policy_consistent_explanation: str = Field(description="Why policy consistent or not")
    escalation_decision_correct: bool = Field(description="Whether the escalation decision was correct (escalating when needed, or NOT escalating when not needed)")
    escalation_explanation: str = Field(description="Why the escalation decision was correct or incorrect")
    retrieval_sufficient: bool = Field(description="Whether retrieval captured enough context to make a correct decision")
    retrieval_explanation: str = Field(description="What retrieval captured or missed")
    retrieval_quality: str = Field(default="clean", description="Quality of retrieved results: clean, minor_issues, or poor")
    retrieval_quality_explanation: str = Field(default="", description="Explanation of retrieval quality issues like duplicates or noise")
    overall_score: float = Field(ge=0, le=1, description="Overall quality score 0-1")
    details: str = Field(description="Summary evaluation narrative")


class WhyThisDecision(BaseModel):
    """Structured explanation for 'Why this decision?' UI block."""
    policy_clause_used: str = Field(description="Primary policy clause applied")
    key_condition_matched: str = Field(description="The key condition that drove the decision")
    key_constraint_triggered: str = Field(description="The constraint or rule that was triggered")


class DecisionOutput(BaseModel):
    """Complete structured output from the decision engine."""
    decision: Literal["APPROVE", "DENY", "ESCALATE", "NEED_MORE_INFO"]
    confidence: float = Field(ge=0, le=1)
    reason: str
    why_this_decision: WhyThisDecision
    policy_citations: list[PolicyCitation]
    retrieved_policies: list[RetrievedPolicy]
    tool_calls: list[ToolCallResult]
    evaluation: EvaluationResult
    improvement_suggestion: Optional[str] = None
    trace_id: str
