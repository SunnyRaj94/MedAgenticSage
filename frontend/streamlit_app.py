import streamlit as st
import json
from backend.db.api import SqliteDB_Agent
from backend.llm.api import load_llm_langchain
from backend.vector_db.clients import get_vector_retriever
from backend.agents.graph import build_graph, serialize_state
from configs import models, env, settings
import os
import warnings

warnings.filterwarnings(action="ignore")


os.environ["TOKENIZERS_PARALLELISM"] = "false"


# st.set_option("server.runOnSave", False)
def safe_display(value):
    if isinstance(value, list):
        for item in value:
            st.markdown(f"- {item}")
    elif isinstance(value, dict):
        if "content" in value:
            value = value["content"]
        if isinstance(value, dict):
            st.json(value)
        elif isinstance(value, list):
            for item in value:
                st.markdown(f"- {item}")
        else:
            st.write(value)
    else:
        st.write(value)


config_loaded = {"model_config": models, "env": env}
llm_selected = settings["llm"]

# -- Setup Configurable DB Path --
AGENT_DB = SqliteDB_Agent("data/db", "medagentic_runs")
AGENT_DB.create_table()

# -- Streamlit Config --
st.set_page_config(page_title="MedAgenticSage", layout="wide")
st.title("🧠 MedAgenticSage - AI Healthcare Agent")

# -- Load LLM + Retriever --
llm = load_llm_langchain(**llm_selected, config=config_loaded)
retriever = get_vector_retriever(**settings["retriever"])

graph = build_graph(llm=llm, retriever=retriever)

# -- Run Form UI --
with st.expander("🩺 Run New Agent"):
    with st.form("run_form"):
        symptoms = st.text_input("Symptoms", value="fever, chills, cough")
        ehr_text = st.text_area(
            "EHR Text", value="Patient reports fatigue and persistent cough."
        )
        question = st.text_input(
            "Literature Question",
            value="What treatments work for respiratory infections?",
        )
        medications = st.text_input(
            "Medications (comma-separated)", value="paracetamol, azithromycin"
        )
        patient_age = st.number_input("Age", value=45)
        patient_sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        submitted = st.form_submit_button("🚀 Run Agent")

if submitted:
    initial_state = {
        "symptoms": symptoms,
        "ehr_text": ehr_text,
        "question": question,
        "medications": [m.strip() for m in medications.split(",")],
        "patient_profile": {
            "age": patient_age,
            "sex": patient_sex,
            "diagnosis": "none",
            "comorbidities": [],
        },
    }

    with st.spinner("🧠 Thinking..."):
        final_state = graph.invoke(initial_state)
        final_state = serialize_state(final_state)
        initial_state = serialize_state(initial_state)

        AGENT_DB.save_run(initial_state, final_state)

    st.success("✅ Agent run completed!")
    for key, value in final_state.items():
        with st.expander(f"{key.upper()}"):
            safe_display(value)

# -- History Viewer --
st.subheader("📜 Past Runs")
keyword = st.text_input("🔍 Search past runs")

if keyword:
    results = AGENT_DB.search_runs(keyword)
else:
    results = AGENT_DB.get_all_runs()

for run in results:
    with st.expander(f"🧾 Run ID: {run['id']} | {run['timestamp']}"):
        st.markdown(f"**Symptoms:** {run['symptoms']}")
        st.markdown(f"**Question:** {run['question']}")
        st.markdown("**Final State:**")
        st.json(json.loads(run["final_state"]))
        if st.button("🗑 Delete", key=f"delete_{run['id']}"):
            AGENT_DB.delete_run(run["id"])
            st.experimental_rerun()
