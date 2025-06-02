import pickle
import joblib 
import tensorflow as tf

def load_models():
    return {
        "diabetes": joblib.load(open("models/diabetes_model.pkl", "rb")),
        "heart": pickle.load(open("models/cardio_model_ML.pkl", "rb")),
        "kidney": joblib.load("models/kidney_disease_model.pkl"),
        "kidney_mri":tf.keras.models.load_model("models/kidn.h5"),
        "liver": joblib.load("models/liver_model.sav"),
        "hypertension": joblib.load("models/hypertension_model.pkl"),
        "mean_std": pickle.load(open("models/mean_std_values.pkl", "rb")),
        "lung_cancer":tf.keras.models.load_model("models/lungcnn.h5")
    }
