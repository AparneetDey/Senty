from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Initialize the VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using VADER sentiment analysis.
    Returns a dictionary with sentiment scores and overall sentiment.
    """
    # Get sentiment scores
    sentiment_scores = sia.polarity_scores(text)
    
    # Determine overall sentiment
    if sentiment_scores['compound'] >= 0.05:
        overall_sentiment = 'Positive'
    elif sentiment_scores['compound'] <= -0.05:
        overall_sentiment = 'Negative'
    else:
        overall_sentiment = 'Neutral'
    
    # Add overall sentiment to the results
    sentiment_scores['overall_sentiment'] = overall_sentiment
    
    return sentiment_scores 