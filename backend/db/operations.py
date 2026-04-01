"""CRUD operations for trace records."""
import json
from db.database import get_connection
from models.trace import TraceRecord, TraceListItem


def save_trace(trace: TraceRecord) -> str:
    """Insert a trace record into SQLite."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO traces 
           (id, created_at, case_input, case_type, decision, confidence, reason,
            why_this_decision, retrieved_policies, policy_citations, tool_calls,
            evaluation, improvement_suggestion, workflow_trace, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            trace.id,
            trace.created_at,
            json.dumps(trace.case_input),
            trace.case_type,
            trace.decision,
            trace.confidence,
            trace.reason,
            json.dumps(trace.why_this_decision),
            json.dumps(trace.retrieved_policies),
            json.dumps(trace.policy_citations),
            json.dumps(trace.tool_calls),
            json.dumps(trace.evaluation),
            trace.improvement_suggestion,
            json.dumps(trace.workflow_trace),
            trace.duration_ms,
        ),
    )
    conn.commit()
    conn.close()
    return trace.id


def get_trace(trace_id: str) -> TraceRecord | None:
    """Retrieve a single trace record by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM traces WHERE id = ?", (trace_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return TraceRecord(
        id=row["id"],
        created_at=row["created_at"],
        case_input=json.loads(row["case_input"]),
        case_type=row["case_type"],
        decision=row["decision"],
        confidence=row["confidence"],
        reason=row["reason"],
        why_this_decision=json.loads(row["why_this_decision"]),
        retrieved_policies=json.loads(row["retrieved_policies"]),
        policy_citations=json.loads(row["policy_citations"]),
        tool_calls=json.loads(row["tool_calls"]),
        evaluation=json.loads(row["evaluation"]),
        improvement_suggestion=row["improvement_suggestion"],
        workflow_trace=json.loads(row["workflow_trace"]),
        duration_ms=row["duration_ms"],
    )


def list_traces(page: int = 1, limit: int = 20) -> tuple[list[TraceListItem], int]:
    """List traces with pagination. Returns (items, total_count)."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
    offset = (page - 1) * limit
    rows = conn.execute(
        "SELECT * FROM traces ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    conn.close()

    items = []
    for row in rows:
        evaluation = json.loads(row["evaluation"])
        items.append(
            TraceListItem(
                id=row["id"],
                created_at=row["created_at"],
                case_type=row["case_type"],
                decision=row["decision"],
                confidence=row["confidence"],
                grounded=evaluation.get("grounded", False),
                policy_consistent=evaluation.get("policy_consistent", False),
                duration_ms=row["duration_ms"],
            )
        )
    return items, total
