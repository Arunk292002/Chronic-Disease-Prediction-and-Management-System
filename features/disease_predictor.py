import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from code.DiseaseModel import DiseaseModel
from code.helper import prepare_symptoms_array
from core.helper import t

def run():
    # Initialize model
    disease_model = DiseaseModel()
    model_path = Path("models/xgboost_model.json")  # relative path (adjust if needed)
    disease_model.load_xgboost(str(model_path))
    page_title=t("🧠 Disease Prediction using Machine Learning")


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


    st.markdown("""---""")
    st.subheader(t("🤒 Enter Your Symptoms Below"))

    # Symptom selection
    symptoms = st.multiselect(
        t("What are your symptoms?"),
        options=sorted(disease_model.all_symptoms),
        placeholder=t("Start typing to search for symptoms..."),
    )

    st.session_state["symptoms_selected"] = symptoms

    # Prepare input array
    X = prepare_symptoms_array(symptoms)

    # Predict Button
    st.markdown("""<div style='text-align: center;'>""", unsafe_allow_html=True)
    predict_btn = st.button(t("🔍 Predict"), disabled=len(symptoms) == 0)
    st.markdown("""</div>""", unsafe_allow_html=True)

    if predict_btn:
        try:
            prediction, prob = disease_model.predict(X)
            prob_percent = f"{prob * 100:.2f}%"

            # Store in session
            st.session_state["general_disease_name"] = prediction
            st.session_state["general_disease_probability"] = prob_percent
            st.session_state["disease_description"] = disease_model.describe_predicted_disease()
            st.session_state["disease_precautions"] = disease_model.predicted_disease_precautions()

            # Output display
            st.markdown(f"## 🩺 {t('Predicted Disease')}: **{prediction}**")
            st.markdown(f"### 🎯 {t('Confidence')}: **{prob_percent}**")

            tab1, tab2 = st.tabs([t("📖 Description"), t("🛡️ Precautions")])

            with tab1:
                st.markdown("""<div style='padding: 10px; border-left: 4px solid #FF4081; background-color: #f9f9f9;'>""", unsafe_allow_html=True)
                st.write(st.session_state["disease_description"])
                st.markdown("""</div>""", unsafe_allow_html=True)

            with tab2:
                precautions = st.session_state["disease_precautions"]
                if precautions:
                    st.markdown("<ul>", unsafe_allow_html=True)
                    for i, p in enumerate(precautions[:4]):
                        st.markdown(f"<li>{p}</li>", unsafe_allow_html=True)
                    st.markdown("</ul>", unsafe_allow_html=True)
                else:
                    st.info(t("No precautions found for this disease."))

        except Exception as e:
            st.error(f"❌ {t('Prediction failed')}: {str(e)}")