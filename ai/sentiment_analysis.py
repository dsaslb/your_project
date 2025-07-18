from transformers import pipeline

sentiment = pipeline("sentiment-analysis", model="snunlp/KR-FinBert-SC")


def analyze_review_sentiment(text):
    result = sentiment(text)
    return result[0]["label"]  # 'positive', 'negative', 'neutral'
