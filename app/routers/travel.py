"""Travel agent API router."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent import build_agent_executor

router = APIRouter(prefix="/travel", tags=["travel"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@router.post("/query", response_model=QueryResponse, summary="Ask the travel agent")
async def query_travel_agent(request: QueryRequest) -> QueryResponse:
    """
    Send a natural-language travel question to the AI agent.

    The agent uses the LangChain ReAct framework to reason through the question
    and call the appropriate tools (Map, Weather) as needed.

    **Example questions:**
    - "What is the weather like in Barcelona this week?"
    - "How do I get from Rome to Naples by train?"
    - "Find the best-rated restaurants near the Eiffel Tower."
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        executor = build_agent_executor()
        result = await executor.ainvoke({"input": request.question})
        answer = result.get("output", "No answer returned by the agent.")
        return QueryResponse(answer=answer)
    except ValueError as exc:
        # Configuration errors (missing API keys, etc.)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent encountered an error: {exc}",
        ) from exc
