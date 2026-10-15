import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.state import SupportState
from app.tools.knowledge_tools import search_policies
from app.tools.order_tools import lookup_order


load_dotenv()


class RoutingDecision(BaseModel):
    intent: Literal["order", "policy", "both", "general"] = Field(
        description=(
            "Choose order for order status/details, policy for policy questions, "
            "both when both order data and policy information are needed, "
            "or general for unrelated/general support messages."
        )
    )


def get_model() -> ChatOpenAI:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key."
        )
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )


def supervisor_node(state: SupportState) -> dict:
    """Use the LLM to classify the request before routing to specialist nodes."""
    model = get_model().with_structured_output(RoutingDecision)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You route customer-support requests. Choose the smallest set of "
                "specialists needed. Use both if the request asks about an order "
                "and asks how a policy applies to that order. Use general for greetings "
                "or questions unrelated to orders and policies.",
            ),
            ("human", "{message}"),
        ]
    )
    decision = (prompt | model).invoke({"message": state["message"]})
    return {"intent": decision.intent}


def route_after_supervisor(state: SupportState) -> list[str]:
    intent = state.get("intent", "general")
    if intent == "order":
        return ["order_agent"]
    if intent == "policy":
        return ["policy_agent"]
    if intent == "both":
        # LangGraph can schedule these independent branches in parallel.
        return ["order_agent", "policy_agent"]
    return ["response_agent"]


def order_agent_node(state: SupportState) -> dict:
    return {"order_result": lookup_order(state["message"])}


def policy_agent_node(state: SupportState) -> dict:
    return {"policy_result": search_policies(state["message"])}


def response_agent_node(state: SupportState) -> dict:
    model = get_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a careful customer-support assistant. Answer in plain language. "
                "Use only the supplied order details and retrieved policy passages for "
                "claims about this customer's order or policy. Do not claim a refund, "
                "cancellation, or other action has been approved or performed. If details "
                "are missing, say what is needed. For a general question with no tool "
                "results, offer help and ask what the customer needs.",
            ),
            (
                "human",
                "Customer message:\n{message}\n\n"
                "Routing intent: {intent}\n\n"
                "Order lookup result:\n{order_result}\n\n"
                "Retrieved policy passages:\n{policy_result}\n\n"
                "Write the final response. If a result is not available, treat it as absent.",
            ),
        ]
    )
    answer = (prompt | model).invoke(
        {
            "message": state["message"],
            "intent": state.get("intent", "general"),
            "order_result": state.get("order_result", "Not requested."),
            "policy_result": state.get("policy_result", "Not requested."),
        }
    )
    return {"answer": answer.content}


builder = StateGraph(SupportState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("order_agent", order_agent_node)
builder.add_node("policy_agent", policy_agent_node)
builder.add_node("response_agent", response_agent_node)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route_after_supervisor)
builder.add_edge("order_agent", "response_agent")
builder.add_edge("policy_agent", "response_agent")
builder.add_edge("response_agent", END)

support_graph = builder.compile()
