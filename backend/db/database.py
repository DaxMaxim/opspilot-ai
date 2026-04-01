"""SQLite database setup and connection."""
import sqlite3
from pathlib import Path
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            case_input TEXT NOT NULL,
            case_type TEXT NOT NULL,
            decision TEXT NOT NULL,
            confidence REAL NOT NULL,
            reason TEXT NOT NULL,
            why_this_decision TEXT NOT NULL DEFAULT '{}',
            retrieved_policies TEXT NOT NULL DEFAULT '[]',
            policy_citations TEXT NOT NULL DEFAULT '[]',
            tool_calls TEXT NOT NULL DEFAULT '[]',
            evaluation TEXT NOT NULL DEFAULT '{}',
            improvement_suggestion TEXT,
            workflow_trace TEXT NOT NULL DEFAULT '[]',
            duration_ms INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
