from flask import Flask, request, render_template
import joblib
import os
from feature_extraction import extract_features

app = Flask(__name__)

# Loaded the trained model 
model = joblib.load('ML_model/malwareclassifier-V2.pkl')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'dll', 'exe'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if a file is uploaded
    if 'file' in request.files:
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('index.html', error="Unsupported file type.")
        
        # Construct the full file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Save the file
        file.save(file_path)

        # Use the model for prediction if the file is `.exe` or `.dll`
        if allowed_file(file.filename):
            try:
                features = extract_features(file_path)
                prediction = model.predict(features)
                
                safe_prob = 50.0
                malware_prob = 50.0
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(features)[0]
                    safe_prob = round(float(proba[0]) * 100, 1)
                    malware_prob = round(float(proba[1]) * 100, 1)
                elif prediction[0] == 1:
                    malware_prob = 100.0
                    safe_prob = 0.0
                else:
                    malware_prob = 0.0
                    safe_prob = 100.0

                is_malware = bool(prediction[0] == 1)
                verdict = "Malware" if is_malware else "Safe"
                confidence = max(safe_prob, malware_prob)

                row = features.iloc[0].to_dict()

                pe_metrics = {
                    'sections_count': int(row.get('SectionMaxChar', 0)),
                    'entry_point': f"0x{int(row.get('AddressOfEntryPoint', 0)):x}",
                    'image_base': f"0x{int(row.get('ImageBase', 0)):x}",
                    'min_entropy': f"{float(row.get('SectionMinEntropy', 0)):.4f}" if row.get('SectionMinEntropy') is not None else "0.0000",
                    'export_size': f"{int(row.get('ImageDirectoryEntryExport', 0))} bytes",
                    'import_size': f"{int(row.get('DirectoryEntryImportSize', 0))} bytes",
                    'size_of_headers': f"{int(row.get('SizeOfHeaders', 0))} bytes",
                    'min_virtual_size': f"{int(row.get('SectionMinVirtualsize', 0))} bytes",
                    'dll_characteristics': f"0x{int(row.get('DllCharacteristics', 0)):x}",
                    'checksum': f"0x{int(row.get('CheckSum', 0)):x}"
                }

                result = {
                    "type": "file",
                    "prediction": verdict,
                    "is_malware": is_malware,
                    "file_name": file.filename,
                    "safe_prob": safe_prob,
                    "malware_prob": malware_prob,
                    "confidence": confidence,
                    "pe_metrics": pe_metrics
                }
                return render_template('result.html', result=result)
            except Exception as e:
                return render_template('index.html', error=f"Error extracting features: {str(e)}")

    return render_template('index.html', error="No file uploaded.")

if __name__ == '__main__':
    app.run(port=5001, debug=True)

