from flask import Flask, render_template, request, jsonify
import pandas as pd
from textblob import TextBlob
import nltk
from collections import Counter
import os
import json
import traceback
import sys

# Set up NLTK data path for Vercel
if os.environ.get('VERCEL'):
    NLTK_DATA = os.path.join('/tmp', 'nltk_data')
    if not os.path.exists(NLTK_DATA):
        os.makedirs(NLTK_DATA)
    nltk.data.path.append(NLTK_DATA)

# Download required NLTK data
try:
    nltk.data.find('punkt')
except LookupError:
    if os.environ.get('VERCEL'):
        nltk.download('punkt', download_dir=NLTK_DATA)
    else:
        nltk.download('punkt')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = '/tmp' if os.environ.get('VERCEL') else 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analyze_sentiment(text):
    """Analyze sentiment of given text using TextBlob."""
    try:
        # Print for debugging
        print(f"Analyzing text: {text[:100]}...")  # Print first 100 chars
        
        if not isinstance(text, str):
            text = str(text)
        
        if not text.strip():
            return None
            
        analysis = TextBlob(text)
        # Get polarity score (-1 to 1)
        score = analysis.sentiment.polarity
        
        # Classify sentiment
        if score < -0.1:
            label = "Negative"
        elif score > 0.1:
            label = "Positive"
        else:
            label = "Neutral"
        
        # Print for debugging
        print(f"Analysis result - Score: {score}, Label: {label}")
            
        return {
            'score': score,
            'label': label
        }
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        print(traceback.format_exc())
        return None

def generate_word_cloud_data(text):
    """Generate word frequency data for word cloud."""
    try:
        # Tokenize and count words
        words = nltk.word_tokenize(str(text).lower())
        # Filter out short words and common stop words
        words = [word for word in words if len(word) > 3 and word.isalnum()]
        word_freq = Counter(words).most_common(50)
        return [{'text': word, 'value': count} for word, count in word_freq]
    except Exception as e:
        print(f"Error generating word cloud data: {str(e)}")
        print(traceback.format_exc())
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze/text', methods=['POST'])
def analyze_text():
    try:
        print("Received text analysis request")  # Debug print
        data = request.get_json()
        
        if not data or 'text' not in data:
            print("No text provided in request")  # Debug print
            return jsonify({'success': False, 'error': 'No text provided'}), 400

        text = data['text']
        if not isinstance(text, str) or not text.strip():
            return jsonify({'success': False, 'error': 'Invalid text provided'}), 400
            
        print(f"Processing text: {text[:100]}...")  # Debug print
        
        sentiment_result = analyze_sentiment(text)
        
        if not sentiment_result:
            print("Failed to analyze sentiment")  # Debug print
            return jsonify({'success': False, 'error': 'Failed to analyze sentiment'}), 500

        word_cloud_data = generate_word_cloud_data(text)
        
        response_data = {
            'success': True,
            'sentiment': sentiment_result,
            'wordCloudData': word_cloud_data
        }
        print(f"Sending response: {json.dumps(response_data)[:200]}...")  # Debug print
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in analyze_text: {str(e)}")  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze/file', methods=['POST'])
def analyze_file():
    filepath = None
    try:
        print("Received file analysis request")
        
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            print("Empty filename")
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            print(f"Invalid file extension: {file_ext}")
            return jsonify({'success': False, 'error': 'Please upload a CSV or Excel file'}), 400

        # Create upload folder if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Save file temporarily
        import uuid
        safe_filename = str(uuid.uuid4()) + file_ext
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        print(f"Saving file to: {filepath}")
        file.save(filepath)

        try:
            # Read file based on extension
            print(f"Reading file: {filepath} with extension: {file_ext}")
            
            if file_ext == '.csv':
                df = pd.read_csv(filepath)
            else:  # Excel file
                df = pd.read_excel(filepath)
            
            print(f"File read successfully. Shape: {df.shape}")
            
            if df.empty:
                raise ValueError("The uploaded file is empty")
                
            # Get text columns
            text_columns = df.select_dtypes(include=['object']).columns
            print(f"Text columns found: {list(text_columns)}")
            
            if len(text_columns) == 0:
                raise ValueError("No text columns found in the file")
                
            # Use the first text column
            text_column = text_columns[0]
            print(f"Using column: {text_column}")
            
            # Initialize counters
            results = []
            all_text = []
            sentiment_counts = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
            total_score = 0
            valid_reviews = 0

            # Process each row
            for text in df[text_column].fillna(''):
                if isinstance(text, str) and text.strip():
                    try:
                        sentiment_result = analyze_sentiment(text)
                        if sentiment_result:
                            results.append(sentiment_result)
                            sentiment_counts[sentiment_result['label']] += 1
                            total_score += sentiment_result['score']
                            all_text.append(text)
                            valid_reviews += 1
                    except Exception as e:
                        print(f"Error analyzing text: {str(e)}")
                        continue

            if valid_reviews == 0:
                raise ValueError("No valid text found for analysis")

            print(f"Successfully analyzed {valid_reviews} reviews")

            # Generate word cloud data
            word_cloud_data = generate_word_cloud_data(' '.join(all_text))

            # Calculate average sentiment
            avg_sentiment = total_score / valid_reviews if valid_reviews > 0 else 0

            response_data = {
                'success': True,
                'totalReviews': valid_reviews,
                'sentimentCounts': sentiment_counts,
                'averageSentiment': avg_sentiment,
                'wordCloudData': word_cloud_data
            }
            
            print("Analysis completed successfully")
            return jsonify(response_data)

        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': error_msg}), 500

    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': error_msg}), 500
    
    finally:
        # Clean up temporary file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Cleaned up temporary file: {filepath}")
            except Exception as e:
                print(f"Error cleaning up file {filepath}: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True) 