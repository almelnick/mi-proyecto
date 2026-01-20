"""Link detection and analysis module."""

import re
import json
from typing import List, Dict
from urllib.parse import urlparse


class LinkAnalyzer:
    """Analyzes and extracts links from text."""

    # Regex pattern for URLs
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    def __init__(self):
        """Initialize link analyzer."""
        pass

    def extract_links(self, text: str) -> List[str]:
        """
        Extract all URLs from text.

        Args:
            text: Text to search for URLs

        Returns:
            List of URLs found
        """
        if not text:
            return []

        return self.URL_PATTERN.findall(text)

    def analyze_links(self, text: str) -> Dict:
        """
        Analyze links in text and return detailed information.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with link analysis
        """
        links = self.extract_links(text)

        if not links:
            return {
                'has_links': False,
                'count': 0,
                'links': [],
                'domains': []
            }

        # Extract domains
        domains = []
        for link in links:
            try:
                parsed = urlparse(link)
                if parsed.netloc:
                    domains.append(parsed.netloc)
            except:
                pass

        return {
            'has_links': True,
            'count': len(links),
            'links': links,
            'domains': list(set(domains))  # unique domains
        }

    def links_to_json(self, links: List[str]) -> str:
        """Convert list of links to JSON string for storage."""
        return json.dumps(links)

    def links_from_json(self, json_str: str) -> List[str]:
        """Convert JSON string back to list of links."""
        try:
            return json.loads(json_str)
        except:
            return []

    def contains_competitor_links(self, text: str, competitor_domains: List[str]) -> bool:
        """
        Check if text contains links to competitor domains.

        Args:
            text: Text to check
            competitor_domains: List of competitor domain names

        Returns:
            True if competitor links found
        """
        analysis = self.analyze_links(text)

        if not analysis['has_links']:
            return False

        for domain in analysis['domains']:
            for competitor in competitor_domains:
                if competitor.lower() in domain.lower():
                    return True

        return False
