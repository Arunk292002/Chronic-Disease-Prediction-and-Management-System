import streamlit as st
st.set_page_config(page_title="Chronic Disease Prediction and Management")
from features import (
    home, diabetes, heart, kidney, liver, lung_cancer,
    fever, hypertension, symptom_tracker, disease_predictor,privacy)
from core.auth import handle_auth
from core.helper import t

if "language" not in st.session_state:
    st.session_state["language"] = "English"
language = st.sidebar.selectbox("🌐 Choose Language", ["English", "Tamil"])
st.session_state["language"] = language

st.markdown("""
        <style>
            #MainMenu, footer {visibility: hidden;}
            .stButton>button,.stDownloadButton>button {
                background-color: #6200EE;
                color: white;
                font-size: 18px;
                padding: 0.75em 2em;
                border-radius: 10px;
                border: none;
                transition: background-color 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #3700B3;
            .stElementContainer{
            flex:0 0 50%; 
            }
            }</style>""", 
        unsafe_allow_html=True)

# Page Title
st.title(t("\U0001F3E5 Patient Health Dashboard"))
st.write(t("Monitor and log vital health data for better tracking and care."))

# Function to handle redirect to home page after login
def redirect_to_home():
    # Set logged-in user session state
    st.session_state["logged_in_user"] = True  # or some user data based on login
    # You can then show the Home Page
    home.run()

# Main logic for showing Login/Register or Home page
if "logged_in_user" not in st.session_state:
    # If not logged in, show Login/Register page
    menu = st.sidebar.selectbox("Navigation", ["Login/Register"])
    
    if menu == "Login/Register":
        # Handle login process (the login function will update session state)
        handle_auth()
        
        # After successful login, redirect to Home
        # Redirect logic could be a simple state change
        if "logged_in_user" in st.session_state:  # After login success
            redirect_to_home()  # Redirect to Home page
else:
    if st.sidebar.button(t("Logout")):
        del st.session_state["logged_in_user"]
        st.success("Logged out successfully!")
        st.rerun()
    # If logged in, show the full menu (e.g., Disease Prediction, etc.)
    menu = st.sidebar.selectbox("Navigation", [
        "Home", "Disease Prediction", "Hypertension", "Diabetes",
        "Heart Disease", "Kidney Disease","Lung Cancer", "Fever", "Symptom Tracker","Privacy"
    ])

    # Handle routing for different pages
    if menu == "Home":
        home.run()
    elif menu == "Disease Prediction":
        disease_predictor.run()
    elif menu == "Hypertension":
        hypertension.run()
    elif menu == "Diabetes":
        diabetes.run()
    elif menu == "Heart Disease":
        heart.run()
    elif menu == "Kidney Disease":
        kidney.run()
    elif menu=='Lung Cancer':
        lung_cancer.run()
    elif menu == "Fever":
        fever.run()
    elif menu == "Symptom Tracker":
        symptom_tracker.run()
    elif menu=="Privacy":
        privacy.run()