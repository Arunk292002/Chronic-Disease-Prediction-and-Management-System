import streamlit as st
from code.imagerec import imagerecognise
import streamlit.components.v1 as components
from PIL import Image
from core.models import load_models
from core.helper import t

model=load_models()
lung_caner_model=model['lung_cancer']

def run():
    page_title=t("Lung Cancer Detection")
    # Custom animated title
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

    # Hide Streamlit menu and footer
    st.markdown("""
        <style>
            #MainMenu, footer {visibility: hidden;}
            .stButton>button {
                background-color: #009688;
                color: white;
                font-size: 18px;
                padding: 0.75em 2em;
                border-radius: 10px;
                border: none;
                transition: background-color 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #00796B;
            }
        </style>
    """, unsafe_allow_html=True)

    # File uploader
    uploaded_file = st.file_uploader(t("📤 Upload a Lung CT Image"), type=['jpg', 'jpeg', 'png'])

    if uploaded_file:
        st.image(uploaded_file, caption=t("🖼️ Uploaded Lung Image"), use_column_width=True)

    # Predict button
    if st.button(t("🔍 Predict")):
        with st.spinner(t("🔬 Analyzing Image... Please wait.")):
            image_bytes = uploaded_file.read()
            y, conf = imagerecognise(image_bytes, lung_caner_model, "models/lung_labels.txt")

        # Result for Normal Lungs
        if y.strip().lower() == "normal":
            predict_res=t("✅ Lungs are Healthy!")
            components.html(f"""
                <style>
                    .result {{
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 26px;
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

        # Result for Cancer Detected
        else:
            predict_res=t("❌ Lung Cancer Detected!")
            predict_subtext=t("⚠️ Consult an Oncologist Immediately")
            components.html(f"""
                <style>
                    .result-bad {{
                        font-family: 'Segoe UI', sans-serif;
                        font-size: 25px;
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

            # Save to session_state
        st.session_state["lung_image_name"] = uploaded_file.name
        st.session_state["lung_prediction_label"] = y.strip().lower()
        st.session_state["lung_prediction_confidence"] = conf
        st.session_state['lung_image_bytes'] = image_bytes