# Sentiment Analysis Web Application

A web application that performs sentiment analysis on text input and CSV files using TextBlob. Built with Flask and designed for deployment on Vercel.

## Features

- Text-based sentiment analysis
- CSV file upload and analysis
- Word cloud visualization
- Beautiful and responsive UI
- Real-time analysis results

## Requirements

- Python 3.9+
- Flask
- TextBlob
- NLTK
- pandas
- Other dependencies listed in `requirements.txt`

## Local Development

1. Clone the repository:
```bash
git clone <your-repo-url>
cd sentiment-analysis
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open http://localhost:5000 in your browser

## Deployment on Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

## File Upload Format

For CSV file analysis, ensure your file has a column containing text reviews. The application will automatically detect and analyze the first text column in the file.

## License

MIT 