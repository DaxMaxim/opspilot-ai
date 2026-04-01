"""Mock operational tools for the decision engine.

These tools simulate realistic external service calls without
requiring actual infrastructure. Logic is deterministic based
on case inputs to ensure reproducible demo behavior.
"""
import random
import time
from datetime import datetime, timedelta
from models.decision import ToolCallResult


def check_eligibility(case_data: dict) -> ToolCallResult:
    """Check refund/claim eligibility based on case attributes.
    
    Returns eligibility status, triggered rules, refund window status,
    and exception eligibility.
    """
    start = time.time()
    
    # Parse dates
    purchase_date = datetime.strptime(case_data.get("purchase_date", "2024-01-01"), "%Y-%m-%d")
    request_date = datetime.strptime(case_data.get("request_date", "2024-02-01"), "%Y-%m-%d")
    days_since_purchase = (request_date - purchase_date).days
    amount = case_data.get("amount", 0)
    
    # Determine refund window status
    if days_since_purchase <= 30:
        window_status = "within_standard_window"
        eligible = True
        rule_triggered = "POL-001: Within standard 30-day refund window — full refund eligible for unused items"
    elif days_since_purchase <= 60:
        window_status = "within_extended_window"
        eligible = case_data.get("case_type") in ["claim_review", "exception_request"]
        rule_triggered = "POL-002: Extended window (damaged goods) or POL-011: Partial refund"
    else:
        window_status = "outside_all_windows"
        eligible = False
        rule_triggered = "POL-001: Outside standard refund window"
    
    # Check high-value constraint
    if amount >= 500:
        rule_triggered += " | POL-008: High-value transaction review required"
    
    # Exception eligibility based on case type
    exception_eligible = case_data.get("case_type") in ["exception_request", "escalation"]
    
    output = {
        "eligible": eligible,
        "rule_triggered": rule_triggered,
        "refund_window_status": window_status,
        "days_since_purchase": days_since_purchase,
        "exception_eligible": exception_eligible,
        "amount_tier": "high_value" if amount >= 500 else "standard",
    }
    
    elapsed = int((time.time() - start) * 1000) + random.randint(15, 45)
    
    return ToolCallResult(
        tool_name="check_eligibility",
        input_data={"customer_id": case_data.get("customer_id"), "amount": amount},
        output_data=output,
        execution_time_ms=elapsed,
    )


def fetch_case_history(user_id: str) -> ToolCallResult:
    """Fetch customer's case history for pattern analysis.
    
    Returns prior refund requests, suspicious pattern flags,
    customer tier, and prior exception approvals.
    """
    start = time.time()
    
    # Deterministic mock data based on user_id hash
    seed = sum(ord(c) for c in user_id) % 100
    
    if seed < 20:
        # Clean customer
        history = {
            "prior_refund_requests": 0,
            "suspicious_pattern_flag": False,
            "customer_tier": "standard",
            "prior_exception_approvals": 0,
            "account_age_days": 365 + seed * 10,
            "total_lifetime_spend": 500 + seed * 50,
        }
    elif seed < 50:
        # Moderate customer with some history
        history = {
            "prior_refund_requests": 1 + seed % 3,
            "suspicious_pattern_flag": False,
            "customer_tier": "gold" if seed > 35 else "standard",
            "prior_exception_approvals": seed % 2,
            "account_age_days": 180 + seed * 5,
            "total_lifetime_spend": 1000 + seed * 100,
        }
    elif seed < 75:
        # VIP customer
        history = {
            "prior_refund_requests": seed % 4,
            "suspicious_pattern_flag": False,
            "customer_tier": "platinum" if seed > 60 else "gold",
            "prior_exception_approvals": 1 + seed % 3,
            "account_age_days": 730 + seed * 10,
            "total_lifetime_spend": 5000 + seed * 200,
        }
    else:
        # Suspicious customer
        history = {
            "prior_refund_requests": 3 + seed % 5,
            "suspicious_pattern_flag": True,
            "customer_tier": "standard",
            "prior_exception_approvals": 2 + seed % 3,
            "account_age_days": 45 + seed % 30,
            "total_lifetime_spend": 200 + seed * 10,
        }
    
    elapsed = int((time.time() - start) * 1000) + random.randint(20, 60)
    
    return ToolCallResult(
        tool_name="fetch_case_history",
        input_data={"user_id": user_id},
        output_data=history,
        execution_time_ms=elapsed,
    )


def escalate_case(reason: str, priority: str) -> ToolCallResult:
    """Escalate a case to the appropriate review queue.
    
    Returns escalation ID, assigned queue, SLA, and priority.
    """
    start = time.time()
    
    queue_map = {
        "low": ("General Review", "72 hours", "Senior Agent"),
        "medium": ("Priority Review", "48 hours", "Team Lead"),
        "high": ("Urgent Review", "24 hours", "Manager"),
        "critical": ("Executive Review", "4 hours", "Director"),
    }
    
    queue_name, sla, handler = queue_map.get(priority, queue_map["medium"])
    escalation_id = f"ESC-{random.randint(10000, 99999)}"
    
    output = {
        "escalation_id": escalation_id,
        "queue": queue_name,
        "sla": sla,
        "priority": priority,
        "assigned_handler": handler,
        "status": "queued",
        "reason": reason,
    }
    
    elapsed = int((time.time() - start) * 1000) + random.randint(10, 30)
    
    return ToolCallResult(
        tool_name="escalate_case",
        input_data={"reason": reason, "priority": priority},
        output_data=output,
        execution_time_ms=elapsed,
    )
