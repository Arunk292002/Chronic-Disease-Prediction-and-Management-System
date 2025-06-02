import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from core.helper import t

def run():
    page_title=t("🌡️ Fever Detection & Recommendations")
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

    st.warning(t("⚠️ **MEDICAL DISCLAIMER**: This tool provides general guidance only and is not a substitute for professional medical advice. Always consult a healthcare provider for medical concerns."))

    # Centered radio button
    st.markdown("###")
    temp_col = st.columns([1, 3, 1])[1]
    temp_unit = st.radio(t("Select Temperature Unit:"), ["Celsius (°C)", "Fahrenheit (°F)"], horizontal=True)

    st.markdown("---")

    try:
        file_path = os.path.join("data", "enhanced_fever_medicine_recommendation.csv")
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip().str.lower()
        except FileNotFoundError:
            st.error(f"❌ File not found at {file_path}")
            df = pd.DataFrame(columns=["fever_severity", "recommended_medication"])
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            df = pd.DataFrame(columns=["fever_severity", "recommended_medication"])

        if "temperature" in st.session_state and "temp_unit" in st.session_state:
            original_temp = st.session_state["temperature"]
            original_unit = st.session_state["temp_unit"]

            if original_unit != temp_unit:
                if original_unit == "Fahrenheit (°F)" and temp_unit == "Celsius (°C)":
                    temperature = (original_temp - 32) * 5/9
                elif original_unit == "Celsius (°C)" and temp_unit == "Fahrenheit (°F)":
                    temperature = (original_temp * 9/5) + 32
                else:
                    temperature = original_temp
            else:
                temperature = original_temp

            st.success(f"{t('✅ Temperature from Home Section')}: {temperature:.1f} {temp_unit[:-4]}")
        else:
            if temp_unit == "Celsius (°C)":
                temperature = st.number_input(t("🌡️ Enter your Temperature (°C):"), 30.0, 45.0, 37.0, 0.1)
            else:
                temperature = st.number_input(t("🌡️ Enter your Temperature (°F):"), 86.0, 113.0, 98.6, 0.1)

        st.session_state["temperature"] = temperature
        st.session_state["temp_unit"] = temp_unit
        temp_celsius = (temperature - 32) * 5/9 if temp_unit == "Fahrenheit (°F)" else temperature

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            age = st.session_state.get("age") or st.number_input(t("🎂 Age"), 0, 120, 25)
            chronic_conditions = st.selectbox(t("🩺 Do you have chronic conditions?"), ["No", "Yes", "Yes, Heart Disease", "Yes, Diabetes", "Yes, Other"])
        with col2:
            bmi = st.session_state.get("bmi") or st.number_input("⚖️ BMI", 10.0, 50.0, 22.0)
            pregnancy_status = st.selectbox(t("🤰 Are you pregnant?"), ["No / Not Applicable", "Yes"])

        st.markdown("---")

        if age <= 3:
            normal_range_c = "36.6°C - 37.2°C"
            normal_range_f = "97.9°F - 99.0°F"
        elif age <= 10:
            normal_range_c = "36.5°C - 37.5°C"
            normal_range_f = "97.7°F - 99.5°F"
        else:
            normal_range_c = "36.1°C - 37.2°C"
            normal_range_f = "97.0°F - 99.0°F"
        st.info(f"{t('ℹ️ Normal temperature range for your age')}: {normal_range_c} / {normal_range_f}")

        severity = ""
        emergency = False

        if age <= 3:
            if temp_celsius >= 38.9:
                severity, emergency = "High", True
            elif 38.0 <= temp_celsius < 38.9:
                severity = "Moderate"
            elif 37.2 < temp_celsius < 38.0:
                severity = "Low"
            elif 36.6 <= temp_celsius <= 37.2:
                severity = "None"
            else:
                severity = "Below Normal"
        elif age <= 10:
            if temp_celsius >= 39.4:
                severity, emergency = "High", True
            elif 38.0 <= temp_celsius < 39.4:
                severity = "Moderate"
            elif 37.5 < temp_celsius < 38.0:
                severity = "Low"
            elif 36.5 <= temp_celsius <= 37.5:
                severity = "None"
            else:
                severity = "Below Normal"
        else:
            if temp_celsius >= 39.0:
                severity = "High"
                if age >= 65:
                    emergency = True
            elif 37.5 <= temp_celsius < 39.0:
                severity = "Moderate"
            elif 37.2 < temp_celsius < 37.5:
                severity = "Low"
            elif 36.1 <= temp_celsius <= 37.2:
                severity = "None"
            else:
                severity = "Below Normal"

        st.markdown("---")

        if severity == "High":
            st.error(f"🔴 Fever Severity: `{severity}`")
        elif severity == "Moderate":
            st.warning(f"🟠 Fever Severity: `{severity}`")
        elif severity == "Low":
            st.info(f"🟡 Fever Severity: `{severity}`")
        elif severity == "None":
            st.success(t("🟢 Normal Temperature"))
        else:
            st.info(t(f"🔵 Status: `{severity}`"))

        # Optional: progress bar (scaled)
        severity_scale = {"None": 0, "Low": 1, "Moderate": 2, "High": 3}
        st.progress(severity_scale.get(severity, 0) / 3)

        if emergency:
            st.error(t("🚨 **EMERGENCY:** High fever at your age group needs urgent attention."))
        if age <= 3 and temp_celsius >= 38.0:
            st.error(t("🚼 **Infant Alert:** Fevers in toddlers require pediatric consultation."))
        if pregnancy_status == "Yes" and temp_celsius >= 38.0:
            st.error(t("🤰 **Pregnancy Alert:** Contact your obstetrician immediately."))
        if chronic_conditions == "Yes" and severity in ["Moderate", "High"]:
            st.error(t("⚠️ **Chronic Condition Alert:** Please consult your doctor."))

        if severity not in ["None", "Below Normal"]:
            match = df[df["fever_severity"].str.lower() == severity.lower()]
            if not match.empty:
                med = match["recommended_medication"].mode()[0]
                med_lower = med.lower()
                if "acetaminophen" in med_lower or "paracetamol" in med_lower:
                    dosage = "Child: weight-based. Adult: 500–1000mg every 4–6h, max 4g/day."
                elif "ibuprofen" in med_lower:
                    dosage = "Child: weight-based. Adult: 200–400mg every 4–6h, max 1.2g/day."
                else:
                    dosage = "Check label or consult doctor."
                st.success(f"{t('💊 Recommended Medication')}: **{med}**")
                with st.expander(t("📋 Dosage Information")):
                    st.write(t(dosage))
                st.warning(t("⚠️ Always follow label instructions. Avoid self-medication during pregnancy or chronic illness."))

            st.subheader(t("🌡️ Fever Care Tips"))
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(t("""
                ✅ **Rest** 🛌  
                ✅ **Hydrate** 💧  
                ✅ **Light clothing** 👕  
                ✅ **Lukewarm sponge bath** 🧽  
                ✅ **Monitor temperature** 📈
                """))
            with col2:
                st.markdown(t("""
                ❌ Ice baths  
                ❌ Alcohol rubs  
                ❌ Double dosing  
                ❌ Ignoring symptoms  
                ❌ Skipping meals
                """))

            st.subheader(t("🚨 Emergency Symptoms – Seek Care If:"))
            st.error(t("""
            - 🌡️ Temp > 103°F (39.4°C)  
            - 😖 Stiff neck or headache  
            - 😤 Breathing difficulty  
            - 😵 Confusion or drowsiness  
            - ⚡ Seizures  
            - 🤢 Severe rash or vomiting
            """))

        elif severity == "Below Normal":
            st.warning(t("""
            🧊 Temperature is unusually low. Could be cold exposure or underlying condition.
            Consult a healthcare provider if concerned.
            """))
        else:
            st.success(t("✅ No fever detected. You're good!"))

        st.markdown(t("For more information, visit [CDC Fever Guidelines](https://www.cdc.gov/fever-guidelines)."))

    except Exception as e:
        st.error(f"{t('An error occurred')}: {str(e)}")
        st.info(t("Please refresh the page and try again."))