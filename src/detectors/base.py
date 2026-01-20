"""Base detector class for platform monitoring."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseDetector(ABC):
    """Abstract base class for platform detectors."""

    def __init__(self, brand_keywords: List[str]):
        """
        Initialize detector.

        Args:
            brand_keywords: List of keywords to search for
        """
        self.brand_keywords = [kw.lower() for kw in brand_keywords]

    @abstractmethod
    def search_mentions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for brand mentions on the platform.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of mention dictionaries
        """
        pass

    def contains_brand_mention(self, text: str) -> bool:
        """
        Check if text contains any brand keywords.

        Args:
            text: Text to check

        Returns:
            True if brand mention found
        """
        if not text:
            return False

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.brand_keywords)

    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the name of the platform."""
        pass
