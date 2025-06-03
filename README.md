# MedAgenticSage
Med = Healthcare/Medicine  Agentic = Autonomous agents  Sage = Wisdom, reasoning, knowledge
MedAgenticSage is an autonomous AI system for healthcare, built with Python, LangGraph, and Streamlit. It combines modular AI agents for symptom analysis, medical Q&A, EHR summarization, treatment planning, and medication safety—bringing wisdom, autonomy, and reasoning to healthcare AI.


# 🧠 Autonomous Healthcare Assistant — Agentic AI System

An autonomous, modular AI agent system for healthcare that can:
- ✅ Check symptoms → differential diagnosis
- ✅ Summarize clinical/EHR notes
- ✅ Answer questions using biomedical literature
- ✅ Recommend treatment plans
- ✅ Check drug safety and interactions

Built with:
- 🧱 LangGraph for agent orchestration
- 🧠 GPT-4, Claude, LLaMA
- 🔍 PubMed, DrugBank, MIMIC
- 🔁 Modular Jupyter notebooks for development
- 🖼️ Streamlit (UI planned in later phase)

---

## 📁 Folder Structure

```

autonomous\_healthcare\_assistant/
│
├── 0\_setup\_environment.ipynb           # Set up APIs, LLMs, tools
├── 1\_symptom\_checker.ipynb             # Symptom → Diagnosis agent
├── 2\_ehr\_summarizer.ipynb              # Clinical note summarizer
├── 3\_literature\_qa.ipynb               # PubMed QA via RAG
├── 4\_drug\_interaction\_checker.ipynb    # Drug safety/interaction checker
├── 5\_treatment\_planner.ipynb           # Personalized care planning
├── 6\_agentic\_orchestration.ipynb       # LangGraph: combine all agents
│
├── utils/                              # Helper scripts, prompts, tools
│   ├── api\_helpers.py
│   ├── prompt\_templates.py
│   └── data\_loader.py
│
├── data/                               # MIMIC excerpts, sample cases
│   └── (test EHRs, drug lists, etc.)
│
└── README.md

````

---

## 🔧 Tech Stack

| Layer                  | Tools & Frameworks                            |
|------------------------|-----------------------------------------------|
| UI (future)            | Streamlit                                     |
| API Gateway (future)   | FastAPI                                       |
| Agentic Logic          | LangGraph, LangChain                          |
| LLMs                   | OpenAI GPT-4, Claude, LLaMA (local/remote)    |
| Retrieval              | Chroma, FAISS + PubMed API                    |
| Tools/APIs             | DrugBank API, OpenFDA, PubMed, MIMIC          |
| Memory (optional)      | LangGraph Memory, Redis                       |

---

## 🚀 Build Roadmap

| Phase | Module                        | Focus                          |
|-------|-------------------------------|---------------------------------|
| 1     | `1_symptom_checker.ipynb`     | MVP with LLM + prompt + tools  |
| 2     | `2_ehr_summarizer.ipynb`      | MIMIC parsing + summarization  |
| 3     | `3_literature_qa.ipynb`       | PubMed search + RAG            |
| 4     | `4_drug_interaction_checker`  | Drug safety checks             |
| 5     | `5_treatment_planner.ipynb`   | Clinical logic + guidelines    |
| 6     | `6_agentic_orchestration`     | LangGraph + memory             |
| 7     | UI + feedback loop            | Streamlit UI, RLHF             |

---

## ✅ Getting Started

1. Clone this repo:
    ```bash
    git clone https://github.com/yourname/autonomous_healthcare_assistant.git
    cd autonomous_healthcare_assistant
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set your `.env` with API keys:
    ```env
    OPENAI_API_KEY=...
    PUBMED_API_KEY=...
    DRUGBANK_API_KEY=...
    ```

4. Start with the first notebook:
    ```
    0_setup_environment.ipynb
    ```

---

## 📌 Notes

- All modules are independently testable.
- UI will be built once all agents are validated.
- The system is designed to be composable and extendable.

---

## 🧠 License & Attribution

- Based on public datasets: MIMIC, HumanDx, PubMed, etc.
- All medical logic and recommendations should be validated by licensed professionals.
