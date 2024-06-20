from flask import Flask, request, render_template, send_file
import pandas as pd
import json
import os
import unicodedata

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        try:
            # Process the JSON file
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            return 'File encoding error. Please upload a file with UTF-8 encoding.'
        except json.JSONDecodeError:
            return 'Invalid JSON file. Please upload a properly formatted JSON file.'

        # Normalize the message to NFKD (Normalization Form KC)
        def normalize_text(text):
            return unicodedata.normalize('NFKD', text)

        # Filter the data
        filtered_data = [obj for obj in data if 'DAZN' in normalize_text(obj.get('message', ''))]
        if not filtered_data:
            return 'No messages contain the word DAZN'

        # Convert to DataFrame
        df = pd.DataFrame(filtered_data)
        # Save to Excel
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'filtered_data.xlsx')
        df.to_excel(excel_path, index=False)
        return send_file(excel_path, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
