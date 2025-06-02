import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from core.models import load_models
from core.helper import t

# Initialize session state for tracking diagnoses
if "diagnoses_history" not in st.session_state:
    st.session_state.diagnoses_history = []

# Load the liver model with caching to optimize performance
@st.cache_resource
def load_liver_model():
    try:
        models = load_models()
        return models['liver']
    except Exception as e:
        st.error(f"{t('❌ Failed to load model:')} {str(e)}")
        return None

# Medical reference ranges for liver parameters
reference_ranges = {
    "Total_Bilirubin": {"min": 0.1, "max": 1.2, "unit": "mg/dL", "normal": "0.1-1.2 mg/dL"},
    "Direct_Bilirubin": {"min": 0.0, "max": 0.3, "unit": "mg/dL", "normal": "0.0-0.3 mg/dL"},
    "Alkaline_Phosphotase": {"min": 44, "max": 147, "unit": "IU/L", "normal": "44-147 IU/L"},
    "Alamine_Aminotransferase": {"min": 7, "max": 55, "unit": "IU/L", "normal": "7-55 IU/L"},
    "Aspartate_Aminotransferase": {"min": 8, "max": 48, "unit": "IU/L", "normal": "8-48 IU/L"},
    "Total_Protiens": {"min": 6.0, "max": 8.3, "unit": "g/dL", "normal": "6.0-8.3 g/dL"},
    "Albumin": {"min": 3.5, "max": 5.0, "unit": "g/dL", "normal": "3.5-5.0 g/dL"},
    "Albumin_and_Globulin_Ratio": {"min": 0.8, "max": 2.0, "unit": "", "normal": "0.8-2.0"}
}

# Parameter descriptions for tooltips
parameter_descriptions = {
    "Total_Bilirubin": "Total_Bilirubin_desc",
    "Direct_Bilirubin": "Direct_Bilirubin_desc",
    "Alkaline_Phosphotase": "Alkaline_Phosphotase_desc",
    "Alamine_Aminotransferase": "Alamine_Aminotransferase_desc",
    "Aspartate_Aminotransferase": "Aspartate_Aminotransferase_desc",
    "Total_Protiens": "Total_Protiens_desc",
    "Albumin": "Albumin_desc",
    "Albumin_and_Globulin_Ratio": "Albumin_and_Globulin_Ratio_desc"
}

# Load liver model at the start
liver_model = load_liver_model()

def show_disclaimer():
    with st.expander(t("⚠️ Medical Disclaimer"), expanded=True):
        st.markdown(t("medical_disclaimer_text"))

def show_parameter_info():
    with st.expander(t("📊 Parameter Information")):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(t("### Testing Parameters"))
            for param, desc in parameter_descriptions.items():
                st.markdown(f"**{param.replace('_', ' ')}**: {t(desc)}")
        
        with col2:
            st.markdown(t("### Normal Reference Ranges"))
            for param, range_info in reference_ranges.items():
                st.markdown(f"**{param.replace('_', ' ')}**: {range_info['normal']}")
def collect_patient_info():
    st.subheader(t("Patient Information"))
    col1, col2 = st.columns(2)

    if "patient_name" not in st.session_state:
        st.session_state["patient_name"] = None
    if "patient_gender" not in st.session_state:
        st.session_state["patient_gender"] = None
    if "patient_age" not in st.session_state:
        st.session_state["patient_age"] = None

    with col1:
        if not st.session_state["patient_name"]:
            name = st.text_input(t("Full Name"))
            gender_options = ["Male", "Female"]
            gender = st.selectbox(t("Gender"), gender_options)

            # Convert gender to int
            sex = 0 if gender == "Male" else 1

            if name:
                st.session_state["patient_name"] = name
                st.session_state["patient_gender"] = sex
        else:
            name = st.session_state["patient_name"]
            sex = st.session_state["patient_gender"]  # This might still be 'Male', fix below 👇
            
            # Ensure gender is an int
            if isinstance(sex, str):
                sex = 0 if sex == "Male" else 1
                st.session_state["patient_gender"] = sex
            
            st.info(f"👤 Name: {name}")
            st.info(f"🚻 Gender: {'Male' if sex == 0 else 'Female'}")

    with col2:
        if not st.session_state["patient_age"]:
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=30)
            if age:
                st.session_state["patient_age"] = age
        else:
            st.info(f"{t('🎂 Age')}: {st.session_state['patient_age']}")

    return st.session_state["patient_name"], st.session_state["patient_gender"], st.session_state["patient_age"]


def collect_lab_values():
    st.subheader(t("Laboratory Test Results"))
    st.caption(t("Enter your lab test results below. Hover over each parameter for information about normal ranges."))
    
    col1, col2 = st.columns(2)
    lab_values = {}
    
    # First column
    with col1:
        for param in list(reference_ranges.keys())[:4]:
            range_info = reference_ranges[param]
            display_name = param.replace('_', ' ')
            help_text = f"{t(parameter_descriptions[param])} {t('Normal range:')} {range_info['normal']}"
            key = f"lab_{param}"  # Unique key for session state
            
            # Use session state if exists, else use default
            default_value = st.session_state.get(key, float(range_info['min']))
            
            value = st.number_input(
                f"{display_name} ({range_info['unit']})",
                min_value=0.0,
                max_value=float(range_info['max']) * 10,
                value=default_value,
                help=help_text,
                key=key
            )

            lab_values[param] = value

            
            lab_values[param] = st.session_state[key]

            if lab_values[param] < range_info['min'] or lab_values[param] > range_info['max']:
                st.caption(f"{t('⚠️ Value outside normal range')} ({range_info['normal']})")
    
    # Second column
    with col2:
        for param in list(reference_ranges.keys())[4:]:
            range_info = reference_ranges[param]
            display_name = param.replace('_', ' ')
            help_text = f"{parameter_descriptions[param]} {t('Normal range:')} {range_info['normal']}"
            key = f"lab_{param}"
            default_value = st.session_state.get(key, float(range_info['min']))

            value = st.number_input(
                f"{display_name} ({range_info['unit']})",
                min_value=0.0,
                max_value=float(range_info['max']) * 10,
                value=default_value,
                help=help_text,
                key=key
            )

            lab_values[param] = value

            if lab_values[param] < range_info['min'] or lab_values[param] > range_info['max']:
                st.caption(f"{t('⚠️ Value outside normal range')} ({range_info['normal']})")
    
    return lab_values


def validate_inputs(name, lab_values):
    """Validate user inputs and return list of errors"""
    errors = []
    
    if not name:
        errors.append(t("Please enter your name"))
    
    # Check if any lab values are missing or zero
    for param, value in lab_values.items():
        if value <= 0:
            errors.append(f"{param.replace('_', ' ')} must be greater than zero")
    
    return errors

def make_prediction(sex, age, lab_values):
    """Process inputs and make prediction"""
    try:
        # Create input array for model
        model_input = [
            int(sex),
            int(age),
            float(lab_values["Total_Bilirubin"]),
            float(lab_values["Direct_Bilirubin"]),
            float(lab_values["Alkaline_Phosphotase"]),
            float(lab_values["Alamine_Aminotransferase"]),
            float(lab_values["Aspartate_Aminotransferase"]),
            float(lab_values["Total_Protiens"]),
            float(lab_values["Albumin"]),
           float( lab_values["Albumin_and_Globulin_Ratio"])
        ]
        
        # Make prediction
        prediction = liver_model.predict([model_input])
        probability = liver_model.predict_proba([model_input])
        print("Model Input:", model_input)
        print("Prediction:", prediction)
        print("Probabilities:", probability)
        print("Classes:", liver_model.classes_)

        return {
            "prediction": prediction[0],
            "probability": probability[0][liver_model.classes_.tolist().index(prediction[0])]
        }
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")
        return None

def display_result(prediction_result, name, lab_values):
    """Display prediction results"""
    if prediction_result is None:
        return
     # Set diagnosis and risk level in session state
    st.session_state["liver_diagnosis"] = "Liver Disease Risk Detected" if prediction_result["prediction"] == 2 and prediction_result["probability"]>0.5 else "No Liver Disease Risk"
    
    # Define risk level based on confidence/probability thresholds (customize thresholds as needed)
    prob = prediction_result["probability"]
    if prediction_result["prediction"] == 2:
        if prob > 1.8:
            risk_level = "High Risk"
        elif prob > 1.5:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"
    else:
        risk_level = "Low Risk"
    
    st.session_state["liver_risk_level"] = risk_level
    
    st.subheader(t("Prediction Result"))
    
    # Create a container with custom styling
    result_container = st.container()
    
    with result_container:
        if prediction_result["prediction"] == 2:
            st.error({t("⚠️ Liver Disease Risk Detected")})
            st.markdown(f"""
            {t('### Assessment for')} {name}
            
           {t('Based on the provided laboratory values, our model suggests a **higher risk of liver disease**')}
            ({t('Confidence')}: {prediction_result["probability"]:.2%}).
            
            {t('**Important Notice:**')}
            {t('- This is not a diagnosis, but a risk assessment based on your test results')}
            {t('- Please consult with a hepatologist or gastroenterologist for proper evaluation')}
            {t('- Further diagnostic tests may be needed to confirm any liver condition')}
            """)
            
            # Highlight concerning values
            concerning_values = []
            for param, value in lab_values.items():
                range_info = reference_ranges[param]
                if value < range_info['min'] or value > range_info['max']:
                    concerning_values.append({
                        "Parameter": param.replace('_', ' '),
                        "Your Value": f"{value} {range_info['unit']}",
                        "Normal Range": range_info['normal']
                    })
            
            if concerning_values:
                st.markdown(t("### Concerning Laboratory Values"))
                st.table(pd.DataFrame(concerning_values))
        else:
            st.success(t("✅ No Liver Disease Risk Detected"))
            st.markdown(f"""
           {t('### Assessment for')} {name}
            
           {t('Based on the provided laboratory values, our model suggests a **low risk of liver disease**')}
            ({t('Confidence')}: {prediction_result["probability"]:.2%}).
            
            {t('**Recommendations:**')}
            {t('- Continue with regular health check-ups')}
            {t('- Maintain a healthy lifestyle with proper diet and exercise')}
            {t('- Limit alcohol consumption')}
            {t('- Stay hydrated and maintain a balanced diet')}
            """)
        
        # Add to history
        diagnosis_record = {
            "name": name,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "result": "Higher Risk" if prediction_result["prediction"] == 1 else "Low Risk",
            "confidence": f"{prediction_result['probability']:.2%}"
        }
        
        st.session_state.diagnoses_history.append(diagnosis_record)

def show_history():
    """Display diagnosis history"""
    if st.session_state.diagnoses_history:
        with st.expander(t("📜 Previous Assessments")):
            st.table(pd.DataFrame(st.session_state.diagnoses_history))

def run():
    page_title=t("🩺 Liver Disease Risk Assessment Tool")
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
    st.markdown("""
    This application uses machine learning to assess the risk of liver disease based on laboratory test results.
    Enter your information and lab values below to receive an assessment.
    """)
    
    # Show disclaimer
    show_disclaimer()
    
    # Tabs for different sections
    tab1, tab2 = st.tabs([t("Assessment"), t("Information")])
    
    with tab1:
        # Collect patient information
        name, sex, age = collect_patient_info()
        # Show parameter information
        show_parameter_info()
        
        # Collect lab values
        lab_values = collect_lab_values()
        
        # Form submission
        if st.button(t("🔍 Predict"), type="primary"):
            # Validate inputs
            errors = validate_inputs(name, lab_values)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Make prediction
                prediction_result = make_prediction(sex, age, lab_values)
                
                if prediction_result:
                    # Display result
                    display_result(prediction_result, name, lab_values)
                    
                    # Show history
                    show_history()
    
    with tab2:
        st.header(t("Understanding Liver Function Tests"))
        st.markdown(t("liver_info_markdown"))

if __name__ == "__main__":
    run()