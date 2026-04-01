"""Trace model for SQLite storage."""
from pydantic import BaseModel, Field
from typing import Optional


class TraceRecord(BaseModel):
    """A complete trace record stored in SQLite."""
    id: str
    created_at: str
    case_input: dict
    case_type: str
    decision: str
    confidence: float
    reason: str
    why_this_decision: dict
    retrieved_policies: list[dict]
    policy_citations: list[dict]
    tool_calls: list[dict]
    evaluation: dict
    improvement_suggestion: Optional[str] = None
    workflow_trace: list[dict]
    duration_ms: int


class TraceListItem(BaseModel):
    """Summary item for the trace list view."""
    id: str
    created_at: str
    case_type: str
    decision: str
    confidence: float
    grounded: bool
    policy_consistent: bool
    duration_ms: int


class TraceListResponse(BaseModel):
    """Paginated trace list response."""
    traces: list[TraceListItem]
    total: int
    page: int
    limit: int
