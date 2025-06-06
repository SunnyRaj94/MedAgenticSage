from backend.agents.templates import Runner
from backend.agents.memory import add_to_memory, retrieve_context
from backend.vector_db.clients import VectorStoreBase


def log_keys(state, node_name):
    print(f"\U0001f511 Keys in state at {node_name}: {list(state.keys())}")


def symptom_node(state, llm, retriever: VectorStoreBase = None):
    log_keys(state, "symptom_node")
    diagnosis = Runner.run_symptom_checker(symptoms=state.get("symptoms"), llm=llm)
    state["diagnosis"] = diagnosis
    add_to_memory(diagnosis, source="diagnosis")
    return state


def ehr_node(state, llm, retriever: VectorStoreBase = None):
    log_keys(state, "ehr_node")
    summary = Runner.run_ehr_summarizer(ehr_text=state.get("ehr_text"), llm=llm)
    state["summary"] = summary
    add_to_memory(summary, source="ehr_summary")
    return state


def literature_node(state, llm, retriever: VectorStoreBase = None):
    log_keys(state, "literature_node")
    question = state.get("question")
    if retriever:
        context_docs = retriever.similarity_search(question)
        context = "\n".join([doc.page_content for doc in context_docs])
    else:
        context = "\n".join([r["text"] for r in retrieve_context(question)])
    answer = Runner.run_literature_qa(question=question, llm=llm, context=context)
    state["literature_answer"] = answer
    add_to_memory(answer, source="literature_qa")
    return state


def drug_node(state, llm, retriever: VectorStoreBase = None):
    log_keys(state, "drug_node")
    meds = state.get("medications")
    if isinstance(meds, str):
        meds = [m.strip() for m in meds.split(",") if m.strip()]
    elif not isinstance(meds, list):
        meds = []
    report = Runner.run_drug_interactions(
        meds=meds, llm=llm, patient_data=state.get("diagnosis", "")
    )
    state["interaction_report"] = report
    add_to_memory(report, source="drug_checker")
    return state


def treatment_node(state, llm, retriever: VectorStoreBase = None):
    log_keys(state, "treatment_node")
    plan = Runner.run_treatment_plan(profile=state.get("patient_profile"), llm=llm)
    state["treatment_plan"] = plan
    add_to_memory(plan, source="treatment_plan")
    return state


def inject_retrieved_context(state, vector_store: VectorStoreBase = None):
    query = state.get("question") or state.get("symptoms")
    if not query or not vector_store:
        return state
    context = vector_store.similarity_search(query)
    state["context"] = "\n".join([doc.page_content for doc in context])
    return state
