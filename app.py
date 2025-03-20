from flask import Flask, render_template, request, jsonify
from sentiment_analyzer import analyze_sentiment
from data_processor import process_excel_file
import os
import nltk

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp'  # Use /tmp for Vercel

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith(('.xlsx', '.xls', '.csv')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            results = process_excel_file(filepath)
            os.remove(filepath)  # Clean up the uploaded file
            return jsonify(results)
        else:
            return jsonify({'error': 'Invalid file format. Please upload Excel or CSV file.'}), 400
    
    elif 'text' in request.form:
        text = request.form['text']
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        result = analyze_sentiment(text)
        return jsonify(result)
    
    return jsonify({'error': 'No input provided'}), 400

if __name__ == '__main__':
    app.run(debug=True) 