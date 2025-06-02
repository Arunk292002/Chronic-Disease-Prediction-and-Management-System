import streamlit as st
import streamlit.components.v1 as components
import datetime
from core.helper import t

def privacy_policy_english():
    components.html("""
        <style>
            @keyframes fadeSlide {
                0% {opacity: 0; transform: translateY(-10px);}
                100% {opacity: 1; transform: translateY(0);}
            }
            #title {
                font-family: 'Segoe UI', sans-serif;
                font-size: 4vw;
                font-weight: bold;
                text-align: center;
                margin-top: 20px;
                animation: fadeSlide 1s ease-out;
                background: linear-gradient(90deg, #FF4081, #FFCDD2);
                -webkit-background-clip: text;
            }
        </style>
        <div id="title">🔐 Privacy Policy</div>
    """, height=100)
    st.markdown("""
    Welcome to our Chronic Disease Management App. Your privacy is important to us. This policy outlines how we collect, use, and protect your personal and health data.

    ---

    ### 📌 What Data We Collect
    - Health parameters: age, blood pressure, blood glucose, symptoms, etc.
    - Login credentials (via Firebase Authentication)
    - Device/browser information (for session security)

    ---

    ### 🎯 Purpose of Data Collection
    Your data is collected to:
    - Provide disease risk predictions
    - Personalize health insights
    - Track health progress over time

    ---

    ### 🚫 Data Sharing
    - We **do not share** your data with third parties without your consent.
    - Data may be anonymized for research or improvement purposes.

    ---

    ### 🧱 Data Security
    - Authentication is managed by **Firebase Authentication**
    - Health data is stored in a **secured Firestore database**
    - Sensitive fields may be encrypted before storage

    ---

    ### 🙋 Your Rights
    As a user, you have the right to:
    - View your stored data
    - Download your health records
    - Request deletion of your account and all related data

    Contact us at **support@yourapp.com** for data removal requests.

    ---

    ### 📅 Data Retention
    Your health records are stored securely unless you explicitly request their deletion.

    ---

    ### ✅ Consent
    By using this app, you agree to the terms outlined above. You may withdraw your consent at any time.

    ---
    """)

def privacy_policy_tamil():
    st.title("🔐 தனியுரிமைக் கொள்கை")
    st.markdown("""
    எங்கள் நெடுங்கால நோய் மேலாண்மை பயன்பாட்டுக்கு வரவேற்கிறோம். உங்கள் தனியுரிமை எங்களுக்கு முக்கியம். உங்கள் தனிப்பட்ட மற்றும் ஆரோக்கிய தரவுகளை எவ்வாறு சேகரிக்கிறோம், பயன்படுத்துகிறோம் மற்றும் பாதுகாக்கிறோம் என்பதைக் கூறும் இந்த கொள்கையைப் படிக்கவும்.

    ---

    ### 📌 நாங்கள் சேகரிக்கும் தரவுகள்
    - ஆரோக்கிய அளவீடுகள்: வயது, இரத்த அழுத்தம், இரத்த சர்க்கரை, அறிகுறிகள் மற்றும் பிற.
    - உள்நுழைவு தகவல்கள் (ஃபயர்பேஸ் அத்தாட்சியீடு மூலம்)
    - சாதனம்/உலாவி தகவல்கள் (அமர்வு பாதுகாப்பிற்காக)

    ---

    ### 🎯 தரவுச் சேகரிப்பின் நோக்கம்
    உங்கள் தரவுகள் கீழ்காணும் நோக்கங்களுக்காக சேகரிக்கப்படுகிறது:
    - நோய் அபாய கணிப்புகளை வழங்க
    - ஆரோக்கிய அறிவுறுத்தல்களை தனிப்பயனாக்க
    - காலப்போக்கில் ஆரோக்கிய முன்னேற்றத்தை கண்காணிக்க

    ---

    ### 🚫 தரவு பகிர்வு
    - உங்கள் அனுமதியில்லாமல் உங்கள் தரவுகளை மூன்றாம் தரப்பினருடன் பகிரமாட்டோம்.
    - ஆராய்ச்சி அல்லது மேம்பாட்டு நோக்கங்களுக்காக தரவுகள் அடையாளம் தெரியாதவையாக மாற்றப்படலாம்.

    ---

    ### 🧱 தரவு பாதுகாப்பு
    - உள்நுழைவு மற்றும் அத்தாட்சியீடு **ஃபயர்பேஸ் அத்தாட்சியீடு** மூலம் நிர்வகிக்கப்படுகிறது.
    - ஆரோக்கிய தரவுகள் **பாதுகாப்பான ஃபயர்ஸ்டோர் தரவுத்தொகையில்** சேமிக்கப்படுகின்றன.
    - முக்கியமான புலங்கள் சேமிப்பிற்கு முன் குறியாக்கம் செய்யப்படலாம்.

    ---

    ### 🙋 உங்கள் உரிமைகள்
    ஒரு பயனராக, உங்களுக்கு கீழ்காணும் உரிமைகள் உள்ளன:
    - உங்கள் சேமித்த தரவுகளை பார்வையிட
    - உங்கள் ஆரோக்கிய பதிவுகளை பதிவிறக்க
    - உங்கள் கணக்கு மற்றும் தொடர்புடைய அனைத்து தரவுகளையும் நீக்குமாறு கோருங்கள்

    தரவு நீக்க கோரிக்கைகளுக்காக **support@yourapp.com** என்ற முகவரியில் எங்களை தொடர்பு கொள்ளவும்.

    ---

    ### 📅 தரவு வைத்திருப்பு
    நீங்கள் வெளிப்படையாக நீக்குமாறு கோரிக்கையிடாத வரை உங்கள் ஆரோக்கிய பதிவுகள் பாதுகாப்பாக சேமிக்கப்படும்.

    ---

    ### ✅ உடன்பாடு
    இந்த பயன்பாட்டைப் பயன்படுத்துவதன் மூலம், மேலே குறிப்பிடப்பட்டுள்ள விதிமுறைகளுக்கு நீங்கள் ஒப்புக்கொள்கிறீர்கள். நீங்கள் எந்த நேரத்திலும் உங்கள் ஒப்புதலை திரும்ப பெறலாம்.

    ---
    """)

def run():
    if st.session_state['language'] == "English":
        privacy_policy_english()
    elif st.session_state['language'] == "Tamil":
        privacy_policy_tamil()

    st.info(t("You can manage your data or revoke consent at any time via your account settings."))
    st.caption(f"{t('Last updated:')} {datetime.date.today().strftime('%B %d, %Y')}")

if __name__ == "__main__":
    run()