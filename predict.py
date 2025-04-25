import os
import numpy as np
import cv2
import joblib
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.utils import img_to_array
import tensorflow as tf

# ✅ Label mapping — must match training class order
label_map = {
    0: "Tomato_Bacterial_spot",
    1: "Tomato_Early_blight",
    2: "Tomato_Healthy",
    3: "Tomato_Late_blight",
    4: "Tomato_Leaf_Mold",
    5: "Tomato_Septoria_leaf_spot",
    6: "Tomato_Spider_mites_Two_spotted_spider_mite",
    7: "Tomato_Target_Spot",
    8: "Tomato_Tomato_Yellow_Leaf_Curl_Virus",
    9: "Tomato_mosaic_virus"
}
num_classes = len(label_map)

# ✅ Build MobileNetV2 model with custom head
def build_model():
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

# ✅ Load model weights
cnn_model = build_model()
try:
    cnn_model.load_weights("keras_trained_model_weights.h5")
    print("✅ MobileNetV2 model loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load MobileNetV2 weights: {e}")
    cnn_model = None

# ✅ Load the non-tomato filter model
try:
    filter_model = joblib.load("non_tomato_leaf_filter.pkl")
    print("✅ Non-tomato leaf filter model loaded.")
except Exception as e:
    print(f"❌ Could not load filter model: {e}")
    filter_model = None

# ✅ Final prediction function
def predict_image(file_path, confidence_threshold=60):
    print(f"\n📷 Predicting: {file_path}")
    
    if not os.path.exists(file_path):
        return {"error": "❌ Image file not found."}

    if cnn_model is None:
        return {"error": "❌ CNN model not loaded."}

    try:
        img = cv2.imread(file_path)
        if img is None:
            return {"error": "❌ Could not read image."}

        # Step 1: Apply non-tomato filter
        if filter_model:
            flat_img = cv2.resize(img, (150, 150)).flatten().reshape(1, -1)
            filter_result = filter_model.predict(flat_img)[0]
            if filter_result == 0:
                return {
                    "is_tomato_leaf": False,
                    "disease_name": "Tomato Leaf Not Detected",
                    "confidence": "N/A",
                    "treatment": "No treatment needed."
                }

        # Step 2: Predict disease with MobileNetV2
        resized = cv2.resize(img, (224, 224))
        img_array = img_to_array(resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = cnn_model.predict(img_array)[0]
        confidence = round(np.max(preds) * 100, 2)
        predicted_index = np.argmax(preds)
        predicted_label = label_map.get(predicted_index, "Unknown")

        print(f"🧠 Predicted: {predicted_label} | Confidence: {confidence}%")

        result = {
            "is_tomato_leaf": True,
            "disease_name": predicted_label,
            "confidence": confidence
        }

        if confidence < confidence_threshold:
            result["note"] = "⚠️ Low confidence. Please verify manually."

        return result

    except Exception as e:
        return {"error": f"❌ Prediction error: {str(e)}"}

# ✅ Test
if __name__ == "__main__":
    print(predict_image("uploads/test.jpg"))
