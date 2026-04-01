"""Pydantic models for case input."""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class CaseInput(BaseModel):
    """Structured case input for the decision engine."""
    case_type: Literal[
        "refund_request",
        "claim_review",
        "exception_request",
        "fraud_investigation",
        "escalation",
    ] = Field(description="Type of operational case")
    customer_id: str = Field(description="Unique customer/user identifier")
    amount: float = Field(description="Transaction amount in USD", ge=0)
    purchase_date: str = Field(description="Date of original purchase (YYYY-MM-DD)")
    request_date: str = Field(description="Date of this request (YYYY-MM-DD)")
    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Case priority level"
    )
    description: str = Field(description="Brief case description")
