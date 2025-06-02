import streamlit as st
import requests
import io
import fitz
from datetime import date
from config.firebase_config import auth
from core.helper import suggest_email_correction, check_password_strength, bar_color, strength_label

try:
    from core.helper import t  # Translation function
except ImportError:
    t = lambda x: x  # fallback

def email_input(label, key):
    email = st.text_input(t(label), key=key)
    correction = suggest_email_correction(email)
    if correction:
        st.warning(f"⚠️ {t('Did you mean')} {correction}?")
    return email

def display_password_strength(password):
    strength = check_password_strength(password)
    if password:
        st.markdown(f"""
            <div style='margin-top:10px; margin-bottom:10px'>
                <div style='width:100%;background:#ddd;height:15px;border-radius:5px'>
                    <div style='width:{(strength/5)*100}%;height:15px;border-radius:5px;background:{bar_color[strength]}'></div>
                </div>
                <small style='color:{bar_color[strength]}'><b>{t(strength_label[strength])}</b></small>
            </div>
        """, unsafe_allow_html=True)
    return strength

def handle_auth():
    st.header(t("🔒 Login / 📝 Register"))
    login_tab, register_tab = st.tabs([t("Login"), t("Register")])

    with login_tab:
        st.subheader(t("🔐 Login"))
        email = email_input("Email", key="login_email")
        password = st.text_input(t("Password"), type="password", key="login_password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("Login"), use_container_width=True):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state["logged_in_user"] = email
                    st.success(f"✅ {t('Welcome')}, {email}!")
                    st.rerun()
                except Exception:
                    st.error(t("❌ Login failed. Please check your credentials."))

        with col2:
            if st.button(t("Forgot Password?"), use_container_width=True):
                if not email:
                    st.warning(t("⚠️ Please enter your email above to reset password."))
                else:
                    try:
                        auth.send_password_reset_email(email)
                        st.success(t("📧 Password reset link sent to your email."))
                    except Exception:
                        st.error(t("❌ Failed to send reset link. Please check the email address."))

    with register_tab:
        st.subheader(t("📝 Register"))
        email = email_input("Email", key="register_email")
        password = st.text_input(t("Password"), type="password", key="register_password")
        confirm_password = st.text_input(t("Confirm Password"), type="password", key="confirm_password")

        strength = display_password_strength(password)

        st.markdown(f"### {t('📄 User Consent')}")

        # Link to view blank consent form (hosted on GDrive, GitHub, or your server)
        st.markdown('[📄 View Consent Form Template](https://drive.google.com/file/d/1u820xqJVJc0CIQBiHZ0zYLdJRDM-Rv3L/view)', unsafe_allow_html=True)

        # Consent checkbox
        consent_given = st.checkbox(t("✅ I agree to the terms and conditions outlined in the User Consent Form."))

        if consent_given:
            user_name = st.text_input(t("🖊️ Enter your full name to sign the consent form:"))
            
            if user_name:
                # Download the clean template
                response = requests.get("https://drive.google.com/uc?export=download&id=1u820xqJVJc0CIQBiHZ0zYLdJRDM-Rv3L")
                if response.status_code == 200:
                    original_pdf_bytes = response.content

                    # Open and edit
                    doc = fitz.open(stream=original_pdf_bytes, filetype="pdf")
                    page = doc[0]

                    name_position = fitz.Point(130, 440)
                    date_position = fitz.Point(130, 465)
                    page.insert_text(name_position, user_name, fontsize=12, fontname="helv")
                    page.insert_text(date_position, date.today().strftime("%Y-%m-%d"), fontsize=12, fontname="helv")

                    # Save edited PDF to buffer
                    pdf_buffer = io.BytesIO()
                    doc.save(pdf_buffer)
                    doc.close()

                    # Download button
                    st.download_button(
                        label=t("📄 Download Your Signed Consent Form"),
                        data=pdf_buffer.getvalue(),
                        file_name="Signed_User_Consent_Form.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error(t("❌ Failed to load consent form template from Google Drive."))

        if st.button(t("Register"), use_container_width=True):
            if not email:
                st.warning(t("❌ Email is required."))
            elif password != confirm_password:
                st.warning(t("❌ Passwords do not match."))
            elif strength < 3:
                st.warning(t("❌ Password too weak."))
            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success(t("✅ Account created successfully! You can now log in."))
                except Exception:
                    st.error(t("❌ Registration failed. Please try again later."))
