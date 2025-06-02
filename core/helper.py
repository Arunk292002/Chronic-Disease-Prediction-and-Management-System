import streamlit as st
import pandas as pd
import re
import json
import io
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
from googletrans import Translator

COMMON_ILLNESS_PATTERNS = {
    'Common Cold': {
        'symptoms': ['Cough', 'Fever', 'Fatigue', 'Headache'],
        'min_symptoms': 2,  # Minimum symptoms needed to suggest this pattern
        'typical_duration': (3, 10),  # Days (min, max)
        'severity_pattern': {'Mild': 2, 'Moderate': 1, 'Severe': 0},  # Expected severity distribution
        'description': 'Usually starts with sore throat, followed by nasal symptoms and cough. Typically improves within 7-10 days.',
        'recommendations': [
            'Rest and stay hydrated',
            'Over-the-counter cold medications may help relieve symptoms',
            'Humidifier can ease congestion and sore throat'
        ]
    },
    'Seasonal Allergies': {
        'symptoms': ['Cough', 'Fatigue', 'Shortness of Breath'],
        'min_symptoms': 2,
        'typical_duration': (7, 60),
        'severity_pattern': {'Mild': 3, 'Moderate': 1, 'Severe': 0},
        'description': 'Symptoms often include itchy eyes, runny nose, and sneezing. May worsen during specific seasons.',
        'recommendations': [
            'Avoid known allergens when possible',
            'Consider over-the-counter antihistamines',
            'Keep windows closed during high pollen seasons'
        ]
    },
    'Influenza': {
        'symptoms': ['Fever', 'Fatigue', 'Headache', 'Chest Pain', 'Shortness of Breath'],
        'min_symptoms': 3,
        'typical_duration': (5, 14),
        'severity_pattern': {'Mild': 0, 'Moderate': 2, 'Severe': 2},
        'description': 'Usually begins suddenly with fever, muscle aches, and exhaustion. More severe than common cold.',
        'recommendations': [
            'Rest and stay hydrated',
            'Consult a doctor, especially if symptoms are severe',
            'Consider antiviral medications if diagnosed early',
            'Avoid contact with others to prevent spread'
        ]
    },
    'Gastroenteritis': {
        'symptoms': ['Nausea', 'Fatigue'],
        'min_symptoms': 2,
        'typical_duration': (1, 5),
        'severity_pattern': {'Mild': 1, 'Moderate': 2, 'Severe': 1},
        'description': 'Often includes stomach cramps, vomiting, and diarrhea. Usually resolves within a few days.',
        'recommendations': [
            'Stay hydrated with small, frequent sips of water',
            'Gradually reintroduce bland foods as symptoms improve',
            'Seek medical attention if unable to keep fluids down or signs of dehydration'
        ]
    },
    'COVID-19': {
        'symptoms': ['Fever', 'Cough', 'Fatigue', 'Shortness of Breath', 'Headache', 'Nausea'],
        'min_symptoms': 3,
        'typical_duration': (7, 21),
        'severity_pattern': {'Mild': 1, 'Moderate': 2, 'Severe': 1},
        'description': 'Symptoms vary widely, may include loss of taste/smell. Can range from mild to severe.',
        'recommendations': [
            'Isolate to prevent spread to others',
            'Consider getting tested for COVID-19',
            'Monitor oxygen levels if possible',
            'Seek immediate medical attention for severe symptoms'
        ]
    },
    'Migraine': {
        'symptoms': ['Headache', 'Nausea'],
        'min_symptoms': 2,
        'typical_duration': (0.5, 3),
        'severity_pattern': {'Mild': 0, 'Moderate': 1, 'Severe': 2},
        'description': 'Typically includes throbbing headache, often on one side, sometimes with light/sound sensitivity.',
        'recommendations': [
            'Rest in a dark, quiet room',
            'Apply cold compresses to the forehead',
            'Consider over-the-counter pain relievers',
            'Track triggers to prevent future attacks'
        ]
    }
}

strength_label = ["Very Weak", "Weak", "Moderate", "Strong", "Very Strong"]
bar_color = ["#FF4B4B", "#FF884B", "#FFD93D", "#2ECC71", "#27AE60"]

# Function to create the input datafram
def create_input_df(user_inputs, category_map):
    # Transform categorical inputs using category_map
    for category in category_map:
        if category in user_inputs:
            user_inputs[category] = category_map[category].get(user_inputs[category], -1)  # -1 or other value for missing/unknown categories
    input_df = pd.DataFrame([user_inputs])
    return input_df

with open("translation.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

def t(key):
    lang = st.session_state.get("language", "English")
    return translations.get(key, {}).get(lang, key)

translator = Translator()

def translate_text(text, dest_language="ta"):  # 'ta' for Tamil
    try:
        translation = translator.translate(text, dest=dest_language)
        return translation.text
    except Exception as e:
        return text

def suggest_email_correction(email):
    common_domains = {
        "gmial.com": "gmail.com",
        "gnail.com": "gmail.com",
        "gamil.com": "gmail.com",
        "gmaill.com": "gmail.com",
        "yaho.com": "yahoo.com",
        "yahho.com": "yahoo.com",
        "hotnail.com": "hotmail.com",
        "hotmai.com": "hotmail.com",
        "outlok.com": "outlook.com"
    }

    if "@" in email:
        local, domain = email.split("@")
        corrected_domain = common_domains.get(domain.lower())
        if corrected_domain:
            return f"{local}@{corrected_domain}"
    return None

def check_password_strength(password):
    score = 0

    # Rules
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[\W_]", password):  # symbols
        score += 1

    return score

def calculate_risk_score():
    score = 0

    # Blood Pressure
    if st.session_state.get("blood_pressure", 0) < 90 or st.session_state.get("blood_pressure", 0) > 140:
        score += 20

    # Heart Rate
    if st.session_state.get("heart_rate", 0) < 60 or st.session_state.get("heart_rate", 0) > 100:
        score += 20

    # Blood Sugar
    if st.session_state.get("blood_sugar", 0) < 70 or st.session_state.get("blood_sugar", 0) > 140:
        score += 20

    # Diabetes prediction
    if st.session_state.get("diabetes_diagnosis", "") == "the patient has diabetes":
        score += 20

    # Heart disease prediction
    if st.session_state.get("heart_diagnosis", "") == 1:
        score += 20

    # Kidney disease prediction
    if st.session_state.get("kidney_diagnosis", "").lower().startswith("the patient is likely to have"):
        score += 20

    # Fever
    if st.session_state.get("temperature", 0) >= 38.0:
        score += 20

    # BMI
    bmi = st.session_state.get("bmi")
    if bmi:
        if bmi < 18.5:
            score += 10
        elif 25 <= bmi < 30:
            score += 10
        elif bmi >= 30:
            score += 20

    return min(score, 100)  # Max 100

def clean_text_for_pdf(text):
    return text.encode('latin-1', 'ignore').decode('latin-1')


def classify_blood_pressure(systolic, diastolic, age, gender, has_heart_disease, avg_glucose, bmi, smoking_status):
    # Blood pressure categories based on current readings
    if systolic > 180 or diastolic > 120:
        return t("Hypertension Crisis"), "🔴", t("Hypertension Crisis Advice")
    elif systolic >= 140 or diastolic >= 90:
        return t("Stage 2 Hypertension"), "🟥", t("Stage 2 Hypertension Advice")
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return t("Stage 1 Hypertension"), "🟧",t( "Stage 1 Hypertension Advice")
    elif 120 <= systolic <= 129 and diastolic < 80:
        return t("Elevated"), "🟨", t("Elevated Advice")
    elif systolic < 120 and diastolic < 80:
        return t("Healthy"), "🟩", t("Healthy Advice")
    
    # Additional context-based classifications
    if age > 60:
        if systolic < 130 and diastolic < 80:
            return t("Normal (Older Adult)"), "🟩", t("Normal (Older Adult) Advice")
        elif systolic >= 130 or diastolic >= 80:
            return t("Age-related Hypertension Risk"), "🟧", t("Age-related Hypertension Risk Advice")

    if has_heart_disease:
        if systolic >= 130 or diastolic >= 80:
            return t("Hypertension Risk with Heart Disease"), "🟥", t("Hypertension Risk with Heart Disease Advice")

    if smoking_status == "smokes" or smoking_status == "formerly smoked":
        if systolic >= 130 or diastolic >= 80:
            return t("Hypertension Risk due to Smoking"), "🟥", t("Hypertension Risk due to Smoking Advice")

    if gender == "Female" and age < 40:
        if systolic >= 120 or diastolic >= 80:
            return t("Hypertension Risk for Young Women"), "🟧", t("Hypertension Risk for Young Women Advice")

    if avg_glucose > 100 and bmi > 30:
        if systolic >= 130 or diastolic >= 80:
            return t("Hypertension Risk with Diabetes and Obesity"), "🟥", t("Hypertension Risk with Diabetes and Obesity Advice")

    # If none of the above conditions match
    return t("Unclassified"), "⚠️", t("Unclassified Advice")
    
# 🚑 Check if patient needs appointment
def needs_appointment():
    if (st.session_state.get("blood_pressure", 0) < 90 or st.session_state.get("blood_pressure", 0) > 140):
        return True
    if (st.session_state.get("heart_rate", 0) < 60 or st.session_state.get("heart_rate", 0) > 100):
        return True
    if (st.session_state.get("blood_sugar", 0) < 70 or st.session_state.get("blood_sugar", 0) > 140):
        return True
    if (st.session_state.get("temperature", 0) > 38.0):
        return True
    if st.session_state.get("diabetes_diagnosis", "").lower() == "the patient has diabetes":
        return True
    if st.session_state.get("heart_diagnosis", "")== 1:
        return True
    if st.session_state.get("kidney_diagnosis", "").lower().startswith("the patient is likely to have"):
        return True
    return False

def analyze_symptom_patterns(symptom_log):
    """
    Analyze symptom log for patterns that match common illnesses
    Returns a list of possible conditions with confidence levels
    """
    if symptom_log.empty:
        return []
    
    # Convert dates from string to datetime if needed
    if isinstance(symptom_log['Date'].iloc[0], str):
        symptom_log['Date'] = pd.to_datetime(symptom_log['Date'])
    
    # Sort by date
    symptom_log = symptom_log.sort_values('Date')
    
    # Get unique dates to calculate duration
    unique_dates = symptom_log['Date'].unique()
    duration_days = (max(unique_dates) - min(unique_dates)).days + 1
    
    # Get list of all symptoms and their severities
    all_symptoms = symptom_log['Symptom'].tolist()
    symptom_count = Counter(all_symptoms)
    
    # Count severity levels
    severity_counts = Counter(symptom_log['Severity'].tolist())
    
    # Calculate the frequency of symptoms over time for progression analysis
    symptom_progression = {}
    for symptom in set(all_symptoms):
        symptom_dates = symptom_log[symptom_log['Symptom'] == symptom]['Date'].tolist()
        symptom_progression[symptom] = symptom_dates
    
    # Analyze matches with known patterns
    matches = []
    
    for illness, pattern in COMMON_ILLNESS_PATTERNS.items():
        # Calculate how many symptoms match
        matching_symptoms = [s for s in pattern['symptoms'] if s in symptom_count]
        symptom_match_ratio = len(matching_symptoms) / len(pattern['symptoms'])
        
        # Check if minimum number of symptoms are present
        if len(matching_symptoms) < pattern['min_symptoms']:
            continue
            
        # Check duration match (if we have enough data points)
        if len(unique_dates) > 1:
            min_duration, max_duration = pattern['typical_duration']
            duration_match = min_duration <= duration_days <= max_duration
            # Calculate how well the duration matches
            if duration_days < min_duration:
                duration_score = duration_days / min_duration
            elif duration_days > max_duration:
                duration_score = max_duration / duration_days
            else:
                duration_score = 1.0
        else:
            # Not enough data points to determine duration
            duration_score = 0.5  # Neutral score
            duration_match = None
            
        # Check severity pattern match
        severity_match_score = 0
        expected_total = sum(pattern['severity_pattern'].values())
        if expected_total > 0:
            for severity, expected_count in pattern['severity_pattern'].items():
                actual_count = severity_counts.get(severity, 0)
                # Calculate proportion of expected vs actual
                if expected_count > 0:
                    severity_match_score += min(actual_count / expected_count, 1.0) * (expected_count / expected_total)
        else:
            severity_match_score = 0.5  # Neutral score
            
        # Calculate overall confidence score (weighted average)
        confidence = (
            symptom_match_ratio * 0.60 +  # Symptom matching is most important
            duration_score * 0.25 +        # Duration is somewhat important
            severity_match_score * 0.15    # Severity pattern is least important
        ) * 100  # Convert to percentage
            
        if confidence >= 40:  # Only include somewhat confident matches
            matches.append({
                'illness': illness,
                'confidence': confidence,
                'matching_symptoms': matching_symptoms,
                'missing_symptoms': [s for s in pattern['symptoms'] if s not in symptom_count],
                'duration_match': duration_match,
                'description': pattern['description'],
                'recommendations': pattern['recommendations']
            })
    
    # Sort by confidence (highest first)
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    return matches

def get_symptom_progression_chart(symptom_log):
    """Generate a chart showing symptom progression over time using matplotlib"""
    if symptom_log.empty:
        return None

    # Convert date column to datetime
    symptom_log['Date'] = pd.to_datetime(symptom_log['Date'])

    # Map severity to numeric values for visualization
    severity_map = {'Mild': 1, 'Moderate': 2, 'Severe': 3}
    symptom_log['SeverityValue'] = symptom_log['Severity'].map(severity_map)

    # Create a pivot for plotting
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot each symptom individually
    for symptom in symptom_log['Symptom'].unique():
        symptom_data = symptom_log[symptom_log['Symptom'] == symptom]
        ax.scatter(symptom_data['Date'], [symptom] * len(symptom_data), 
                   s=symptom_data['SeverityValue'] * 60,  # Size by severity
                   label=symptom,
                   alpha=0.6,
                   edgecolors='k')

    ax.set_title("Symptom Progression Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Symptom")
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.0))
    plt.tight_layout()

    # Convert to image to display in Streamlit
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)

    # Clear the figure to avoid Streamlit duplication
    plt.close(fig)

    return img

def analyze_and_display_patterns(symptom_log):
    """Analyze symptom patterns and display results in the Streamlit app"""
    st.subheader("🔍 Pattern Recognition Analysis")
    
    if symptom_log.empty:
        st.info("No symptoms have been logged yet. Please log your symptoms to see pattern analysis.")
        return
        
    # Add a chart showing symptom progression
    chart = get_symptom_progression_chart(symptom_log)
    if chart:
        st.image(chart, use_container_width=True)
    
    # Get pattern matches
    matches = analyze_symptom_patterns(symptom_log)
    
    if not matches:
        st.info("No clear illness patterns detected from the logged symptoms. Continue tracking for better analysis.")
        return
        
    # Display potential illness matches
    st.subheader("🔬 Potential Illness Patterns Detected")
    st.markdown("*Note: This is not a medical diagnosis. Please consult a healthcare professional.*")
    
    for match in matches:
        confidence_color = "#5cb85c" if match['confidence'] >= 70 else "#f0ad4e" if match['confidence'] >= 50 else "#d9534f"
        
        with st.expander(f"{match['illness']} - Confidence: {match['confidence']:.1f}%"):
            st.markdown(f"""
            <div style="padding: 10px; border-left: 5px solid {confidence_color};">
                <p><strong>Description:</strong> {match['description']}</p>
                <p><strong>Matching symptoms:</strong> {', '.join(match['matching_symptoms'])}</p>
                <p><strong>Missing symptoms to watch for:</strong> {', '.join(match['missing_symptoms']) if match['missing_symptoms'] else 'None'}</p>
                <p><strong>Typical duration:</strong> {COMMON_ILLNESS_PATTERNS[match['illness']]['typical_duration'][0]}-{COMMON_ILLNESS_PATTERNS[match['illness']]['typical_duration'][1]} days</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("Recommendations:")
            for i, recommendation in enumerate(match['recommendations'], 1):
                st.markdown(f"{i}. {recommendation}")
            
            # Add action button for top matches
            if match['confidence'] >= 60:
                if st.button(f"Schedule Appointment (Based on {match['illness']} Pattern)", key=f"appt_{match['illness']}"):
                    st.session_state['appointment_reason'] = f"Possible {match['illness']} - Symptoms: {', '.join(match['matching_symptoms'])}"
                    st.success("✅ Appointment reason saved. Please go to the Home page to complete scheduling.")

def suggest_next_health_actions(symptom_log, matches):
    """Suggest next health actions based on symptom analysis"""
    st.subheader("📋 Suggested Next Steps")
    
    if not symptom_log.empty and matches:
        top_match = matches[0]
        
        # Determine urgency level
        urgent_symptoms = ['Chest Pain', 'Shortness of Breath', 'Severe Headache']
        has_urgent_symptoms = any(symptom in urgent_symptoms for symptom in symptom_log['Symptom'].unique())
        severe_symptoms = symptom_log[symptom_log['Severity'] == 'Severe']['Symptom'].tolist()
        
        if has_urgent_symptoms or (severe_symptoms and top_match['confidence'] > 60):
            st.error("⚠️ **Urgent Attention Recommended**: Based on your symptoms, we recommend seeking medical attention promptly.")
            st.markdown("### Why this is urgent:")
            if has_urgent_symptoms:
                urgent_found = [s for s in urgent_symptoms if s in symptom_log['Symptom'].unique()]
                st.markdown(f"- You reported {', '.join(urgent_found)}, which may require immediate evaluation")
            if severe_symptoms:
                st.markdown(f"- You rated these symptoms as severe: {', '.join(severe_symptoms)}")
                
        elif top_match['confidence'] > 70:
            st.warning(f"**Recommended Action**: Based on the pattern matching {top_match['illness']}, consider the following:")
            for rec in top_match['recommendations']:
                st.markdown(f"- {rec}")
        else:
            st.info("**Recommended Action**: Continue monitoring your symptoms and update the tracker daily.")
            
        # Suggest symptom tracking focus
        if top_match['missing_symptoms']:
            st.markdown("### Symptoms to watch for:")
            for symptom in top_match['missing_symptoms']:
                st.markdown(f"- {symptom}")
    else:
        st.info("Continue logging your symptoms daily for better pattern recognition.")