"""Sentiment analysis module using VADER."""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Tuple


class SentimentAnalyzer:
    """Analyzes sentiment of text content."""

    def __init__(self):
        """Initialize VADER sentiment analyzer."""
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (compound_score, label)
            compound_score: -1.0 (most negative) to 1.0 (most positive)
            label: 'positive', 'negative', or 'neutral'
        """
        if not text:
            return 0.0, 'neutral'

        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']

        # Classify based on compound score
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'

        return compound, label

    def get_detailed_scores(self, text: str) -> dict:
        """
        Get detailed sentiment scores.

        Returns:
            Dictionary with neg, neu, pos, and compound scores
        """
        if not text:
            return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}

        return self.analyzer.polarity_scores(text)
