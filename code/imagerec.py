from PIL import Image
import numpy as np
import tensorflow as tf
import io

def decode_prediction(prediction, label_path):
    with open(label_path, "r") as f:
        labels = [line.strip() for line in f.readlines()]
    predicted_index = np.argmax(prediction)
    return labels[predicted_index]

def imagerecognise(image_bytes, model_path, label_path):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize((150, 150))  # Match the expected model input size
    img_array = tf.keras.preprocessing.image.img_to_array(image)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize

    model = model_path
    prediction = model.predict(img_array)

    y = decode_prediction(prediction, label_path)
    conf = np.max(prediction) * 100
    return y, conf
