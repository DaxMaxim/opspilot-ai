"""Seed script — initializes vector store and creates sample trace records."""
import json
import uuid
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import init_db
from db.operations import save_trace
from rag.vectorstore import seed_vector_store
from models.trace import TraceRecord


def create_sample_traces():
    """Create realistic sample trace records for the demo."""
    
    samples = [
        {
            "case_input": {
                "case_type": "refund_request",
                "customer_id": "CUST-1042",
                "amount": 49.99,
                "purchase_date": "2026-03-10",
                "request_date": "2026-03-25",
                "priority": "low",
                "description": "Customer requests refund on unused product within 30-day window"
            },
            "decision": "APPROVE",
            "confidence": 0.94,
            "reason": "Request is within the standard 30-day refund window. Product is unused and unopened, customer has valid proof of purchase, and no prior refund for this transaction. All eligibility conditions under POL-001 are met. Full refund issued per POL-001 Section 3 — unused item within 30-day window.",
            "why_this_decision": {
                "policy_clause_used": "POL-001 Section 3: Full refund for unused/unopened items within 30-day window",
                "key_condition_matched": "Request submitted within 30-day window (15 days since purchase), product unused",
                "key_constraint_triggered": "POL-001 Section 1: Standard Refund Window — within 30 calendar days"
            },
            "evaluation": {
                "grounded": True,
                "grounded_explanation": "Decision directly references POL-001 eligibility conditions which are present in retrieved context.",
                "policy_consistent": True,
                "policy_consistent_explanation": "Decision correctly applies the standard refund policy rules. All four conditions are verified.",
                "escalation_decision_correct": True,
                "escalation_explanation": "No escalation needed for a straightforward within-window refund request.",
                "retrieval_sufficient": True,
                "retrieval_explanation": "Standard refund policy was retrieved with high relevance. No key context was missed.",
                "retrieval_quality": "clean",
                "retrieval_quality_explanation": "Retrieved chunks are relevant and non-redundant.",
                "overall_score": 0.95,
                "details": "High-quality decision with strong grounding, policy consistency, and appropriate action."
            },
            "policy_citations": [
                {"policy_id": "POL-001", "policy_name": "Standard Refund Policy", "section": "Section 2: Eligibility Conditions", "relevant_text": "A refund is eligible if ALL conditions are met: within 30-day window, not fully consumed, valid proof of purchase, no prior refund for same transaction."},
                {"policy_id": "POL-001", "policy_name": "Standard Refund Policy", "section": "Section 3: Refund Amounts", "relevant_text": "Full refund: Issued when the product/service is returned unused or unopened within the 30-day refund window."}
            ],
            "tool_calls": [
                {"tool_name": "check_eligibility", "input_data": {"customer_id": "CUST-1042", "amount": 49.99}, "output_data": {"eligible": True, "rule_triggered": "POL-001: Within standard 30-day refund window — full refund eligible for unused items", "refund_window_status": "within_standard_window", "days_since_purchase": 15, "exception_eligible": False, "amount_tier": "standard"}, "execution_time_ms": 32},
                {"tool_name": "fetch_case_history", "input_data": {"user_id": "CUST-1042"}, "output_data": {"prior_refund_requests": 0, "suspicious_pattern_flag": False, "customer_tier": "standard", "prior_exception_approvals": 0, "account_age_days": 480, "total_lifetime_spend": 750}, "execution_time_ms": 28}
            ],
            "improvement_suggestion": None,
            "duration_ms": 2340,
        },
        {
            "case_input": {
                "case_type": "exception_request",
                "customer_id": "CUST-7721",
                "amount": 299.00,
                "purchase_date": "2026-02-01",
                "request_date": "2026-03-20",
                "priority": "high",
                "description": "VIP Platinum customer requesting refund 47 days after purchase. Third exception this year."
            },
            "decision": "ESCALATE",
            "confidence": 0.78,
            "reason": "While the customer holds Platinum VIP status (60-day extended window applies), this is their 3rd exception request this year which exceeds the standard limit of 2. POL-005 mandates senior review for 3rd exceptions, and the combination of VIP status with exception limit breach requires manager-level decision.",
            "why_this_decision": {
                "policy_clause_used": "POL-005 Section 2: Third Exception Request — automatic senior review required",
                "key_condition_matched": "3rd exception request within 12-month rolling period exceeds standard limit",
                "key_constraint_triggered": "POL-005 Section 4: VIP customer exceeded exception limit — escalate to management"
            },
            "evaluation": {
                "grounded": True,
                "grounded_explanation": "Decision references both VIP policy (POL-004) and repeated exceptions policy (POL-005) which were retrieved.",
                "policy_consistent": True,
                "policy_consistent_explanation": "Correctly identifies conflict between VIP extended window and exception limit. Escalation is the appropriate path per POL-005 Section 4.",
                "escalation_decision_correct": True,
                "escalation_explanation": "Escalation is warranted: VIP customer with exceeded exception limit creates a policy conflict that requires manager judgment.",
                "retrieval_sufficient": True,
                "retrieval_explanation": "Both VIP policy and repeated exceptions policy were retrieved. Escalation criteria also retrieved.",
                "retrieval_quality": "clean",
                "retrieval_quality_explanation": "All relevant policies retrieved without duplication.",
                "overall_score": 0.88,
                "details": "Strong decision with appropriate escalation. Policy conflict correctly identified and handled."
            },
            "policy_citations": [
                {"policy_id": "POL-005", "policy_name": "Repeated Exceptions Policy", "section": "Section 2: Third Exception Request", "relevant_text": "When a customer submits a third exception request within 12 months: the request is automatically flagged for senior review."},
                {"policy_id": "POL-004", "policy_name": "VIP Customer Policy", "section": "Section 3: Refund Window Extensions", "relevant_text": "Platinum: Extended refund window (60 days), dedicated rep, exception consideration."},
                {"policy_id": "POL-007", "policy_name": "Escalation Criteria", "section": "Section 1: Automatic Escalation Triggers", "relevant_text": "Cases must be escalated when: Customer is VIP tier, or standard policy does not clearly cover the situation."}
            ],
            "tool_calls": [
                {"tool_name": "check_eligibility", "input_data": {"customer_id": "CUST-7721", "amount": 299.0}, "output_data": {"eligible": True, "rule_triggered": "POL-002: Extended window (damaged goods) or POL-011: Partial refund", "refund_window_status": "within_extended_window", "days_since_purchase": 47, "exception_eligible": True, "amount_tier": "standard"}, "execution_time_ms": 38},
                {"tool_name": "fetch_case_history", "input_data": {"user_id": "CUST-7721"}, "output_data": {"prior_refund_requests": 3, "suspicious_pattern_flag": False, "customer_tier": "platinum", "prior_exception_approvals": 2, "account_age_days": 1100, "total_lifetime_spend": 12500}, "execution_time_ms": 45},
                {"tool_name": "escalate_case", "input_data": {"reason": "VIP customer exceeded exception limit — requires manager decision", "priority": "high"}, "output_data": {"escalation_id": "ESC-34521", "queue": "Urgent Review", "sla": "24 hours", "priority": "high", "assigned_handler": "Manager", "status": "queued"}, "execution_time_ms": 22}
            ],
            "improvement_suggestion": None,
            "duration_ms": 4120,
        },
        {
            "case_input": {
                "case_type": "refund_request",
                "customer_id": "CUST-9381",
                "amount": 89.50,
                "purchase_date": "2025-12-15",
                "request_date": "2026-03-22",
                "priority": "medium",
                "description": "Customer's 4th refund request this year. Pattern of purchasing and returning within 30 days. Requesting refund citing dissatisfaction."
            },
            "decision": "DENY",
            "confidence": 0.87,
            "reason": "The request is outside the 30-day refund window (97 days since purchase). Additionally, the customer has submitted 4 refund requests this year, triggering suspicious activity flags under POL-009 and exceeding the exception limit under POL-005. The pattern of repeated purchases and returns indicates potential policy abuse.",
            "why_this_decision": {
                "policy_clause_used": "POL-001 Section 1: Outside 30-day window AND POL-005 Section 3: Gaming pattern detected",
                "key_condition_matched": "97 days since purchase — outside all standard and extended refund windows",
                "key_constraint_triggered": "POL-009: 4 refund requests in 12 months exceeds velocity threshold (5+ in 12 months)"
            },
            "evaluation": {
                "grounded": True,
                "grounded_explanation": "Decision cites POL-001 window rules, POL-005 exception limits, and POL-009 velocity triggers — all present in retrieved context.",
                "policy_consistent": True,
                "policy_consistent_explanation": "Denial is correct: outside refund window, exception limit exceeded, and suspicious pattern identified.",
                "escalation_decision_correct": True,
                "escalation_explanation": "Direct denial is appropriate rather than escalation since the case is clear-cut with multiple policy violations.",
                "retrieval_sufficient": False,
                "retrieval_explanation": "Fraud review policy (POL-003) was not retrieved but may be relevant given the suspicious pattern flag.",
                "retrieval_quality": "minor_issues",
                "retrieval_quality_explanation": "Retrieval focused on refund policies but missed fraud-specific criteria that would strengthen the decision.",
                "overall_score": 0.82,
                "details": "Solid decision but retrieval could have included fraud review policy for more comprehensive analysis."
            },
            "policy_citations": [
                {"policy_id": "POL-001", "policy_name": "Standard Refund Policy", "section": "Section 1: Standard Refund Window", "relevant_text": "Requests submitted after this window are automatically ineligible for standard processing."},
                {"policy_id": "POL-005", "policy_name": "Repeated Exceptions Policy", "section": "Section 3: Pattern Assessment", "relevant_text": "Gaming pattern: Repeated similar requests exploiting policy gaps → deny and flag."}
            ],
            "tool_calls": [
                {"tool_name": "check_eligibility", "input_data": {"customer_id": "CUST-9381", "amount": 89.5}, "output_data": {"eligible": False, "rule_triggered": "POL-001: Outside standard refund window", "refund_window_status": "outside_all_windows", "days_since_purchase": 97, "exception_eligible": False, "amount_tier": "standard"}, "execution_time_ms": 29},
                {"tool_name": "fetch_case_history", "input_data": {"user_id": "CUST-9381"}, "output_data": {"prior_refund_requests": 4, "suspicious_pattern_flag": True, "customer_tier": "standard", "prior_exception_approvals": 2, "account_age_days": 210, "total_lifetime_spend": 450}, "execution_time_ms": 41}
            ],
            "improvement_suggestion": "Consider retrieving POL-003 (Fraud Review Rules) for cases flagged with suspicious patterns. The current retrieval focused on refund and exception policies but missed fraud-specific criteria.",
            "duration_ms": 3680,
        },
        {
            "case_input": {
                "case_type": "claim_review",
                "customer_id": "CUST-5564",
                "amount": 650.00,
                "purchase_date": "2026-03-01",
                "request_date": "2026-03-28",
                "priority": "high",
                "description": "Customer claims product arrived damaged. Missing photos of damage. High-value item ($650). Requesting full refund."
            },
            "decision": "NEED_MORE_INFO",
            "confidence": 0.91,
            "reason": "While the claim is within the refund window and damaged goods exception applies (POL-002), mandatory documentation is missing. Photographic evidence of damage is required per POL-006. Additionally, as a high-value transaction ($650), enhanced verification is required per POL-008. The customer must provide damage photos and undergo identity verification before the claim can proceed.",
            "why_this_decision": {
                "policy_clause_used": "POL-006 Section 2: NEED_MORE_INFO Protocol — documentation missing triggers hold",
                "key_condition_matched": "Photographic evidence of damage is mandatory but not provided",
                "key_constraint_triggered": "POL-008: High-value transaction ($650 > $500 threshold) requires complete documentation with no exceptions"
            },
            "evaluation": {
                "grounded": True,
                "grounded_explanation": "Decision correctly references POL-006 documentation requirements and POL-008 high-value thresholds from retrieved policies.",
                "policy_consistent": True,
                "policy_consistent_explanation": "NEED_MORE_INFO is the correct status per POL-006 when mandatory documentation is missing.",
                "escalation_decision_correct": True,
                "escalation_explanation": "Not escalating is appropriate — the case needs documentation first before any decision can be made.",
                "retrieval_sufficient": True,
                "retrieval_explanation": "Damaged goods, missing documentation, and high-value transaction policies all retrieved successfully.",
                "retrieval_quality": "clean",
                "retrieval_quality_explanation": "All relevant policies retrieved with good coverage and no noise.",
                "overall_score": 0.93,
                "details": "Excellent decision quality. Correctly identifies documentation gap and high-value constraints."
            },
            "policy_citations": [
                {"policy_id": "POL-006", "policy_name": "Missing Documentation Policy", "section": "Section 2: NEED_MORE_INFO Protocol", "relevant_text": "When documentation is missing or incomplete: Decision status is set to NEED_MORE_INFO. Specify exactly which documents are missing."},
                {"policy_id": "POL-002", "policy_name": "Damaged Goods Exception", "section": "Section 3: Required Documentation", "relevant_text": "Photographic evidence of the damage (minimum 2 photos), Original order confirmation, Description of damage. Missing documentation will result in NEED_MORE_INFO status."},
                {"policy_id": "POL-008", "policy_name": "High-Value Transaction Policy", "section": "Section 2: Mandatory Requirements", "relevant_text": "All refund requests for high-value transactions require: Complete documentation with no exceptions."}
            ],
            "tool_calls": [
                {"tool_name": "check_eligibility", "input_data": {"customer_id": "CUST-5564", "amount": 650.0}, "output_data": {"eligible": True, "rule_triggered": "POL-001: Within standard 30-day refund window — full refund eligible for unused items | POL-008: High-value transaction review required", "refund_window_status": "within_standard_window", "days_since_purchase": 27, "exception_eligible": False, "amount_tier": "high_value"}, "execution_time_ms": 35},
                {"tool_name": "fetch_case_history", "input_data": {"user_id": "CUST-5564"}, "output_data": {"prior_refund_requests": 0, "suspicious_pattern_flag": False, "customer_tier": "gold", "prior_exception_approvals": 0, "account_age_days": 820, "total_lifetime_spend": 3200}, "execution_time_ms": 33}
            ],
            "improvement_suggestion": None,
            "duration_ms": 3150,
        },
        {
            "case_input": {
                "case_type": "fraud_investigation",
                "customer_id": "CUST-2210",
                "amount": 1200.00,
                "purchase_date": "2026-03-15",
                "request_date": "2026-03-27",
                "priority": "critical",
                "description": "Account created 20 days ago. Third refund request this month. Different shipping and billing addresses. Total requests exceed $2,000."
            },
            "decision": "DENY",
            "confidence": 0.92,
            "reason": "Multiple fraud indicators triggered: new account (<30 days), 3 refund requests in 7 days exceeding velocity thresholds, differing shipping/billing addresses, and high cumulative refund amount. Per POL-003 auto-deny criteria, the account matches known fraud patterns. Case placed on auto-hold per POL-009.",
            "why_this_decision": {
                "policy_clause_used": "POL-003 Section 3: Auto-Deny Criteria — transaction patterns match known fraud signatures",
                "key_condition_matched": "3 fraud indicators simultaneously triggered: new account, high velocity, address mismatch",
                "key_constraint_triggered": "POL-009 Section 1: 3+ refund requests in 7 days triggers automatic review"
            },
            "evaluation": {
                "grounded": True,
                "grounded_explanation": "Decision references specific fraud triggers from POL-003 and POL-009 that match the case attributes.",
                "policy_consistent": True,
                "policy_consistent_explanation": "Auto-deny is correct when multiple fraud signatures are detected per POL-003 Section 3.",
                "escalation_decision_correct": True,
                "escalation_explanation": "Direct denial is appropriate for confirmed fraud patterns rather than escalation which would delay action.",
                "retrieval_sufficient": True,
                "retrieval_explanation": "Fraud review rules and suspicious activity triggers were both retrieved successfully.",
                "retrieval_quality": "clean",
                "retrieval_quality_explanation": "Fraud-related policies retrieved accurately without noise.",
                "overall_score": 0.94,
                "details": "High-confidence denial with strong multi-signal fraud detection grounded in policy."
            },
            "policy_citations": [
                {"policy_id": "POL-003", "policy_name": "Fraud Review Rules", "section": "Section 1: Automatic Fraud Review Triggers", "relevant_text": "3+ refund requests within 90-day period, customer account less than 30 days old, shipping address differs from billing address."},
                {"policy_id": "POL-009", "policy_name": "Suspicious Activity Triggers", "section": "Section 1: Velocity-Based Triggers", "relevant_text": "3+ refund requests in 7 days triggers automatic review."},
                {"policy_id": "POL-003", "policy_name": "Fraud Review Rules", "section": "Section 3: Auto-Deny Criteria", "relevant_text": "Transaction patterns match known fraud signatures."}
            ],
            "tool_calls": [
                {"tool_name": "check_eligibility", "input_data": {"customer_id": "CUST-2210", "amount": 1200.0}, "output_data": {"eligible": False, "rule_triggered": "POL-001: Within standard 30-day refund window — full refund eligible for unused items | POL-008: High-value transaction review required", "refund_window_status": "within_standard_window", "days_since_purchase": 12, "exception_eligible": False, "amount_tier": "high_value"}, "execution_time_ms": 31},
                {"tool_name": "fetch_case_history", "input_data": {"user_id": "CUST-2210"}, "output_data": {"prior_refund_requests": 3, "suspicious_pattern_flag": True, "customer_tier": "standard", "prior_exception_approvals": 0, "account_age_days": 20, "total_lifetime_spend": 2100}, "execution_time_ms": 44}
            ],
            "improvement_suggestion": None,
            "duration_ms": 2890,
        },
    ]
    
    now = datetime.utcnow()
    
    for i, sample in enumerate(samples):
        trace = TraceRecord(
            id=str(uuid.uuid4()),
            created_at=(now - timedelta(hours=i * 6, minutes=i * 17)).isoformat(),
            case_input=sample["case_input"],
            case_type=sample["case_input"]["case_type"],
            decision=sample["decision"],
            confidence=sample["confidence"],
            reason=sample["reason"],
            why_this_decision=sample["why_this_decision"],
            retrieved_policies=[],  # Simplified for seed data
            policy_citations=sample["policy_citations"],
            tool_calls=sample["tool_calls"],
            evaluation=sample["evaluation"],
            improvement_suggestion=sample.get("improvement_suggestion"),
            workflow_trace=[
                {"node": "parse_case", "timestamp": now.isoformat(), "duration_ms": 120, "output_summary": "Parsed case attributes"},
                {"node": "retrieve_policy", "timestamp": now.isoformat(), "duration_ms": 340, "output_summary": "Retrieved 5 policy chunks"},
                {"node": "decide_action", "timestamp": now.isoformat(), "duration_ms": 890, "output_summary": f"Preliminary: {sample['decision']}"},
                {"node": "call_tool", "timestamp": now.isoformat(), "duration_ms": 85, "output_summary": f"Executed {len(sample['tool_calls'])} tools"},
                {"node": "generate_final_decision", "timestamp": now.isoformat(), "duration_ms": 670, "output_summary": f"Final: {sample['decision']}"},
                {"node": "evaluate_decision", "timestamp": now.isoformat(), "duration_ms": 430, "output_summary": f"Score: {sample['evaluation']['overall_score']}"},
                {"node": "save_trace", "timestamp": now.isoformat(), "duration_ms": 8, "output_summary": "Trace saved"},
            ],
            duration_ms=sample["duration_ms"],
        )
        save_trace(trace)
        print(f"  Created trace: {trace.id} ({trace.decision})")


def main():
    print("=" * 50)
    print("OpsPilot AI — Seed Script")
    print("=" * 50)
    
    print("\n1. Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    
    print("\n2. Seeding vector store with policy documents...")
    count = seed_vector_store()
    print(f"   ✓ {count} policy chunks indexed")
    
    print("\n3. Creating sample trace records...")
    create_sample_traces()
    print("   ✓ Sample traces created")
    
    print("\n" + "=" * 50)
    print("Seeding complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
