"""OpsPilot AI — FastAPI Backend Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import FRONTEND_URL
from db.database import init_db
from rag.vectorstore import seed_vector_store
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and vector store on startup."""
    init_db()
    seed_vector_store()
    yield


app = FastAPI(
    title="OpsPilot AI",
    description="AI Decision Engine for Compliance-Critical Operational Workflows",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)
