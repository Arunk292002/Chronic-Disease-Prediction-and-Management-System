# features/home.py
import streamlit as st
import urllib.parse
import pandas as pd
import plotly.express as px
import datetime
import os
from core.pdf_report import generate_pdf
from core.helper import calculate_risk_score, t
from core.location import geocode_address, get_nearby_hospitals,validate_address,reverse_geocode_osm, generate_google_maps_directions_link

@st.cache_data
def get_cached_reverse_address(lat, lon):
    return reverse_geocode_osm(lat, lon)

def generate_google_maps_search_link(address):
    """
    Generate a Google Maps search link based on the hospital address.
    
    Args:
        address (str): Full address of the hospital
    
    Returns:
        str: Google Maps search URL
    """
    # URL encode the address
    encoded_address = urllib.parse.quote(address)
    
    # Generate Google Maps search URL
    return f"https://www.google.com/maps/search/?api=1&query={encoded_address}"

def enhance_hospital_data(hospitals):
    """
    Enhance hospital data with Google Maps search links using full address
    
    Args:
        hospitals (list): List of hospital dictionaries
    
    Returns:
        list: Enhanced hospital dictionaries with Google Maps search link
    """
    for hospital in hospitals:
        # Get the hospital's full address using reverse geocoding
        full_address = get_cached_reverse_address(hospital['lat'], hospital['lon'])
        
        # Add Google Maps search link using the full address
        hospital['google_maps_link'] = generate_google_maps_search_link(full_address)
    
    return hospitals

def run():
    st.subheader(t("👤 Patient Details"))
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input(t("Patient Name"))
        patient_age = st.number_input(t("Age"), min_value=1, max_value=120)
    with col2:
        patient_gender = st.selectbox(t("Gender"), [t("Male"), t("Female"), t("Other")])

    st.divider()
    st.session_state["patient_name"]=patient_name
    st.session_state["patient_age"]=patient_age
    st.session_state["patient_gender"]=patient_gender
    st.subheader(t("Enter Your Health Data"))
    st.session_state["blood_pressure"] = st.number_input(t("Blood Pressure (mmHg)"), min_value=50, max_value=200, step=1)
    st.session_state["heart_rate"] = st.number_input(t("Heart Rate (bpm)"), min_value=30, max_value=200, step=1)
    st.session_state["blood_sugar"] = st.number_input(t("Blood Sugar Level (mg/dL)"), min_value=50, max_value=500, step=1)
    st.session_state["temperature"] = st.number_input(t("Body Temperature (°C)"), min_value=35.0, max_value=42.0, step=0.1)
    st.subheader(t("💪 BMI Calculator"))
    height_cm = st.number_input(t("Height (in cm)"), min_value=100, max_value=250, step=1)
    weight_kg = st.number_input(t("Weight (in kg)"), min_value=20, max_value=250, step=1)

    # BMI Calculation
    if height_cm > 0:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        st.metric(t("🧮 Your BMI"), f"{bmi:.2f}")

        # BMI Classification
        if bmi < 18.5:
            st.session_state['bmi_desc']="Underweight"
            st.warning(t("🔹 Underweight"))
        elif 18.5 <= bmi < 25:
            st.session_state['bmi_desc']="Normal weight"
            st.success(t("✅ Normal weight"))
        elif 25 <= bmi < 30:
            st.session_state['bmi_desc']="Overweight"
            st.warning(t("🟠 Overweight"))
        else:
            st.session_state['bmi_desc']="Obese"
            st.error(t("🔴 Obese"))
        st.session_state["bmi"] = round(bmi, 2)


    if "health_data" not in st.session_state:
        st.session_state["health_data"] = pd.DataFrame(columns=["Blood Pressure", "Heart Rate", "Blood Sugar", "Temperature"])

    if st.button(t("Save Data")):
        new_data = pd.DataFrame([[st.session_state["blood_pressure"], st.session_state["heart_rate"], 
                                st.session_state["blood_sugar"], st.session_state["temperature"], st.session_state.get("bmi", None)]], 
                                columns=["Blood Pressure", "Heart Rate", "Blood Sugar", "Temperature","BMI"])
        st.session_state["health_data"] = pd.concat([st.session_state["health_data"], new_data], ignore_index=True)
        st.success(t("✅ Data saved successfully!"))
        
        # ✅ Set flag to show Risk Score after saving
        st.session_state["show_risk"] = True

    st.subheader(t("📊 Health Data Log"))
    st.dataframe(st.session_state["health_data"])
    
    st.subheader(t("📈 Health Trends"))
    if not st.session_state["health_data"].empty:
        health_data_numeric = st.session_state["health_data"].astype(float)
        fig = px.line(health_data_numeric, markers=True)
        st.plotly_chart(fig)
    if st.session_state.get("show_risk"):
        st.subheader(t("📋 Health Risk Overview"))

        with st.expander(t("Explain Risk Factors (Click to View Details)")):
            risk_table = """
            | **Metric** | **Normal Range** | **Points if Abnormal** |
            |:---|:---|:---|
            | Blood Pressure | 90–140 mmHg | +20 |
            | Heart Rate | 60–100 bpm | +20 |
            | Blood Sugar | 70–140 mg/dL | +20 |
            | BMI | 18.5–24.9 kg/m² | +10–20 |
            | Diabetes Prediction | Positive | +20 |
            | Heart Disease Prediction | Positive | +20 |
            | Kidney Disease Prediction | Positive | +20 |
            | High Fever (Temperature > 38°C) | Detected | +20 |
            """
            st.markdown(risk_table)

        st.subheader(t("📋 Health Risk Summary"))

        risk_score = calculate_risk_score()
        st.session_state["risk_score"]=risk_score

        # Color + Message
        if risk_score <= 30:
            risk_color = "green"
            risk_message = t("Low Risk ✅ Maintain healthy habits!")
            suggestion = [
               t("Continue a balanced diet"),
                t("Stay physically active"),
                t("Get routine checkups")
            ]
        elif risk_score <= 70:
            risk_color = "orange"
            risk_message = t("Moderate Risk ⚠️ Watch your health closely!")
            suggestion = [
                t("Consult a nutritionist"),
                t("Monitor BP, Sugar daily"),
                t("Mild exercise recommended")
            ]
        else:
            risk_color = "red"
            risk_message = t("High Risk ❗ Immediate medical attention advised!")
            suggestion = [
                t("Consult your doctor urgently"),
                t("Strict diet and medication"),
                t("Avoid stress and monitor vitals daily")
            ]
        st.session_state['risk_message']=risk_message
        translated_risk_score_label = t("Risk Score")
        st.markdown(f"""
        <div style="background-color:{risk_color};padding:10px;border-radius:10px">
        <h2 style="color:white;">{translated_risk_score_label}: {risk_score}/100</h2>
        <h4 style="color:white;">{risk_message}</h4>
        </div>
        """, unsafe_allow_html=True)
        # Show Suggestions
        st.subheader(t("💡 Personalized Suggestions:"))
        for i, tip in enumerate(suggestion, 1):
            st.markdown(f"- {tip}")
        st.session_state["suggestion"]=suggestion

        # # 📋 Appointment Request Form
        if risk_score >30:
            st.subheader(t("🚑 Appointment Request (Recommended)"))

            appointment_name = st.text_input(t("Patient Name"), st.session_state.get("patient_name", ""),key="appointment_patient_name")
            contact_number = st.text_input(t("Contact Number"))
            preferred_date = st.date_input(t("Preferred Appointment Date"))
            preferred_time = st.time_input(t("Preferred Time"))
            symptoms_summary = st.text_area(t("Briefly describe your symptoms:"))

            if st.button(t("Submit Appointment Request")):
                appointment_data = pd.DataFrame([{
                    "Patient Name": appointment_name,
                    "Contact Number": contact_number,
                    "Preferred Date": preferred_date,
                    "Preferred Time": preferred_time,
                    "Symptoms Summary": symptoms_summary,
                    "Request Timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                }])

                # Save appointment request
                appointments_file = f"appointments_{appointment_name.replace(' ', '_').lower()}.csv"
                if os.path.exists(appointments_file):
                    existing = pd.read_csv(appointments_file)
                    appointment_data = pd.concat([existing, appointment_data], ignore_index=True)
                appointment_data.to_csv(appointments_file, index=False)
                st.success(t("✅ Your appointment request has been submitted!"))
            st.subheader(t("📍 Hospital Suggestions Near You"))
    
            # Get the address from user
            address = st.text_input(t("Enter your full address to find hospitals nearby"), 
                                placeholder=t("e.g. 123 Main St, New York, NY 10001"))
            
            col1, col2 = st.columns([1,1])
            search_button = col1.button(t("🔍 Find Nearby Hospitals"))
            radius = col2.slider(t("Search radius (km)"), 1, 20, 5) * 1000  # Convert to meters
            
            # Store the address suggestions in session state if not already present
            if "address_suggestions" not in st.session_state:
                st.session_state.address_suggestions = []
            
            # If the user clicks the search button and enters an address
            if search_button and address:
                with st.spinner(t("Validating your address...")):
                    is_valid, suggestions, primary_result = validate_address(address)
                    
                    if not is_valid:
                        st.error(t("❌ Couldn't find this address. Please check your input and try again."))
                        return
                    
                    # Get primary suggestion details
                    primary_suggestion = suggestions[0] if suggestions else "Unknown"
                    st.session_state.address_suggestions = suggestions
                    
                    # Show address confirmation
                    if len(suggestions) > 1:
                        st.info(f"📌 Did you mean: **{primary_suggestion}**?")
                        
                        # Let user select from suggestions if multiple found
                        selected_address = st.selectbox(
                            t("Select your exact address:"),
                            suggestions
                        )
                    else:
                        selected_address = primary_suggestion
                    st.session_state["input_address"]=address    
                    # Get the geocoded coordinates
                    with st.spinner(t("Locating hospitals near you...")):
                        lat, lon, display_name = geocode_address(selected_address)
                        
                        if lat and lon:
                            st.session_state["user_address"] = selected_address
                            st.session_state["user_lat"] = lat
                            st.session_state["user_lon"] = lon                            
                            st.success(f"{t('📌 Location detected:')} {display_name}")
                            
                            # Get hospitals with the user-specified radius
                            hospitals = get_nearby_hospitals(lat, lon, radius=radius)                            
                            if hospitals:
                                # Try to extract city from the selected address
                                city = selected_address.split(',')[-2].strip() if ',' in selected_address else None
                                
                                # Enhance hospitals with Google Maps search links
                                hospitals = enhance_hospital_data(hospitals)
                                
                                # The rest of your existing hospital display code remains the same
                                for i, hospital in enumerate(hospitals, 1):
                                    with st.expander(f"{i}. {hospital['name']} ({hospital['distance']:.2f} km away)"):
                                        cols = st.columns([3, 1])
                                        
                                        address = get_cached_reverse_address(hospital['lat'], hospital['lon'])
                                        user_address = st.session_state.get("input_address", "")
                                        hospital_address = get_cached_reverse_address(hospital['lat'], hospital['lon'])
                                        # Left column with details
                                        details = f"""
                                        **{t('Address')}:** {address}  
                                        **{t('Phone')}:** {hospital.get('phone', t('Not available'))}  
                                        **{t('Emergency')}:** {hospital.get('emergency', t('Unknown'))}  
                                        """
                                        cols[0].markdown(details)
                                
                                        # Right column with map links
                                        # Use the new Google Maps search link
                                        map_url = hospital.get('google_maps_link', f"https://www.google.com/maps?q={hospital['lat']},{hospital['lon']}")
                                        cols[1].markdown(f"[📍 Open in Maps]({map_url})")

                                        osm_url = f"https://www.openstreetmap.org/?mlat={hospital['lat']}&mlon={hospital['lon']}&zoom=18"
                                        cols[1].markdown(f"[🗺️ View in OpenStreetMap]({osm_url})")

                                        # Add directions button
                                        directions_url = generate_google_maps_directions_link(user_address, hospital_address)
                                        cols[1].markdown(f"[🚗 Get Directions]({directions_url})")
                            else:
                                st.warning(t("No hospitals found within the specified radius. Try increasing the search radius."))
                        else:
                            st.error(t("❌ Couldn't determine coordinates for this address. Please try another address."))

            if st.button(t("Download Full Report")):
                pdf_path = generate_pdf()
                with open(pdf_path, "rb") as file:
                    st.download_button(t("Download PDF Report"), file, file_name=pdf_path, mime="application/pdf")