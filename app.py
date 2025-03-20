from flask import Flask, render_template, request, jsonify
import pandas as pd
from textblob import TextBlob
import plotly.express as px
from collections import Counter
import re

app = Flask(__name__)

def analyze_sentiment(text):
    """Simple sentiment analysis using TextBlob"""
    if not isinstance(text, str):
        return 0
    analysis = TextBlob(str(text))
    return analysis.sentiment.polarity

def get_sentiment_label(score):
    """Convert sentiment score to label"""
    if score > 0.1:
        return 'Positive'
    elif score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Process the data
            df['Sentiment'] = df['Review'].apply(analyze_sentiment)
            df['Sentiment_Label'] = df['Sentiment'].apply(get_sentiment_label)
            
            # Calculate statistics
            total_reviews = len(df)
            sentiment_counts = df['Sentiment_Label'].value_counts()
            avg_sentiment = df['Sentiment'].mean()
            
            # Create visualizations
            sentiment_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title='Sentiment Distribution'
            )
            
            sentiment_dist = px.histogram(
                df,
                x='Sentiment',
                title='Sentiment Score Distribution',
                nbins=50
            )
            
            # Prepare word cloud data
            text = ' '.join(df['Review'].astype(str))
            words = re.findall(r'\w+', text.lower())
            word_freq = Counter(words)
            
            # Create word cloud data (limit to top 50 words)
            word_cloud_data = [
                {'text': word, 'value': freq}
                for word, freq in word_freq.most_common(50)
                if len(word) > 2  # Filter out short words
            ]
            
            return jsonify({
                'success': True,
                'total_reviews': total_reviews,
                'sentiment_counts': sentiment_counts.to_dict(),
                'avg_sentiment': float(avg_sentiment),
                'sentiment_pie': sentiment_pie.to_json(),
                'sentiment_dist': sentiment_dist.to_json(),
                'word_cloud': word_cloud_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

if __name__ == '__main__':
    app.run(debug=True) 