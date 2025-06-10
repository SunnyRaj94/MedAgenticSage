# main.py - Enhanced MedAgenticSage Dashboard
import streamlit as st
import json
import faiss

# from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# import time
from frontend.utils.api import CSS_MAIN

from backend.db.api import SqliteDB_Agent
from backend.llm.api import load_llm_langchain
from backend.vector_db.clients import get_vector_retriever, get_embeddings_model
from backend.agents.graph import build_graph, serialize_state
from configs import models, env, settings


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


def safe_display_as_string(value):
    """
    Safely formats various types of agent output into a string.
    """
    if isinstance(value, list):
        # Join list items with hyphens for readability
        return "\n".join([f"- {item}" for item in value])
    elif isinstance(value, dict):
        # Prioritize 'content' key if it exists
        if "content" in value:
            content_value = value["content"]
            if isinstance(content_value, dict):
                # For nested dicts, return JSON string
                return f"```json\n{json.dumps(content_value, indent=2)}\n```"
            elif isinstance(content_value, list):
                # For lists within 'content', join with hyphens
                return "\n".join([f"- {item}" for item in content_value])
            else:
                # Fallback for other types in 'content'
                return str(content_value)
        else:
            # If no 'content' key, return JSON string of the whole dict
            return f"```json\n{json.dumps(value, indent=2)}\n```"
    else:
        # For all other types, convert directly to string
        return str(value)


# Mock data for demonstration - replace with your actual backend calls
class MockDB:
    def get_stats(self):
        return {"cases_today": 24, "accuracy": 89, "avg_time": 15, "total_cases": 1247}

    def get_recent_cases(self):
        return [
            {
                "id": 1,
                "type": "Respiratory",
                "status": "Completed",
                "time": "2 min ago",
            },
            {"id": 2, "type": "Cardiac", "status": "In Progress", "time": "5 min ago"},
            {"id": 3, "type": "Drug Check", "status": "Completed", "time": "8 min ago"},
            {
                "id": 4,
                "type": "Literature QA",
                "status": "Completed",
                "time": "12 min ago",
            },
        ]

    def get_usage_data(self):
        dates = pd.date_range(start="2024-01-01", end="2024-01-30", freq="D")
        return pd.DataFrame(
            {
                "date": dates,
                "cases": [15 + i % 20 + (i // 7) * 3 for i in range(len(dates))],
                "accuracy": [85 + (i % 10) + (i // 15) * 2 for i in range(len(dates))],
            }
        )


# Page configuration
st.set_page_config(
    page_title="MedAgenticSage",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling
st.markdown(
    CSS_MAIN,
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_medagentic_components():
    config_loaded = {"model_config": models, "env": env}
    llm_selected = settings["llm"]

    AGENT_DB = SqliteDB_Agent("data/db", "medagentic_runs")
    AGENT_DB.create_table()

    llm = load_llm_langchain(**llm_selected, config=config_loaded)
    retriever = get_vector_retriever(
        **settings["retriever"],
    )
    embeddings_model = get_embeddings_model()
    index = faiss.IndexFlatL2(embeddings_model.get_sentence_embedding_dimension())
    graph = build_graph(
        llm=llm, retriever=retriever, embedding_model=embeddings_model, index=index
    )
    return AGENT_DB, llm, retriever, graph


AGENT_DB, llm, retriever, graph = initialize_medagentic_components()


# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "mock_db" not in st.session_state:
    st.session_state.mock_db = MockDB()

# Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
    <div class="main-header">
        <h2>🧠 MedAgenticSage</h2>
        <p>AI-Powered Healthcare Assistant</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Navigation Menu
    st.markdown("### 📋 Navigation")

    nav_options = {
        "🏠 Dashboard": "Dashboard",
        "💬 Chat Interface": "Chat",
        "📊 Analytics": "Analytics",
        "📋 Case Management": "Cases",
        "🔍 Search & History": "Search",
        "📚 Knowledge Base": "Knowledge",
        "⚙️ Settings": "Settings",
    }

    for label, page in nav_options.items():
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.current_page = page

    st.markdown("---")

    # Quick Stats in Sidebar
    st.markdown("### 📈 Quick Stats")
    stats = st.session_state.mock_db.get_stats()

    st.metric("Cases Today", stats["cases_today"], delta=5)
    st.metric("Accuracy", f"{stats['accuracy']}%", delta="2%")
    st.metric("Avg Time", f"{stats['avg_time']} min", delta="-3 min")

    st.markdown("---")
    st.markdown("**👤 Dr. Sarah Wilson**")
    st.markdown("🏥 General Medicine")
    st.markdown("🌟 Premium Account")


# Main Content Area
def render_dashboard():
    st.markdown(
        """
    <div class="main-header">
        <h1>🏠 Medical AI Dashboard</h1>
        <p>Welcome back! Here's your healthcare analytics overview</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    stats = st.session_state.mock_db.get_stats()

    with col1:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{stats['cases_today']}</p>
            <p class="metric-label">Cases Today</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{stats['accuracy']}%</p>
            <p class="metric-label">Accuracy Rate</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{stats['avg_time']}</p>
            <p class="metric-label">Avg Time (min)</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="metric-card">
            <p class="metric-value">{stats['total_cases']}</p>
            <p class="metric-label">Total Cases</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Main Content Row
    col1, col2 = st.columns([2, 1])

    with col1:
        # Usage Trends Chart
        st.markdown("### 📈 Usage Trends")

        usage_data = st.session_state.mock_db.get_usage_data()

        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Daily Cases", "Accuracy Trend"),
            vertical_spacing=0.1,
        )

        fig.add_trace(
            go.Scatter(
                x=usage_data["date"],
                y=usage_data["cases"],
                mode="lines+markers",
                name="Cases",
                line=dict(color="#667eea", width=3),
                marker=dict(size=6),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=usage_data["date"],
                y=usage_data["accuracy"],
                mode="lines+markers",
                name="Accuracy %",
                line=dict(color="#764ba2", width=3),
                marker=dict(size=6),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Recent Cases
        st.markdown("### 🕒 Recent Cases")

        recent_cases = st.session_state.mock_db.get_recent_cases()

        for case in recent_cases:
            status_class = (
                "status-completed"
                if case["status"] == "Completed"
                else "status-progress"
            )
            st.markdown(
                f"""
            <div class="recent-case">
                <strong>Case #{case['id']}</strong> - {case['type']}<br>
                <span class="{status_class}">{case['status']}</span>
                <small style="float: right; color: #666;">{case['time']}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Quick Actions
        st.markdown("### 🚀 Quick Actions")

        if st.button("💬 Start New Chat", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()

        if st.button("📄 Upload Medical Report", use_container_width=True):
            st.info("File upload functionality coming soon!")

        if st.button("🔍 Search Past Cases", use_container_width=True):
            st.session_state.current_page = "Search"
            st.rerun()

        if st.button("📊 View Full Analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()


# def render_chat_interface():
#     st.markdown(
#         """
#     <div class="main-header">
#         <h1>💬 Medical Consultation Chat</h1>
#         <p>Conversational AI for medical case analysis</p>
#     </div>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Chat Preview
#     st.markdown(
#         """
#     <div class="chat-preview">
#         <h3>🤖 AI Medical Assistant</h3>
#         <p>Hello! I'm your AI medical assistant. I can help you with:</p>
#         <ul>
#             <li>Symptom analysis and differential diagnosis</li>
#             <li>Drug interaction checking</li>
#             <li>Literature review and recommendations</li>
#             <li>Treatment planning</li>
#             <li>EHR summarization</li>
#         </ul>
#         <p><strong>Ready to start a consultation?</strong></p>
#     </div>
#     """,
#         unsafe_allow_html=True,
#     )

#     # Chat Interface Placeholder
#     st.info("🚧 Advanced chat interface with multi-modal input coming in next phase!")

#     # Quick Start Options
#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown("### 🩺 Quick Consultation")
#         symptoms = st.text_area(
#             "Describe symptoms:", placeholder="e.g., fever, cough, fatigue..."
#         )
#         age = st.number_input("Patient age:", min_value=0, max_value=120, value=30)

#     with col2:
#         st.markdown("### 📋 Additional Info")
#         medical_history = st.text_area(
#             "Medical history:", placeholder="Previous conditions, medications..."
#         )
#         urgency = st.selectbox("Urgency level:", ["Low", "Medium", "High", "Emergency"])

#     if st.button("🚀 Start Analysis", use_container_width=True):
#         with st.spinner("Analyzing case..."):
#             time.sleep(2)  # Simulate processing
#             st.success("Analysis complete! Results would appear here.")


def render_chat_interface():
    st.markdown(
        """
    <div class="main-header">
        <h1>💬 Medical Consultation Chat</h1>
        <p>Conversational AI for medical case analysis</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Chat Preview - Initial AI greeting
    st.markdown(
        """
    <div class="chat-preview">
        <h3>🤖 AI Medical Assistant</h3>
        <p>Hello! I'm your AI medical assistant. I can help you with:</p>
        <ul>
            <li>Symptom analysis and differential diagnosis</li>
            <li>Drug interaction checking</li>
            <li>Literature review and recommendations</li>
            <li>Treatment planning</li>
            <li>EHR summarization</li>
        </ul>
        <p><strong>Please provide details about the patient's symptoms and any relevant medical history to start.</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- Chat Input Form for MedAgenticSage Graph ---
    st.markdown("---")
    st.subheader("Start a New Medical Case Analysis")

    with st.form("medical_consultation_form"):
        st.write("Please provide the following details:")
        symptoms = st.text_area(
            "**1. Patient Symptoms:** Describe the primary symptoms (e.g., 'high fever, persistent cough, body aches')",
            placeholder="e.g., fever, cough, fatigue...",
            height=80,
        )
        ehr_text = st.text_area(
            "**2. EHR Text / Medical History (Optional):** Provide relevant past medical history, lab results, or clinical notes.",
            placeholder="e.g., 'Patient reports persistent cough with fatigue. Chest X-ray shows mild inflammation.'",
            height=80,
        )
        question = st.text_input(
            "**3. Specific Medical Question (Optional):** Ask a question for literature review (e.g., 'What recent treatments are effective for respiratory infections?')",
            placeholder="e.g., What recent treatments are effective for respiratory infections?",
        )
        medications = st.text_input(
            "**4. Current Medications (Comma-separated, Optional):** List any medications the patient is currently taking.",
            placeholder="e.g., paracetamol, azithromycin",
        )

        st.markdown("**5. Patient Profile (for context):**")
        col1, col2 = st.columns(2)
        with col1:
            patient_age = st.number_input("Age:", min_value=0, max_value=120, value=30)
        with col2:
            patient_sex = st.selectbox("Sex:", ["Male", "Female", "Other"])

        submit_button = st.form_submit_button("🚀 Get Medical Analysis")

    if submit_button and symptoms:  # Ensure symptoms are provided
        # Prepare initial state for the LangGraph
        initial_state = {
            "symptoms": symptoms,
            "ehr_text": ehr_text if ehr_text else None,  # Pass None if empty
            "question": question if question else None,  # Pass None if empty
            "medications": (
                [m.strip() for m in medications.split(",")] if medications else []
            ),
            "patient_profile": {
                "age": patient_age,
                "sex": patient_sex,
                "diagnosis": "none",  # This will be filled by the agent
                "comorbidities": [],  # Could be expanded with another input
            },
        }

        st.session_state["messages"] = []  # Clear previous messages for a new run
        st.session_state["messages"].append(
            {"role": "user", "content": f"Symptoms: {symptoms}"}
        )
        if ehr_text:
            st.session_state["messages"].append(
                {"role": "user", "content": f"EHR Text: {ehr_text}"}
            )
        if question:
            st.session_state["messages"].append(
                {"role": "user", "content": f"Question: {question}"}
            )
        if medications:
            st.session_state["messages"].append(
                {"role": "user", "content": f"Medications: {medications}"}
            )
        st.session_state["messages"].append(
            {
                "role": "user",
                "content": f"Patient Profile: Age {patient_age}, Sex {patient_sex}",
            }
        )
        st.session_state["messages"].append(
            {"role": "user", "content": "Running analysis..."}
        )

        with st.spinner("🧠 MedAgenticSage is analyzing the case..."):
            try:
                # Invoke the LangGraph agent
                final_state = graph.invoke(initial_state)

                # Serialize states for saving
                initial_state_serialized = serialize_state(initial_state)
                final_state_serialized = serialize_state(final_state)

                # Save the run to the database
                AGENT_DB.save_run(initial_state_serialized, final_state_serialized)

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": "✅ Analysis complete! Here are the findings:",
                    }
                )

                # Display detailed results in the chat interface
                for key, value in final_state.items():
                    if value and key not in [
                        "context",
                        "patient_profile",
                    ]:  # Exclude raw context and patient profile for cleaner display
                        st.session_state["messages"].append(
                            {
                                "role": "assistant",
                                "content": f"**📌 {key.upper().replace('_', ' ')}:**",
                            }
                        )
                        display_value = value  # Start with the full object
                        if hasattr(value, "content"):
                            # If it's a LangChain message object, extract its content
                            display_value = value.content
                        elif isinstance(value, dict) and "content" in value:
                            # If it's a dictionary that contains a 'content' key
                            display_value = value["content"]
                        # For displaying complex outputs like dicts/lists, convert to string or specific format
                        content_to_display = safe_display_as_string(display_value)
                        st.session_state["messages"].append(
                            {"role": "assistant", "content": content_to_display}
                        )

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": f"❌ An error occurred during analysis: {e}",
                    }
                )

    elif submit_button and not symptoms:
        st.error("Please describe the patient's symptoms to start the analysis.")

    # Display chat messages (both user input and agent responses)
    st.markdown("---")
    st.subheader("Consultation Log")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])


def render_analytics():
    st.markdown(
        """
    <div class="main-header">
        <h1>📊 Advanced Analytics</h1>
        <p>Comprehensive insights into your medical AI usage</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Performance", "🎯 Accuracy", "⏱️ Efficiency", "📋 Cases"]
    )

    with tab1:
        st.markdown("### Performance Overview")

        # Sample performance data
        performance_data = pd.DataFrame(
            {
                "Agent": [
                    "Symptom Checker",
                    "Drug Interaction",
                    "Literature QA",
                    "Treatment Planner",
                    "EHR Summarizer",
                ],
                "Usage": [45, 38, 52, 33, 28],
                "Accuracy": [92, 96, 88, 91, 94],
                "Avg_Time": [3.2, 1.8, 4.5, 5.1, 2.9],
            }
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                performance_data,
                x="Agent",
                y="Usage",
                title="Agent Usage Distribution",
                color="Usage",
                color_continuous_scale="viridis",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(
                performance_data,
                x="Accuracy",
                y="Avg_Time",
                size="Usage",
                hover_name="Agent",
                title="Accuracy vs Response Time",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### Accuracy Analysis")
        st.info("Detailed accuracy metrics and trends will be displayed here")

    with tab3:
        st.markdown("### Efficiency Metrics")
        st.info("Time-based performance analysis coming soon")

    with tab4:
        st.markdown("### Case Statistics")
        st.info("Comprehensive case breakdown and patterns")


def render_placeholder_page(title, description):
    st.markdown(
        f"""
    <div class="main-header">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.info("🚧 This section is under development and will be available soon!")
    st.markdown("### Coming Soon:")
    st.markdown("- Advanced search capabilities")
    st.markdown("- Case management tools")
    st.markdown("- Knowledge base integration")
    st.markdown("- Comprehensive settings panel")


# Main App Logic
def main():
    current_page = st.session_state.current_page

    if current_page == "Dashboard":
        render_dashboard()
    elif current_page == "Chat":
        render_chat_interface()
    elif current_page == "Analytics":
        render_analytics()
    elif current_page == "Cases":
        render_placeholder_page("📋 Case Management", "Manage and track medical cases")
    elif current_page == "Search":
        render_placeholder_page(
            "🔍 Search & History", "Search through case history and records"
        )
    elif current_page == "Knowledge":
        render_placeholder_page(
            "📚 Knowledge Base", "Access medical knowledge and references"
        )
    elif current_page == "Settings":
        render_placeholder_page("⚙️ Settings", "Configure your AI assistant preferences")


if __name__ == "__main__":
    main()
