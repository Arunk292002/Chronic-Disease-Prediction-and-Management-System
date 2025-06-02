## 🏥 Chronic Disease Prediction and Management System

This project is an AI-powered web and mobile-compatible application built using **Streamlit** to predict and monitor chronic diseases such as **Heart Disease**, **Diabetes**, **Kidney Disease**, and **Lung Disease**. It integrates **machine learning** and **deep learning** techniques to offer real-time health risk predictions, second-opinion evaluation, and telehealth support.

---

### 🚀 Features

* 🔍 Predicts risk for 4 major chronic conditions using clinical data and medical images
* 🧠 Uses ML models like Logistic Regression, Random Forest, SVM and CNN
* 📊 Visualizes prediction results with charts and health risk levels
* 📁 Allows users to upload lab reports and X-ray/CT scans for image-based diagnosis
* 🌐 Multilingual dashboard support (e.g., English and Tamil)
* 📄 PDF report generation with risk classification and model interpretation
* 🔒 Secure user authentication via Firebase and compliance with **DPDPA 2023**
* 💬 Built-in appointment scheduling and secure messaging for telehealth support

---

### 🧰 Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python, Scikit-learn, TensorFlow, Keras, OpenCV
* **Authentication**: Firebase
* **Visualization**: Matplotlib, Seaborn, Plotly
* **PDF Generation**: fpdf
* **Deployment**: Streamlit Sharing / Render / Railway

---

### 🧪 Model Overview

| Disease        | Model Used             | Input Type      |
| -------------- | ---------------------- | --------------- |
| Heart Disease  | Random Forest          | Structured data |
| Diabetes       | Logistic Regression    | Structured data |
| Kidney Disease | Support Vector Machine | Structured data |
| Lung Disease   | CNN                    | X-ray/CT images |

---

### 📁 How to Run

1. Clone this repo
   `git clone [https://github.com/Arunk292002/chronic-disease-prediction.git](https://github.com/Arunk292002/Chronic-Disease-Prediction-and-Management-System.git)`
2. Install dependencies
   `pip install -r requirements.txt`
3. Launch Streamlit
   `streamlit run app.py`

---
