import streamlit as st
import io
from fpdf import FPDF
from PIL import Image
from datetime import datetime
from code.meal_planner import get_personalized_meal_plan
from core.helper import t

def clean_text_for_pdf(text):
    return text.encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf():
        patient_name = st.session_state.get("patient_name", "Unknown")
        if not patient_name:
            st.error(t("❌ Cannot generate report: Please enter the patient's name first."))
            return None
        patient_age = st.session_state.get("patient_age", "N/A")
        patient_gender = st.session_state.get("patient_gender", "N/A")
        risk_score = st.session_state.get("risk_score", "N/A")
        risk_message = st.session_state.get("risk_message", "Not Available")
        suggestion = st.session_state.get("suggestion", [])
        pdf = FPDF()
        original_cell = FPDF.cell
        original_multi_cell = FPDF.multi_cell

        def safe_cell(self, *args, **kwargs):
            args = list(args)
            if len(args) > 1 and isinstance(args[1], str):
                args[1] = clean_text_for_pdf(args[1])
            return original_cell(self, *args, **kwargs)

        def safe_multi_cell(self, *args, **kwargs):
            args = list(args)
            if len(args) > 1 and isinstance(args[1], str):
                args[1] = clean_text_for_pdf(args[1])
            return original_multi_cell(self, *args, **kwargs)

        FPDF.cell = safe_cell
        FPDF.multi_cell = safe_multi_cell

        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Patient Health Report", ln=True, align="C")
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%m-%Y %H:%M:%S")
        report_id = current_datetime.strftime("REP-%Y%m%d-%H%M%S")
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Report ID: {report_id}", ln=True)
        pdf.cell(200, 10, f"Generated on: {formatted_datetime}", ln=True)
        pdf.ln(5)
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Patient Name: {patient_name}", ln=True)
        pdf.cell(200, 10, f"Age: {patient_age}", ln=True)
        pdf.cell(200, 10, f"Gender: {patient_gender}", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Health Data:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Blood Pressure: {st.session_state['blood_pressure']} mmHg", ln=True)
        pdf.cell(200, 10, f"Heart Rate: {st.session_state['heart_rate']} bpm", ln=True)
        pdf.cell(200, 10, f"Blood Sugar: {st.session_state['blood_sugar']} mg/dL", ln=True)
        pdf.cell(200, 10, f"Body Temperature: {st.session_state['temperature']} °C", ln=True)
        if "bmi" in st.session_state:
            pdf.cell(200, 10, f"BMI: {st.session_state['bmi']} kg/m²", ln=True)
            pdf.cell(200, 10, f"BMI Description: {st.session_state['bmi_desc']}", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Prediction Results:", ln=True)
        pdf.set_font("Arial", "", 12)
        fever_status = "Normal" if st.session_state['temperature'] < 38.0 else "Fever Detected"
        pdf.cell(200, 10, f"Fever Detection: {fever_status}", ln=True)

        # Hypertension and Fever
        if "hypertension_result" in st.session_state:
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Hypertension Risk Analysis", ln=True)
            pdf.set_font("Arial", "", 12)
            result = st.session_state["hypertension_result"]
            pdf.cell(200, 10, f"Systolic: {result.get('systolic', 'N/A')} mmHg", ln=True)
            pdf.cell(200, 10, f"Diastolic: {result.get('diastolic', 'N/A')} mmHg", ln=True)
            pdf.cell(200, 10, f"Blood Pressure Category: {result.get('bp_category', 'N/A')}", ln=True)
            pdf.multi_cell(0, 10, f"Advice: {result.get('bp_advice', 'N/A')}")
            risk = result.get("prediction")
            if risk == 1:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(200, 10, "Model Prediction: HIGH RISK", ln=True)
            else:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(200, 10, "Model Prediction: LOW RISK", ln=True)
            pdf.set_text_color(0, 0, 0)

        # Include Symptoms if available
        if "symptoms_selected" in st.session_state:
            symptoms = st.session_state["symptoms_selected"]
            if symptoms:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(200, 10, "Symptoms:", ln=True)
                pdf.set_font("Arial", "", 12)
                for symptom in symptoms:
                    pdf.cell(200, 10, f"- {symptom}", ln=True)
                pdf.ln(5)
        
        # General Disease Prediction (XGBoost based on symptoms)
        if "general_disease_name" in st.session_state:
            disease_name = st.session_state["general_disease_name"]
            disease_prob = st.session_state.get("general_disease_probability", "N/A")
            pdf.cell(200, 10, f"General Disease Prediction (Symptom-Based): {disease_name} ({disease_prob})", ln=True)
        
        # General Disease Description
        if "disease_description" in st.session_state:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Disease Description:", ln=True)
            pdf.set_font("Arial", "", 12)
            description_lines = st.session_state["disease_description"].split('\n')
            for line in description_lines:
                pdf.multi_cell(0, 10, line)
            pdf.ln(5)

        # General Disease Precautions
        if "disease_precautions" in st.session_state:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Precautions:", ln=True)
            pdf.set_font("Arial", "", 12)
            precautions = st.session_state["disease_precautions"]
            for i, item in enumerate(precautions, 1):
                pdf.cell(200, 10, f"{i}. {item}", ln=True)
            pdf.ln(5)

        # Include Diabetes Result
        if "diabetes_diagnosis" in st.session_state:
            if "diabetes_inputs" in st.session_state:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(200, 10, "Diabetes Input Details:", ln=True)
                pdf.set_font("Arial", "", 12)

                inputs = st.session_state["diabetes_inputs"]
                input_items = list(inputs.items())
                col_width = 90
                row_height = 10

                for i in range(0, len(input_items), 2):
                    # First column
                    key1, val1 = input_items[i]
                    formatted_key1 = key1.replace("_", " ").capitalize()
                    pdf.cell(col_width, row_height, f"{formatted_key1}: {val1}", ln=0)

                    # Second column, if exists
                    if i + 1 < len(input_items):
                        key2, val2 = input_items[i + 1]
                        formatted_key2 = key2.replace("_", " ").capitalize()
                        pdf.cell(col_width, row_height, f"{formatted_key2}: {val2}", ln=1)
                    else:
                        pdf.ln(row_height)
                pdf.ln(5)

            # Diabetes prediction output
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, f"Diabetes Prediction: {st.session_state['diabetes_diagnosis']}", ln=True)

        # Include Heart Prediction Result in PDF
        if "heart_diagnosis" in st.session_state:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, "Heart Disease Prediction Details:", ln=True)

            # Include input values if available
            if "heart_inputs" in st.session_state:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(200, 10, "Patient Inputs:", ln=True)
                pdf.set_font("Arial", "", 12)

                inputs = st.session_state["heart_inputs"]
                input_items = list(inputs.items())

                col_width = 90  # Width for each column
                row_height = 10

                for i in range(0, len(input_items), 2):
                    # First column
                    key1, val1 = input_items[i]
                    formatted_key1 = key1.replace("_", " ").capitalize()
                    pdf.cell(col_width, row_height, f"{formatted_key1}: {val1}", ln=0)

                    # Second column (if exists)
                    if i + 1 < len(input_items):
                        key2, val2 = input_items[i + 1]
                        formatted_key2 = key2.replace("_", " ").capitalize()
                        pdf.cell(col_width, row_height, f"{formatted_key2}: {val2}", ln=1)
                    else:
                        # If only one item in the last row
                        pdf.ln(row_height)

                pdf.ln(5)
            # Include the prediction result
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "Prediction Outcome:", ln=True)
            pdf.set_font("Arial", "", 12)
            diagnosis = st.session_state["heart_diagnosis"]
            if diagnosis==0:
                predict_desc="No Cardiovascular Disease Detected"
            else:
                predict_desc="High Risk of Cardiovascular Disease"
            pdf.cell(200, 10, f"Heart Disease Prediction: {predict_desc}", ln=True)
            pdf.ln(5)
            # Add Activity Level
            if "activity_level" in st.session_state:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(200, 10, f"Activity Level: {st.session_state['activity_level']}", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.ln(5)

            # Add Nutrition Guidelines
            if "nutrition_guidelines" in st.session_state:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(200, 10, "Nutrition Guidelines:", ln=True)
                pdf.set_font("Arial", "", 12)

                guidelines_data = st.session_state["nutrition_guidelines"]

                if isinstance(guidelines_data, dict):
                    # Convert dict to string with key-value formatting
                    formatted_guidelines = "\n".join([f"{k}: {v}" for k, v in guidelines_data.items()])
                else:
                    formatted_guidelines = str(guidelines_data)

                pdf.multi_cell(0, 10, formatted_guidelines)
                pdf.ln(5)

            # Add Nutrition Tips
            if "nutrition_tips" in st.session_state:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(200, 10, "Nutrition Tips:", ln=True)
                pdf.set_font("Arial", "", 12)

                tips_data = st.session_state["nutrition_tips"]

                if isinstance(tips_data, dict):
                    # Convert dict to string with key-value formatting
                    formatted_tips = "\n".join([f"{k}: {v}" for k, v in tips_data.items()])
                else:
                    formatted_tips = str(tips_data)

                pdf.multi_cell(0, 10, formatted_tips)
                pdf.ln(5)

        if "lung_prediction_label" in st.session_state:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Lung Cancer Analysis", ln=True)

            pdf.set_font("Arial", "", 12)
            result_text = (
                f"Prediction: {st.session_state['lung_prediction_label'].capitalize()}\n"
                f"Confidence: {st.session_state['lung_prediction_confidence']:.2f}%\n"
            )
            pdf.multi_cell(0, 10, result_text)

            # Add image if available
            if "lung_image_bytes" in st.session_state:
                image = Image.open(io.BytesIO(st.session_state["lung_image_bytes"]))
                image_path = "temp_lung_image.jpg"
                image.save(image_path)
                pdf.image(image_path, w=100)  # Adjust width as needed
                pdf.ln(5)

        # Include Kidney Result
        if "kidney_diagnosis" in st.session_state:
            if "kidney_inputs" in st.session_state:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Kidney Input Details:", ln=True)
                pdf.set_font("Arial", "", 12)
                inputs = st.session_state["kidney_inputs"]
                keys = list(inputs.keys())

                # Two-column layout: split keys into pairs
                for i in range(0, len(keys), 2):
                    key1 = keys[i]
                    val1 = inputs[key1]
                    key1_str = f"{key1}: {val1}"

                    if i + 1 < len(keys):
                        key2 = keys[i + 1]
                        val2 = inputs[key2]
                        key2_str = f"{key2}: {val2}"
                    else:
                        key2_str = ""
                    # Each row has two cells
                    pdf.cell(95, 10, key1_str, border=0)
                    pdf.cell(95, 10, key2_str, border=0, ln=True)
                pdf.ln(5)
            pdf.cell(200, 10, f"Kidney Disease Prediction: {st.session_state['kidney_diagnosis']}", ln=True)
            label = st.session_state.get("kidney_prediction_label", "Not available")
            confidence = st.session_state.get("kidney_prediction_confidence", "N/A")            
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Kidney Ultrasound Analysis", ln=True)

            pdf.set_font("Arial", "", 12)
            result_text = f"Prediction: {label.capitalize()}\nConfidence: {confidence:.2f}%"
            pdf.multi_cell(0, 10, result_text)
            # Add image if available
            if "kidney_ultrasound_image" in st.session_state:
                image = Image.open(io.BytesIO(st.session_state['kidney_ultrasound_image']))
                image_path = "temp_kidney_image.jpg"
                image.save(image_path)
                pdf.image(image_path, w=100)  # Resize as needed

        if "liver_diagnosis" in st.session_state:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "Liver Disease Risk Assessment", ln=True)
            # Define input labels and session state keys (adjust based on your app)
            input_fields = {
                "Age": "liver_age",
                "Gender": "liver_gender",
                "Total Bilirubin": "liver_total_bilirubin",
                "Direct Bilirubin": "liver_direct_bilirubin",
                "Alkaline Phosphotase": "liver_alk_phos",
                "Alamine Aminotransferase (ALT)": "liver_alt",
                "Aspartate Aminotransferase (AST)": "liver_ast",
                "Total Proteins": "liver_total_protein",
                "Albumin": "liver_albumin",
                "Albumin/Globulin Ratio": "liver_ag_ratio"
            }

            # Two-column layout
            col_width = 95  # half of A4 width
            row_height = 8
            keys = list(input_fields.items())

            for i in range(0, len(keys), 2):
                key1, val1 = keys[i]
                val1_data = st.session_state.get(val1, "N/A")
                pdf.cell(col_width, row_height, f"{key1}: {val1_data}", border=0)

                if i + 1 < len(keys):
                    key2, val2 = keys[i + 1]
                    val2_data = st.session_state.get(val2, "N/A")
                    pdf.cell(col_width, row_height, f"{key2}: {val2_data}", border=0)

                pdf.ln(row_height)
            pdf.set_font("Arial", '', 12)
            pdf.cell(200, 10, f"Prediction: {st.session_state['liver_diagnosis']}", ln=True)
            pdf.ln(5)

            # Optional: Add severity if available
            if "liver_risk_level" in st.session_state:
                pdf.cell(200, 10, f"Severity Level: {st.session_state['liver_risk_level']}", ln=True)
                pdf.ln(3)

        # 🎯 New Meal Plan Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Personalized Meal Recommendation:", ln=True)
        pdf.set_font("Arial", "", 12)

        # Generate meal plan dynamically
        meal_plan = get_personalized_meal_plan(
            glucose=st.session_state['blood_sugar'],
            bmi=24  # ✅ You can dynamically pass patient's BMI if available
        )

        for meal_time, meals in meal_plan.items():
            pdf.cell(200, 10, f"{meal_time}:", ln=True)
            for meal in meals:
                meal_line = f" - {meal['name']} | {meal['Calories']} kcal, {meal['Fibre']}g Fiber, {meal['Sugars']}g Sugar"
                pdf.cell(200, 10, meal_line, ln=True)
            pdf.ln(5)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Risk Assessment:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Risk Score: {risk_score}/100", ln=True)
        pdf.cell(200, 10, f"Risk Level: {clean_text_for_pdf(risk_message)}", ln=True)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Personalized Suggestions:", ln=True)
        pdf.set_font("Arial", "", 12)
        for tip in suggestion:
            pdf.cell(200, 10, f"- {clean_text_for_pdf(tip)}", ln=True)
        pdf.output("patient_report.pdf")
        return "patient_report.pdf"