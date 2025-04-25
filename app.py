from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
import pyrebase
from predict import predict_image  # uses CNN + filter .pkl model

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Firebase Config (unchanged)
firebase_config = {
    "apiKey": "AIzaSyDu1vfZOceK6RSBzJqmJZqeFuuqL9Z4A60",
    "authDomain": "cropguardauth.firebaseapp.com",
    "projectId": "cropguardauth",
    "storageBucket": "cropguardauth.firebasestorage.app",
    "messagingSenderId": "591988252857",
    "appId": "1:591988252857:web:cfdb69638542203774bb68",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# ✅ Upload config
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Disease Treatment Map
disease_treatments = {
    "Tomato_Yellow_Leaf_Curl_Virus": "Use resistant varieties and control whiteflies.",
    "Tomato_Early_blight": "Apply fungicides like chlorothalonil or copper-based sprays.",
    "Tomato_Late_blight": "Use mancozeb-based fungicides and remove infected leaves.",
    "Tomato_Bacterial_spot": "Use copper-based fungicides and avoid overhead watering.",
    "Tomato_Leaf_Mold": "Improve air circulation, reduce humidity, apply fungicides.",
    "Tomato_Septoria_leaf_spot": "Remove affected leaves and apply chlorothalonil sprays.",
    "Tomato_Target_Spot": "Apply fungicides and rotate crops regularly.",
    "Tomato_mosaic_virus": "Disinfect tools, remove infected plants, control aphids.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Use neem oil or insecticidal soap.",
    "Tomato_Healthy": "No treatment required."
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                print("✅ Image saved:", file_path)
                prediction = predict_image(file_path)
                print("🧠 Model Prediction:", prediction)

                if "error" in prediction:
                    return jsonify({'error': prediction["error"]}), 500

                if not prediction.get("is_tomato_leaf"):
                    return jsonify({
                        'disease_name': "Tomato Leaf Not Detected",
                        'confidence_score': "N/A",
                        'treatment': "No treatment needed. Image does not contain a tomato leaf."
                    })

                disease = prediction["disease_name"]
                confidence = prediction["confidence"]
                treatment = disease_treatments.get(disease, "No specific treatment found.")

                return jsonify({
                    'disease_name': disease,
                    'confidence_score': confidence,
                    'treatment': treatment
                })

            return jsonify({'error': 'Invalid file format'}), 400

        except Exception as e:
            print("❌ Exception during upload:", e)
            return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

    return render_template('upload.html')

# ✅ Launch
if __name__ == '__main__':
    app.run(debug=True)
