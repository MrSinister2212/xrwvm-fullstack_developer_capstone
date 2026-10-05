from flask import Flask, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import os

app = Flask("Sentiment Analyzer")

# The repository includes sentiment/vader_lexicon.zip under this directory.
# Add this directory as an NLTK data root so NLTK can resolve
# sentiment/vader_lexicon.zip correctly.
nltk.data.path.append(os.path.dirname(__file__))

sia = SentimentIntensityAnalyzer()


@app.get('/')
def home():
    return "Welcome to the Sentiment Analyzer. Use /analyze/text to get the sentiment"


@app.get('/analyze/<path:input_txt>')
def analyze_sentiment(input_txt):
    scores = sia.polarity_scores(input_txt)
    compound = scores['compound']

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return jsonify({"sentiment": sentiment})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
