from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from backend.agents.nodes import (
    symptom_node,
    ehr_node,
    literature_node,
    drug_node,
    treatment_node,
    inject_retrieved_context,
)
from langchain.schema import AIMessage


class AgentState(TypedDict):
    symptoms: Optional[str]
    question: Optional[str]
    ehr_text: Optional[str]
    medications: Optional[list[str]]
    patient_profile: Optional[dict]
    diagnosis: Optional[str]
    summary: Optional[str]
    literature_answer: Optional[str]
    interaction_report: Optional[str]
    treatment_plan: Optional[str]
    context: Optional[str]


# -- Graph Definition --
def build_graph(llm, retriever, **kwargs):
    builder = StateGraph(AgentState)
    builder.add_node(
        "inject_context", lambda s: inject_retrieved_context(s, retriever, **kwargs)
    )
    builder.add_node(
        "symptom_checker", lambda s: symptom_node(s, llm, retriever, **kwargs)
    )
    builder.add_node("ehr_summarizer", lambda s: ehr_node(s, llm, retriever, **kwargs))
    builder.add_node(
        "literature_qa", lambda s: literature_node(s, llm, retriever, **kwargs)
    )
    builder.add_node("drug_checker", lambda s: drug_node(s, llm, retriever, **kwargs))
    builder.add_node(
        "treatment_planner", lambda s: treatment_node(s, llm, retriever, **kwargs)
    )

    builder.set_entry_point("inject_context")
    builder.add_conditional_edges(
        "inject_context",
        lambda s: s.get("question") is not None,
        {True: "literature_qa", False: "symptom_checker"},
    )
    builder.add_conditional_edges(
        "symptom_checker",
        lambda s: s.get("ehr_text") is not None,
        {True: "ehr_summarizer", False: "drug_checker"},
    )
    builder.add_edge("ehr_summarizer", "drug_checker")
    builder.add_edge("literature_qa", "drug_checker")
    builder.add_edge("drug_checker", "treatment_planner")
    builder.add_edge("treatment_planner", END)

    return builder.compile()


def serialize_state(state):
    def convert(obj):
        if isinstance(obj, AIMessage):
            return obj.dict() if hasattr(obj, "dict") else str(obj)
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        return obj

    return convert(state)
