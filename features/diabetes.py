import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from code.meal_planner import get_personalized_meal_plan
from core.models import load_models
from core.helper import t

models=load_models()
model_diabetes=models['diabetes']

def validate_inputs(input_data):
    errors = []

    # Specific validation rules
    validations = [
        ('Pregnancies', lambda x: x >= 0, t("Pregnancies cannot be negative")),
        ('Glucose', lambda x: x > 0, t("Glucose must be a positive value")),
        ('BloodPressure', lambda x: x >= 0, t("Blood Pressure cannot be negative")),
        ('SkinThickness', lambda x: x >= 0, t("Skin Thickness cannot be negative")),
        ('Insulin', lambda x: x >= 0, t("Insulin cannot be negative")),
        ('BMI', lambda x: x > 0, t("BMI must be a positive value")),
        ('DiabetesPedigreeFunction', lambda x: 0 <= x <= 1, t("Diabetes Pedigree Function must be between 0 and 1")),
        ('Age', lambda x: x > 0, t("Age must be a positive value"))
    ]

    # Ensure you're validating scalar values
    for param, validation_func, error_msg in validations:
        value = input_data[param].iloc[0] if isinstance(input_data, pd.DataFrame) else input_data[param]
        if not validation_func(value):
            errors.append(error_msg)

    return errors
def analyze_diabetes_risk(prediction, input_data):
    # Safely extract scalar values from DataFrame
    glucose = input_data['Glucose'].iloc[0]
    bmi = input_data['BMI'].iloc[0]
    blood_pressure = input_data['BloodPressure'].iloc[0]
    age = input_data['Age'].iloc[0]
    pregnancies = input_data['Pregnancies'].iloc[0]
    insulin = input_data['Insulin'].iloc[0]
    dpf = input_data['DiabetesPedigreeFunction'].iloc[0]

    # Define risk thresholds
    risk_thresholds = [
        (glucose > 125, t("High Glucose Level")),
        (bmi > 30, t("Obesity")),
        (blood_pressure > 130, t("High Blood Pressure")),
        (age > 45, t("Age-related Risk")),
        (pregnancies > 3, t("Multiple Pregnancies")),
        (insulin > 100, t("High Insulin Level")),
        (dpf > 0.5, t("Strong Family History"))
    ]

    # Collect identified risk factors
    risk_factors = [msg for condition, msg in risk_thresholds if condition]

    return {
        'prediction': prediction,
        'risk_factors': risk_factors,
        'risk_score': len(risk_factors)
    }

def run():
    page_title=t("🩺 Diabetes Prediction Test")
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
    # Create input columns
    col1, col2 = st.columns(2)
    
    # Input collection with enhanced guidance
    with col1:
        Pregnancies = st.number_input(
            t('Number of Pregnancies'), 
            min_value=0, 
            help=t("Total number of pregnancies (0 if never pregnant)")
        )
        Glucose = st.number_input(
            t('Glucose Level'), 
            min_value=0, 
            help=t("Plasma glucose concentration (mg/dL). Normal is 70-100 mg/dL")
        )
        BloodPressure = st.number_input(
            t('Blood Pressure'), 
            min_value=0, 
            help=t("Diastolic blood pressure (mm Hg). Normal is below 120/80")
        )
        Insulin = st.number_input(
            t('Insulin Level'), 
            min_value=0, 
            help=t("2-Hour serum insulin (mu U/ml). Normal is 16-166 mu U/ml")
        )
    
    with col2:
        SkinThickness = st.number_input(
            t('Skin Thickness'), 
            min_value=0, 
            help=t("Triceps skin fold thickness (mm)")
        )
        BMI = st.number_input(
            t('Body Mass Index (BMI)'), 
            min_value=0.0, 
            format="%.1f", 
            help=t("Body mass index. Healthy range is 18.5-24.9")
        )
        DiabetesPedigreeFunction = st.number_input(
            t('Diabetes Pedigree Function'), 
            min_value=0.0, 
            max_value=1.0, 
            format="%.3f", 
            help=t("Diabetes genetic likelihood. Higher values indicate greater risk")
        )
        Age = st.number_input(
            t('Age'), 
            min_value=0, 
            help=t("Age of the patient in years")
        )
    
    # Prediction button
    if st.button(t('🔍 Predict')):
        # Prepare input data dictionary
        input_data = {
            'Pregnancies': Pregnancies,
            'Glucose': Glucose,
            'BloodPressure': BloodPressure,
            'SkinThickness': SkinThickness,
            'Insulin': Insulin,
            'BMI': BMI,
            'DiabetesPedigreeFunction': DiabetesPedigreeFunction,
            'Age': Age
        }
        st.session_state['diabetes_inputs']={
            'Pregnancies': Pregnancies,
            'Glucose': Glucose,
            'Skin Thickness': SkinThickness,
            'Insulin': Insulin,
            'Diabetes Pedigree Function': DiabetesPedigreeFunction
        }
        with st.spinner(t("🧠 Analyzing your data...")):
            input_data = pd.DataFrame([[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                                        BMI, DiabetesPedigreeFunction, Age]],
                                    columns=["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                                            "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"])
            prediction = model_diabetes.predict(input_data)[0]
        
            # Validate inputs
            input_errors = validate_inputs(input_data)
            
            if input_errors:
                # Display validation errors
                for error in input_errors:
                    st.error(error)
                return
            
            # Analyze prediction
            analysis = analyze_diabetes_risk(prediction, input_data)
            
            # Display results with risk analysis
            if analysis['prediction'] == 1:
                st.error(t("⚠️ Diabetes Risk Detected"))
                st.markdown(t("### Risk Factors Identified:"))
                for factor in analysis['risk_factors']:
                    st.warning(f"- {factor}")
                
                # Additional risk score visualization
                risk_percentage = min(analysis['risk_score'] * 20, 100)  # Convert to percentage
                st.progress(risk_percentage)
                st.markdown(f"**Risk Score:** {risk_percentage}%")
            else:
                st.success(t("✅ Low Diabetes Risk"))
        
        # Store in session state
        st.session_state["diabetes_diagnosis"] = analysis
        st.session_state['show_meal_plan'] = True 
        
        # Personalized Meal Plan
        if st.session_state.get('show_meal_plan', False):
            st.subheader(t("🍽 Personalized Meal Plan"))
            # You can modify the get_personalized_meal_plan function to use the risk analysis
            meal_plan = get_personalized_meal_plan(
                glucose=Glucose, 
                bmi=BMI, 
            )

            for meal_time, meals in meal_plan.items():
                st.markdown(f"### {meal_time}")
                for meal in meals:
                    st.markdown(f"- {meal['name']} | {meal['Calories']} kcal | {meal['Fibre']}g Fiber | {meal['Sugars']}g Sugar")
                st.markdown("---")