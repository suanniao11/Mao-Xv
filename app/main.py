"""FastAPI application entry point for the AI Travel Agent."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.travel import router as travel_router

app = FastAPI(
    title="AI Travel Agent",
    description=(
        "An AI-powered travel assistant built with FastAPI and LangChain ReAct. "
        "Ask travel questions and the agent will use Map and Weather tools to answer."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(travel_router)


@app.get("/", tags=["health"])
async def root():
    """Health-check endpoint."""
    return {"status": "ok", "message": "AI Travel Agent is running."}


@app.get("/health", tags=["health"])
async def health():
    """Detailed health check."""
    return {"status": "healthy"}
