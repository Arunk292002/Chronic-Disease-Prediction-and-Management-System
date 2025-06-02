import streamlit as st
import streamlit.components.v1 as components
import seaborn as sns
import matplotlib.pyplot as plt
from core.helper import create_input_df,t
from core.models import load_models
from code.imagerec import imagerecognise
import pandas as pd

models=load_models()
kidney_disease=models["kidney"]
kidney_disease_mri=models["kidney_mri"]

category_map = {
    'red_blood_cells': {'normal': 0, 'abnormal': 1},
    'pus_cell': {'normal': 0, 'abnormal': 1},
    'pus_cell_clumps': {'notpresent': 0, 'present': 1},
    'bacteria': {'notpresent': 0, 'present': 1},
    'hypertension': {'no': 0, 'yes': 1},
    'diabetes_mellitus': {'no': 0, 'yes': 1},
    'coronary_artery_disease': {'no': 0, 'yes': 1},
    'appetite': {'poor': 0, 'good': 1},
    'pedal_edema': {'no': 0, 'yes': 1},
    'anemia': {'no': 0, 'yes': 1}
}

def run():
    page_title=t("Chronic Kidney Disease Detection")
    # Custom Title with Gradient and Animation
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

    tab1, tab2=st.tabs([t("With Parameters"),t("With MRI")])
    with tab1:
        # categorical input
        col1, col2 = st.columns(2)
        with col1:
            age = st.slider(t('Age'), 0, 100, 30)
            blood_pressure = st.slider(t('Blood Pressure (mmHg)'), 0, 180, 80)
            specific_gravity = st.slider(t('Specific Gravity'), 1.000, 1.030, 1.015)
            albumin = st.slider(t('Albumin (g/dL)'), 0, 5, 0)
            sugar = st.slider(t('Sugar'), 0, 5, 0)
            blood_glucose_random = st.slider(t('Blood Glucose Random (mg/dL)'), 0, 500, 120)
        with col2:
            blood_urea = st.slider(t('Blood Urea (mg/dL)'), 0, 200, 40)
            serum_creatinine = st.slider(t('Serum Creatinine (mg/dL)'), 0.0, 10.0, 1.2)
            sodium = st.slider(t('Sodium (mEq/L)'), 110, 160, 135)
            potassium = st.slider(t('Potassium (mEq/L)'), 2.0, 10.0, 4.5)
            hemoglobin = st.slider(t('Hemoglobin (g/dL)'), 5.0, 20.0, 13.5)
            packed_cell_volume = st.slider(t('Packed Cell Volume (%)'), 20, 55, 40)

        st.markdown("---")
        st.markdown(t("🧫 Blood Cell Counts"))
        col3, col4 = st.columns(2)
        with col3:
            white_blood_cell_count = st.slider(t('WBC Count (cells/cumm)'), 4000, 20000, 10000)
        with col4:
            red_blood_cell_count = st.slider(t('RBC Count (millions/cumm)'), 2, 7, 5)

        st.markdown("---")
        st.markdown(t("⚕️ Clinical Symptoms & Conditions"))

        col5, col6 = st.columns(2)
        with col5:
            red_blood_cells = st.radio(t('Red Blood Cells'), ('normal', 'abnormal'))
            pus_cell = st.radio(t('Pus Cell'), ('normal', 'abnormal'))
            pus_cell_clumps = st.radio(t('Pus Cell Clumps'), ('notpresent', 'present'))
            bacteria = st.radio(t('Bacteria'), ('notpresent', 'present'))
            appetite = st.radio(t('Appetite'), ('good', 'poor'))

        with col6:
            hypertension = st.radio(t('Hypertension'), ('no', 'yes'))
            diabetes_mellitus = st.radio(t('Diabetes Mellitus'), ('no', 'yes'))
            coronary_artery_disease = st.radio(t('Coronary Artery Disease'), ('no', 'yes'))
            pedal_edema = st.radio(t('Pedal Edema'), ('no', 'yes'))
            anemia = st.radio(t('Anemia'), ('no', 'yes'))

        # Store user input
        user_inputs = {
            'age': age,
            'blood_pressure': blood_pressure,
            'specific_gravity': specific_gravity,
            'albumin': albumin,
            'sugar': sugar,
            'red_blood_cells': red_blood_cells,
            'pus_cell': pus_cell,
            'pus_cell_clumps': pus_cell_clumps,
            'bacteria': bacteria,
            'blood_glucose_random': blood_glucose_random,
            'blood_urea': blood_urea,
            'serum_creatinine': serum_creatinine,
            'sodium': sodium,
            'potassium': potassium,
            'hemoglobin': hemoglobin,
            'packed_cell_volume': packed_cell_volume,
            'white_blood_cell_count': white_blood_cell_count,
            'red_blood_cell_count': red_blood_cell_count,
            'hypertension': hypertension,
            'diabetes_mellitus': diabetes_mellitus,
            'coronary_artery_disease': coronary_artery_disease,
            'appetite': appetite,
            'pedal_edema': pedal_edema,
            'anemia': anemia
        }

        st.session_state["kidney_inputs"] = {
            'Specific Gravity': specific_gravity,
            'Albumin': albumin,
            'Sugar': sugar,
            'Red Blood Cells': red_blood_cells,
            'Pus Cell': pus_cell,
            'Pus Cell Clumps': pus_cell_clumps,
            'Bacteria': bacteria,
            'Blood Glucose (Random)': blood_glucose_random,
            'Blood Urea': blood_urea,
            'Serum Creatinine': serum_creatinine,
            'Sodium': sodium,
            'Potassium': potassium,
            'Hemoglobin': hemoglobin,
            'Packed Cell Volume': packed_cell_volume,
            'White Blood Cell Count': white_blood_cell_count,
            'Red Blood Cell Count': red_blood_cell_count,
            'Hypertension': hypertension,
            'Diabetes Mellitus': diabetes_mellitus,
            'Coronary Artery Disease': coronary_artery_disease,
            'Appetite': appetite,
            'Pedal Edema': pedal_edema,
            'Anemia': anemia
        }

        # Prediction
        st.markdown("---")
        if st.button(t("🔍 Predict")):
            input_df = create_input_df(user_inputs, category_map)
            prediction = kidney_disease.predict(input_df)

            if prediction[0] == 0:
                kidney_diagnosis = t('⚠️ The patient is likely to have **Chronic Kidney Disease**.')
            else:
                kidney_diagnosis = t('✅ The patient is **unlikely to have Chronic Kidney Disease**.')

            st.success(kidney_diagnosis)
            st.session_state['kidney_diagnosis'] = kidney_diagnosis

            with st.expander(t("🔎 Show model details")):
                st.json(kidney_disease.get_params())
                st.write(t("Model used: **Support Vector Machine (SVM)**"))

        # Heatmap
        st.markdown("---")
        st.subheader(t("📊 Kidney Disease Risk Factors Heatmap"))
        if st.button(t("Show Heatmap")):
            kidney_data = pd.DataFrame({
                "Blood Urea": [st.sidebar.number_input("Blood Urea", min_value=0.0, max_value=100.0, value=30.0)],
                "Hemoglobin": [st.sidebar.number_input("Hemoglobin", min_value=5.0, max_value=20.0, value=13.0)],
                "Serum Creatinine": [st.sidebar.number_input("Serum Creatinine", min_value=0.0, max_value=10.0, value=1.2)],
                "Age": [age]
            })

            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(kidney_data.corr(), annot=True, cmap='coolwarm', ax=ax)
            st.pyplot(fig)


        with tab2:
            # File Uploader Section
            uploaded_file = st.file_uploader(t("📤 Upload a Kidney Ultrasound Image"), type=['jpg', 'jpeg', 'png'])

            if uploaded_file:
                st.image(uploaded_file, caption=t("🖼️ Uploaded Kidney Image"), use_column_width=True)

            # Prediction Button and Result
            if st.button(t("🔍 Predict"),key="predict_button"):
                with st.spinner(t("🔬 Analyzing Image... Please wait.")):
                    image_bytes = uploaded_file.read()
                    y, conf = imagerecognise(image_bytes, kidney_disease_mri, "models/kidney_labels.txt")
                    st.session_state['kidney_prediction_label'] = y.strip().lower()
                    st.session_state['kidney_prediction_confidence'] = conf
                    st.session_state['kidney_ultrasound_image'] = image_bytes

                if y.strip().lower() == "normal":
                    predict_res=t("✅ Kidneys are Healthy!")
                    components.html(f"""
                        <style>
                            .result {{
                                font-family: 'Segoe UI', sans-serif;
                                font-size: 32px;
                                font-weight: bold;
                                color: #009688;
                                text-align: center;
                                margin-top: 30px;
                                animation: fadeIn 1s ease-in;
                            }}
                            @keyframes fadeIn {{
                                from {{opacity: 0;}}
                                to {{opacity: 1;}}
                            }}
                        </style>
                        <div class="result">{predict_res}</div>
                    """, height=100)
                else:
                    predict_res=t("❌ Kidney Disease Detected!")
                    predict_subtext=t("⚠️ Consult a Nephrologist Immediately")
                    components.html(f"""
                        <style>
                            .result-bad {{
                                font-family: 'Segoe UI', sans-serif;
                                font-size: 30px;
                                font-weight: bold;
                                color: #D32F2F;
                                text-align: center;
                                margin-top: 30px;
                                animation: shake 0.5s ease-in-out infinite alternate;
                            }}
                            .subtext {{
                                font-size: 18px;
                                font-weight: normal;
                                color: #FF7043;
                                text-align: center;
                                margin-top: 10px;
                            }}
                            @keyframes shake {{
                                0% {{transform: translateX(0);}}
                                100% {{transform: translateX(5px);}}
                            }}
                        </style>
                        <div class="result-bad">{predict_res}</div>
                        <div class="subtext">{predict_subtext}</div>
                    """, height=120)
            

