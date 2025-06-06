symptom_prompt_template = """
You are a diagnostic medical assistant.

Given the following symptoms: {symptoms}

Return:
- A ranked list of likely diagnoses
- Suggested urgency level (low, medium, high)
- Recommended next steps for the patient

Be concise but medically accurate.
"""


ehr_summarizer_prompt_template = """
You are a clinical summarization agent.

Given the following raw clinical note or discharge summary:

---
{ehr_text}
---

Extract and return the following:
- Primary diagnosis
- Key findings (labs, vitals, procedures)
- Medications prescribed
- Follow-up recommendations
- Summary (in layman's terms)

Be clear and structured in your output.
"""

literature_qa_template = """
You are a medical assistant with access to the latest PubMed literature.

Based on the following research summaries:

---
{context}
---

Answer the question:
"{question}"

Be precise, cite evidence, and avoid speculation.
"""


drug_interaction_prompt_template = """
You are a medical safety assistant.

Given the following medications: {drugs}

Known interactions found:
{interactions}

Analyze the combination and provide:
- A safety summary
- Suggested monitoring actions
- Warnings and clinical advice

Be medically accurate and concise.
"""


treatment_prompt_template = """
You are an expert clinical decision support assistant.

Patient details:
- Diagnosis: {diagnosis}
- Age: {age}
- Sex: {sex}
- Comorbidities: {comorbidities}

Based on NICE, NIH, and other evidence-based guidelines:

🔹 Generate a step-by-step treatment plan
🔹 Include first-line and second-line options
🔹 Address all comorbidities
🔹 Include medication, lifestyle, follow-up, and referrals
🔹 Make it clear and clinician-ready
"""


def symptom_prompt(symptoms: str) -> str:  # NOQA
    return symptom_prompt_template.format(symptoms=symptoms)


def ehr_summary_prompt(ehr_text: str) -> str:  # NOQA
    return ehr_summarizer_prompt_template.format(ehr_text=ehr_text)


def literature_qa_prompt(question: str, context: str = "") -> str:  # NOQA
    return literature_qa_template.format(context=context, question=question)


def drug_interaction_prompt(  # NOQA
    meds: list[str], patient_data: str = ""
) -> str:  # NOQA
    med_list = ", ".join(meds)
    return drug_interaction_prompt_template.format(
        drugs=med_list, interactions=patient_data
    )


def treatment_prompt(profile: dict) -> str:  # NOQA
    return treatment_prompt_template.format(
        diagnosis=profile.get("diagnosis"),
        age=profile.get("age"),
        sex=profile.get("sex"),
        comorbidities=", ".join(profile.get("comorbidities", [])),
    )
