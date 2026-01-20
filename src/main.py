#!/usr/bin/env python3
"""
Brand Mention Detector - Main CLI
Detecta menciones de tu marca en Reddit con análisis de sentimiento y links.
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
from typing import List

from .storage.database import Database, Mention
from .analyzers.sentiment import SentimentAnalyzer
from .analyzers.link_analyzer import LinkAnalyzer
from .detectors.reddit_detector import RedditDetector
from .notifiers.console_notifier import ConsoleNotifier


class BrandMentionDetector:
    """Main application class."""

    def __init__(self):
        """Initialize the brand mention detector."""
        # Load environment variables
        load_dotenv()

        # Get configuration
        self.brand_name = os.getenv('BRAND_NAME', 'YourBrand')
        brand_keywords_str = os.getenv('BRAND_KEYWORDS', self.brand_name)
        self.brand_keywords = [kw.strip() for kw in brand_keywords_str.split(',')]

        # Initialize components
        self.db = Database()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.link_analyzer = LinkAnalyzer()
        self.notifier = ConsoleNotifier()

        # Initialize Reddit detector if credentials available
        self.reddit_detector = None
        self._init_reddit_detector()

    def _init_reddit_detector(self):
        """Initialize Reddit detector with credentials."""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'BrandMentionDetector/1.0')

        if not client_id or not client_secret:
            self.notifier.display_warning(
                "Reddit credentials not found. Please configure .env file."
            )
            return

        subreddits_str = os.getenv('BRAND_SUBREDDITS', 'all')
        subreddits = [s.strip() for s in subreddits_str.split(',')]

        try:
            self.reddit_detector = RedditDetector(
                brand_keywords=self.brand_keywords,
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                subreddits=subreddits
            )
            self.notifier.display_success("Reddit detector initialized successfully")
        except Exception as e:
            self.notifier.display_error(f"Failed to initialize Reddit detector: {e}")

    def scan_reddit(self, limit: int = 100, notify: bool = True):
        """
        Scan Reddit for brand mentions.

        Args:
            limit: Maximum results per search
            notify: Whether to display notifications
        """
        if not self.reddit_detector:
            self.notifier.display_error("Reddit detector not initialized")
            return

        self.notifier.display_info(f"Scanning Reddit for mentions of: {', '.join(self.brand_keywords)}")

        try:
            # Search for mentions
            raw_mentions = self.reddit_detector.search_mentions(limit=limit)

            self.notifier.display_info(f"Found {len(raw_mentions)} potential mentions")

            # Process and store mentions
            new_count = 0
            for raw_mention in raw_mentions:
                # Analyze sentiment
                sentiment_score, sentiment_label = self.sentiment_analyzer.analyze(
                    raw_mention['content']
                )

                # Analyze links
                link_analysis = self.link_analyzer.analyze_links(raw_mention['content'])

                # Create mention object
                mention = Mention(
                    platform=raw_mention['platform'],
                    platform_id=raw_mention['platform_id'],
                    author=raw_mention['author'],
                    content=raw_mention['content'],
                    url=raw_mention['url'],
                    created_at=raw_mention['created_at'],
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    has_links=link_analysis['has_links'],
                    extracted_links=self.link_analyzer.links_to_json(link_analysis['links']),
                    subreddit=raw_mention.get('subreddit'),
                    post_score=raw_mention.get('post_score', 0),
                    num_comments=raw_mention.get('num_comments', 0),
                    is_reply=raw_mention.get('is_reply', False)
                )

                # Add to database
                if self.db.add_mention(mention):
                    new_count += 1
                    if notify:
                        self.notifier.notify_new_mention(mention)

            self.notifier.display_success(f"Added {new_count} new mentions to database")

        except Exception as e:
            self.notifier.display_error(f"Error scanning Reddit: {e}")

    def show_recent(self, limit: int = 20):
        """Show recent mentions."""
        mentions = self.db.get_recent_mentions(limit=limit)

        if not mentions:
            self.notifier.display_info("No mentions found")
            return

        self.notifier.display_mentions_table(mentions, f"Recent {limit} Mentions")

    def show_by_sentiment(self, sentiment: str, limit: int = 20):
        """Show mentions by sentiment."""
        mentions = self.db.get_mentions_by_sentiment(sentiment, limit=limit)

        if not mentions:
            self.notifier.display_info(f"No {sentiment} mentions found")
            return

        self.notifier.display_mentions_table(
            mentions,
            f"{sentiment.capitalize()} Mentions"
        )

    def show_with_links(self, limit: int = 20):
        """Show mentions that contain links."""
        mentions = self.db.get_mentions_with_links(limit=limit)

        if not mentions:
            self.notifier.display_info("No mentions with links found")
            return

        self.notifier.display_mentions_table(mentions, "Mentions with Links")

    def show_stats(self):
        """Show statistics."""
        stats = self.db.get_stats()
        self.notifier.display_stats(stats)

    def close(self):
        """Close database connection."""
        self.db.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Brand Mention Detector - Monitor your brand across social platforms'
    )

    parser.add_argument(
        'command',
        choices=['scan', 'recent', 'positive', 'negative', 'neutral', 'links', 'stats'],
        help='Command to execute'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of results (default: 50)'
    )

    parser.add_argument(
        '--no-notify',
        action='store_true',
        help='Disable notifications during scan'
    )

    args = parser.parse_args()

    # Initialize detector
    detector = BrandMentionDetector()

    try:
        if args.command == 'scan':
            detector.scan_reddit(limit=args.limit, notify=not args.no_notify)
        elif args.command == 'recent':
            detector.show_recent(limit=args.limit)
        elif args.command == 'positive':
            detector.show_by_sentiment('positive', limit=args.limit)
        elif args.command == 'negative':
            detector.show_by_sentiment('negative', limit=args.limit)
        elif args.command == 'neutral':
            detector.show_by_sentiment('neutral', limit=args.limit)
        elif args.command == 'links':
            detector.show_with_links(limit=args.limit)
        elif args.command == 'stats':
            detector.show_stats()
    finally:
        detector.close()


if __name__ == '__main__':
    main()
