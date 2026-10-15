from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.graph import support_graph
from app.schemas import ChatRequest, ChatResponse


load_dotenv(override=True)
app = FastAPI(
    title="Agentic AI Customer Support",
    description=(
        "A learning project demonstrating FastAPI, LangGraph, supervisor routing, "
        "specialist nodes, and RAG retrieval with FAISS."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = support_graph.invoke({"message": request.message})
        return ChatResponse(
            answer=result.get("answer", "Sorry, I could not generate a response."),
            intent=result.get("intent", "general"),
            order_result=result.get("order_result"),
            policy_result=result.get("policy_result"),
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc
