import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', 'http://localhost:3030').rstrip('/')
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url', 'http://localhost:5050/'
).rstrip('/') + '/'


def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint
    try:
        response = requests.get(request_url, params=kwargs or None, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"GET request failed for {request_url}: {exc}")
        return []


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + 'analyze/' + quote(str(text), safe='')
    try:
        response = requests.get(request_url, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"Sentiment request failed for {request_url}: {exc}")
        return {'sentiment': 'neutral'}


def post_review(data_dict):
    request_url = backend_url + '/insert_review'
    try:
        response = requests.post(request_url, json=data_dict, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"POST request failed for {request_url}: {exc}")
        raise
