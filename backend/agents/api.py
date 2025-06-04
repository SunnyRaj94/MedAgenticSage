from backend.prompts.templates import (
    symptom_prompt,
    ehr_summary_prompt,
    literature_qa_prompt,
    drug_interaction_prompt,
    treatment_prompt,
)


def run_symptom_checker(symptoms: str, llm) -> str:
    prompt = symptom_prompt(symptoms=symptoms)
    return llm.invoke(prompt)


def run_ehr_summarizer(ehr_text: str, llm) -> str:
    prompt = ehr_summary_prompt(ehr_text)
    return llm.invoke(prompt)


def run_literature_qa(question: str, llm, context: str = "") -> str:
    prompt = literature_qa_prompt(question, context)
    return llm.invoke(prompt)


def run_drug_interactions(meds: list, llm, patient_data: str = "") -> str:
    prompt = drug_interaction_prompt(meds, patient_data)
    return llm.invoke(prompt)


def run_treatment_plan(profile: dict, llm) -> str:
    prompt = treatment_prompt(profile)
    return llm.invoke(prompt)
