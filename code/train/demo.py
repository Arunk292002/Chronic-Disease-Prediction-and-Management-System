import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Load dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
df = pd.read_csv(url, header=None)

# Assign column names
df.columns = [
    "Age", "Gender", "Total_Bilirubin", "Direct_Bilirubin",
    "Alkaline_Phosphotase", "Alamine_Aminotransferase", "Aspartate_Aminotransferase",
    "Total_Protiens", "Albumin", "Albumin_and_Globulin_Ratio", "Liver_Disease"
]

# Drop rows with missing values
df.dropna(inplace=True)

# Encode Gender: Male = 0, Female = 1
df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})

# Convert labels: 1 = liver disease, 2 = no liver disease → 1 = disease, 0 = healthy
df["Liver_Disease"] = df["Liver_Disease"].map({1: 1, 2: 0})

# Split features and labels
X = df.drop(columns=["Liver_Disease"])
y = df["Liver_Disease"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Train model with class weight balancing
model = RandomForestClassifier(class_weight="balanced", n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "liver_model.sav")
print("\n✅ Model saved to liver_model.sav")
