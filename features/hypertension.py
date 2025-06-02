import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
from core.helper import classify_blood_pressure, t
from core.models import load_models

# New: Risk categorization based on model output
def categorize_risk(prob):
    if prob >= 0.75:
        return "High Risk", "🔴", "risk_advice_high"
    elif prob >= 0.4:
        return "Moderate Risk", "🟠", "risk_advice_moderate"
    else:
        return "Low Risk", "🟢", "risk_advice_low"

def run():
    page_title=t("🩺 Hypertension Risk Prediction")
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

    # --- Input fields (unchanged as requested) ---
    age = st.slider(t("Age"), 1, 100, 30, help=t('Enter the age of the patient.'))
    gender = st.radio(t("Gender"), ["Male", "Female", "Other"])
    has_heart_disease = st.radio(t("Do you have any heart disease?"), ["Yes", "No"], help=t('Does the patient have a history of heart disease?'))
    ever_married = st.radio(t("Ever Married"), ["Yes", "No"], help=t('Marital status of the patient.'))
    work_type = st.selectbox(t("Work Type"), ["Private", "Self-employed", "Govt_job", "children", "Never_worked"], help=t('Type of occupation of the patient.'))
    residence_type = st.radio(t("Residence Type"), ["Urban", "Rural"], help=t('Residential living area of the patient.'))
    avg_glucose = st.number_input(t("Average Glucose Level (mg/dL)"), min_value=50.0, max_value=300.0, step=0.1, help=t('Average glucose level in the blood.'))
    bmi = st.number_input(t("Body Mass Index (BMI)"), min_value=10.0, max_value=60.0, step=0.1, help=t('Body mass index of the patient.'))
    smoking_status = st.selectbox(t("Smoking Status"), ["never smoked", "formerly smoked", "smokes", "Unknown"], help=t('Smoking behavior of the patient.'))
    systolic = st.number_input(t("Systolic (mmHg)"), min_value=70, max_value=250, value=120)
    diastolic = st.number_input(t("Diastolic (mmHg)"), min_value=40, max_value=150, value=80)

    st.session_state["age"] = age
    st.session_state["gender"] = gender

    if avg_glucose < 70 or bmi < 10:
        st.warning(t("⚠️ Please enter realistic glucose and BMI values."))
        return

    # Encoding
    gender_map = {"Male": 1, "Female": 0, "Other": 2}
    married_map = {"Yes": 1, "No": 0}
    work_map = {"Private": 2, "Self-employed": 3, "Govt_job": 0, "children": 1, "Never_worked": 4}
    residence_map = {"Urban": 1, "Rural": 0}
    smoke_map = {"never smoked": 2, "formerly smoked": 1, "smokes": 3, "Unknown": 0}
    heart_disease = 1 if has_heart_disease == "Yes" else 0

    user_df = pd.DataFrame([{
        "gender": gender_map[gender],
        "age": age,
        "heart_disease": heart_disease,
        "ever_married": married_map[ever_married],
        "work_type": work_map[work_type],
        "Residence_type": residence_map[residence_type],
        "avg_glucose_level": avg_glucose,
        "bmi": bmi,
        "smoking_status": smoke_map[smoking_status]
    }])

    expected_order = [
        'gender', 'age', 'heart_disease', 'ever_married',
        'work_type', 'Residence_type', 'avg_glucose_level',
        'bmi', 'smoking_status'
    ]
    user_df = user_df[expected_order]

    # --- Button centered with full width in column ---
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        predict_button = st.button(t("Predict Hypertension Risk"), use_container_width=True)

    if predict_button:
        model = load_models()
        hypertension_model = model['hypertension']

        if hasattr(hypertension_model, "predict_proba"):
            prob = hypertension_model.predict_proba(user_df)[0][1]
            st.metric(t("Hypertension Risk Probability"), f"{prob*100:.2f}%")

            # Categorize based on risk percentage
            risk_category, risk_emoji, risk_advice_key = categorize_risk(prob)

            # Use translation keys for advice
            risk_advice = t(risk_advice_key)

            # Map emoji to colors (same as before)
            risk_color = {"🔴": "#E03E3E", "🟠": "#E07B39", "🟢": "#4CAF50"}[risk_emoji]

            st.markdown(f"""
            <div style="
                background-color: {risk_color};
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                color: white;
                margin-bottom: 20px;
            ">
                <h2 style='margin: 0;'>{risk_emoji} {t('Hypertension Risk Category')}: <strong>{t(risk_category)}</strong></h2>
                <p style='margin: 8px 0 0; font-size: 1.1em; font-weight: 500;'>{risk_advice}</p>
            </div>
            """, unsafe_allow_html=True)


            st.session_state["hypertension_result"] = {
                "risk_percent": f"{prob*100:.2f}%",
                "risk_category": risk_category,
                "risk_advice": risk_advice,
                "systolic": systolic,
                "diastolic": diastolic
            }
        else:
            st.warning(t("This model does not support probability prediction."))

        # BP classification
        bp_category, bp_emoji, bp_advice = classify_blood_pressure(systolic, diastolic, age, gender, has_heart_disease, avg_glucose, bmi, smoking_status)

        st.markdown(f"### {bp_emoji} {t('Blood Pressure Category')}: **{bp_category}**")
        st.markdown(f"**{t('Advice')}:** {bp_advice}")

        # Feature importance section with spacing and fallback message
        st.markdown("---")
        st.subheader(t("📊 Feature Importance"))
        try:
            importance = hypertension_model.coef_[0]
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(expected_order, importance, color="#FF4081")
            ax.set_xlabel(t("Weight"))
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            st.pyplot(fig)
        except AttributeError:
            st.info(t("Feature importance not available for this model."))

    st.markdown("---")  # Footer divider for clarity