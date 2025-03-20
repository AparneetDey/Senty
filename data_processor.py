import pandas as pd
from sentiment_analyzer import analyze_sentiment

def process_excel_file(filepath):
    """
    Process an Excel or CSV file containing reviews and analyze sentiment for each review.
    Returns a summary of the sentiment analysis.
    """
    # Read the file based on its extension
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    
    # Assuming the first column contains the reviews
    review_column = df.columns[0]
    
    # Analyze sentiment for each review
    results = []
    for review in df[review_column]:
        if pd.notna(review):  # Check if the review is not NaN
            sentiment_result = analyze_sentiment(str(review))
            results.append(sentiment_result)
    
    # Calculate summary statistics
    total_reviews = len(results)
    positive_count = sum(1 for r in results if r['overall_sentiment'] == 'Positive')
    negative_count = sum(1 for r in results if r['overall_sentiment'] == 'Negative')
    neutral_count = sum(1 for r in results if r['overall_sentiment'] == 'Neutral')
    
    # Calculate average compound score
    avg_compound = sum(r['compound'] for r in results) / total_reviews if total_reviews > 0 else 0
    
    return {
        'summary': {
            'total_reviews': total_reviews,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'average_sentiment': avg_compound
        },
        'detailed_results': results
    } 