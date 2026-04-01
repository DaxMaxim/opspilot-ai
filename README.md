# OpsPilot AI

**AI Decision Engine for Compliance-Critical Operational Workflows**

OpsPilot AI is a policy-grounded decision engine that processes structured operational cases through an agentic RAG pipeline, evaluates decisions for groundedness and policy consistency, and stores full execution traces for observability.

> **This is not a chatbot.** It is AI decision infrastructure for compliance operations.

---

## Architecture

```
┌──────────────────────────┐     ┌──────────────────────────────────────┐
│   Next.js Frontend       │────▶│   FastAPI Backend                    │
│   (Port 3000)            │     │   (Port 8000)                        │
│                          │     │                                      │
│   • Landing Page         │     │   ┌──────────────────────────────┐   │
│   • Case Review          │     │   │  LangGraph Workflow Engine   │   │
│   • Decision Result      │     │   │  8-node decision pipeline    │   │
│   • Trace History        │     │   │                              │   │
│   • Trace Detail         │     │   │  parse → retrieve → decide   │   │
│                          │     │   │  → tools → final → evaluate  │   │
└──────────────────────────┘     │   │  → improve → save_trace      │   │
                                 │   └──────────┬──────┬────────────┘   │
                                 │              │      │                │
                                 │   ┌──────────▼┐  ┌──▼───────────┐   │
                                 │   │ ChromaDB  │  │ SQLite       │   │
                                 │   │ (Vectors) │  │ (Traces)     │   │
                                 │   └───────────┘  └──────────────┘   │
                                 └──────────────────────────────────────┘
```

## Key Capabilities

| Capability | Implementation |
|-----------|---------------|
| **RAG Retrieval** | ChromaDB vector store with 73 policy chunks from 12 policy documents |
| **Agentic Orchestration** | LangGraph StateGraph with 8 nodes and conditional edges |
| **Tool Calling** | 3 mock tools: `check_eligibility`, `fetch_case_history`, `escalate_case` |
| **Structured Outputs** | Strict JSON schema enforcement on all LLM calls with retry logic |
| **Policy Grounding** | Decisions cite specific policy clauses from retrieved documents |
| **Evaluation Layer** | 4-axis evaluation: groundedness, policy consistency, escalation, retrieval |
| **Trace Observability** | Full node-by-node execution traces stored in SQLite |
| **"Why This Decision?"** | Explicit display of policy clause used, key condition, and constraint triggered |

## Tech Stack

- **Frontend**: Next.js 16 (App Router, TypeScript)
- **Backend**: Python FastAPI
- **Workflow Engine**: LangGraph (StateGraph)
- **Vector Store**: ChromaDB (PersistentClient)
- **LLM**: OpenAI gpt-4o-mini (structured JSON output mode)
- **Embeddings**: ChromaDB built-in (all-MiniLM-L6-v2)
- **Trace Storage**: SQLite
- **Styling**: Vanilla CSS (custom dark theme design system)

## Quick Start

### Prerequisites
- Node.js ≥ 20
- Python ≥ 3.10
- OpenAI API key

### 1. Clone and configure

```bash
cd opspilot-ai
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Seed the database and vector store

```bash
# From project root
source backend/venv/bin/activate
python -m backend.seed
```

This creates:
- 73 policy chunks in ChromaDB from 12 policy documents
- 5 sample trace records for demo

### 4. Start the backend

```bash
source backend/venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

### 6. Open the app

Visit **http://localhost:3000**

---

## LangGraph Workflow

The decision pipeline has 8 nodes with conditional branching:

```
START → parse_case → retrieve_policy → decide_action
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                     call_tool_if_needed     generate_final_decision
                              │                       ▲
                              └───────────────────────┘
                                          │
                                  evaluate_decision
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                     suggest_improvement          save_trace
                              │                       ▲
                              └───────────────────────┘
                                                      │
                                                     END
```

### Nodes

| Node | Purpose |
|------|---------|
| `parse_case` | Extract structured attributes + flags from case input |
| `retrieve_policy` | RAG query against ChromaDB for top-5 policy chunks |
| `decide_action` | Preliminary decision + determine if tools are needed |
| `call_tool_if_needed` | Execute `check_eligibility`, `fetch_case_history`, optionally `escalate_case` |
| `generate_final_decision` | Final structured decision with policy citations and "why this decision" |
| `evaluate_decision` | 4-axis evaluation: groundedness, policy consistency, escalation, retrieval |
| `suggest_improvement` | Produce actionable improvement if evaluation score < 0.7 |
| `save_trace` | Persist full trace to SQLite |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/cases/review` | Run full decision workflow |
| `GET` | `/api/traces` | List traces (paginated) |
| `GET` | `/api/traces/{id}` | Get full trace detail |
| `POST` | `/api/seed` | Seed vector store + sample data |
| `GET` | `/api/health` | Health check |

## Demo Walkthrough

1. **Landing page** → Click "Launch Decision Engine"
2. **Case Review** → Click any of the 4 demo cases to auto-fill the form
3. **Run Decision Review** → Watch the pipeline process (3-5 seconds)
4. **Decision Result** → See decision, confidence, "Why This Decision?", policy citations, tool calls, and evaluation
5. **Trace History** → View all past decisions with groundedness indicators
6. **Trace Detail** → Inspect node-by-node execution timeline, tool outputs, and evaluation scores

### Sample Cases

| Case | Expected Decision |
|------|-------------------|
| Standard refund, $49.99, within 30 days | APPROVE |
| VIP Platinum, $299, 47 days, 3rd exception | ESCALATE |
| 4th refund this year, suspicious pattern, $89 | DENY |
| Damaged goods, $650, missing photos | NEED_MORE_INFO |

## Policy Corpus

12 policy documents covering:

| Policy | Topic |
|--------|-------|
| POL-001 | Standard 30-day refund policy |
| POL-002 | Damaged goods exception |
| POL-003 | Fraud review rules |
| POL-004 | VIP customer policy |
| POL-005 | Repeated exceptions policy |
| POL-006 | Missing documentation policy |
| POL-007 | Escalation criteria |
| POL-008 | High-value transaction policy |
| POL-009 | Suspicious activity triggers |
| POL-010 | Manual override rules |
| POL-011 | Partial refund policy |
| POL-012 | Service credit policy |

## Folder Structure

```
opspilot-ai/
├── frontend/                  # Next.js app
│   ├── app/
│   │   ├── page.tsx           # Landing page
│   │   ├── review/page.tsx    # Case review + result
│   │   ├── traces/page.tsx    # Trace history
│   │   └── traces/[id]/       # Trace detail
│   └── lib/
│       ├── api.ts             # Backend API client
│       ├── types.ts           # TypeScript types
│       └── samples.ts         # Demo case data
├── backend/                   # Python FastAPI
│   ├── main.py                # App entry
│   ├── config.py              # Settings
│   ├── seed.py                # Seed script
│   ├── api/routes.py          # API endpoints
│   ├── workflow/
│   │   ├── state.py           # LangGraph state schema
│   │   ├── nodes.py           # 8 workflow nodes
│   │   └── graph.py           # StateGraph definition
│   ├── rag/vectorstore.py     # ChromaDB setup + retrieval
│   ├── tools/mock_tools.py    # 3 mock operational tools
│   ├── db/                    # SQLite CRUD
│   ├── models/                # Pydantic schemas
│   └── data/policies/         # 12 seed policy documents
└── .env.example
```

## License

MIT
