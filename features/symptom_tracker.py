import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
from core.helper import t,analyze_and_display_patterns, suggest_next_health_actions, analyze_symptom_patterns,COMMON_ILLNESS_PATTERNS
def run():
    page_title=t("🩺 Symptom Tracker")
    components.html(f"""
        <style>
            @keyframes fadeSlide {{
                0% {{opacity: 0; transform: translateY(-10px);}}
                100% {{opacity: 1; transform: translateY(0);}}
            }}
            #title {{
                font-family: 'Segoe UI', sans-serif;
                font-size: 3.5vw;
                font-weight: bold;
                text-align: center;
                margin-top: 15px;
                animation: fadeSlide 1s ease-out;
                background: linear-gradient(90deg, #FF4081, #FFCDD2);
                -webkit-background-clip: text;
                color: inherit;
                -webkit-text-fill-color: initial;
            }}
        </style>
        <div id="title">{page_title}</div>
    """, height=50)

    # Keep existing symptom tracking code
    selected_symptoms = st.multiselect(t("Select symptoms you're experiencing today:"), 
                                       ["Fever", "Cough", "Fatigue", "Headache", "Chest Pain", 
                                        "Shortness of Breath", "Nausea", "Sore Throat", 
                                        "Runny Nose", "Body Aches", "Dizziness", "Chills"])
    
    log_date = st.date_input(t("Date"), datetime.now().date())

    # Add symptom duration tracking
    duration_options = ["Started today", "1-2 days", "3-5 days", "1-2 weeks", "More than 2 weeks"]
    symptom_duration = {}
    symptom_severity = {}
    
    if selected_symptoms:
        st.subheader(t("Symptom Details:"))
        cols = st.columns(2)
        
        for i, symptom in enumerate(selected_symptoms):
            with cols[i % 2]:
                st.markdown(f"**{symptom}**")
                severity = st.select_slider(
                    f"{t('Severity')}:",
                    ["Mild", "Moderate", "Severe"],
                    key=f"severity_{symptom}"
                )
                duration = st.selectbox(
                    f"{t('Duration')}:",
                    duration_options,
                    key=f"duration_{symptom}"
                )
                symptom_severity[symptom] = severity
                symptom_duration[symptom] = duration
                st.markdown("---")

    # Access session state for symptom log
    if "symptom_log" not in st.session_state:
        st.session_state["symptom_log"] = pd.DataFrame(columns=["Date", "Symptom", "Severity", "Duration"])

    if st.button(t("Log Symptoms")):
        for symptom, severity in symptom_severity.items():
            duration = symptom_duration.get(symptom, "Started today")
            new_entry = pd.DataFrame([[log_date, symptom, severity, duration]], 
                                    columns=["Date", "Symptom", "Severity", "Duration"])
            st.session_state["symptom_log"] = pd.concat([st.session_state["symptom_log"], new_entry], ignore_index=True)
        st.success(t("Symptoms logged successfully!"))
        st.rerun()  # Refresh to show updated analysis

    # Show Symptom Log
    st.subheader(t("📝 Symptom Log"))
    if not st.session_state["symptom_log"].empty:
        st.dataframe(st.session_state["symptom_log"])
        
        # Add pattern analysis
        matches = analyze_symptom_patterns(st.session_state["symptom_log"])
        analyze_and_display_patterns(st.session_state["symptom_log"])
        suggest_next_health_actions(st.session_state["symptom_log"], matches)
    else:
        st.info(t("No symptoms logged yet. Start tracking your symptoms to see pattern analysis."))