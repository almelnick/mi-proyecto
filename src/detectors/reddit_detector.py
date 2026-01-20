"""Reddit detector using PRAW."""

import praw
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseDetector


class RedditDetector(BaseDetector):
    """Detector for Reddit brand mentions."""

    def __init__(
        self,
        brand_keywords: List[str],
        client_id: str,
        client_secret: str,
        user_agent: str,
        subreddits: Optional[List[str]] = None
    ):
        """
        Initialize Reddit detector.

        Args:
            brand_keywords: List of keywords to search for
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
            subreddits: List of subreddits to monitor (None = all)
        """
        super().__init__(brand_keywords)

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        self.subreddits = subreddits or ['all']

    def get_platform_name(self) -> str:
        """Return platform name."""
        return 'reddit'

    def search_mentions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for brand mentions on Reddit.

        Args:
            limit: Maximum number of results per keyword

        Returns:
            List of mention dictionaries
        """
        mentions = []

        for subreddit_name in self.subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Search for each keyword
                for keyword in self.brand_keywords:
                    try:
                        # Search posts
                        for submission in subreddit.search(keyword, limit=limit, sort='new'):
                            mention = self._process_submission(submission)
                            if mention:
                                mentions.append(mention)

                        # Search comments (new comments in hot posts)
                        for submission in subreddit.hot(limit=20):
                            submission.comments.replace_more(limit=0)
                            for comment in submission.comments.list():
                                if self.contains_brand_mention(comment.body):
                                    mention = self._process_comment(comment, submission)
                                    if mention:
                                        mentions.append(mention)

                    except Exception as e:
                        print(f"Error searching for '{keyword}' in r/{subreddit_name}: {e}")
                        continue

            except Exception as e:
                print(f"Error accessing subreddit r/{subreddit_name}: {e}")
                continue

        return mentions

    def _process_submission(self, submission) -> Optional[Dict[str, Any]]:
        """Process a Reddit submission into a mention dictionary."""
        try:
            # Combine title and selftext for analysis
            full_text = f"{submission.title}\n{submission.selftext}"

            return {
                'platform': 'reddit',
                'platform_id': f"reddit_post_{submission.id}",
                'author': str(submission.author) if submission.author else '[deleted]',
                'content': full_text,
                'url': f"https://reddit.com{submission.permalink}",
                'created_at': datetime.fromtimestamp(submission.created_utc),
                'subreddit': submission.subreddit.display_name,
                'post_score': submission.score,
                'num_comments': submission.num_comments,
                'is_reply': False
            }
        except Exception as e:
            print(f"Error processing submission: {e}")
            return None

    def _process_comment(self, comment, submission) -> Optional[Dict[str, Any]]:
        """Process a Reddit comment into a mention dictionary."""
        try:
            return {
                'platform': 'reddit',
                'platform_id': f"reddit_comment_{comment.id}",
                'author': str(comment.author) if comment.author else '[deleted]',
                'content': comment.body,
                'url': f"https://reddit.com{comment.permalink}",
                'created_at': datetime.fromtimestamp(comment.created_utc),
                'subreddit': submission.subreddit.display_name,
                'post_score': comment.score,
                'num_comments': 0,
                'is_reply': True
            }
        except Exception as e:
            print(f"Error processing comment: {e}")
            return None

    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get information about a subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
                'name': subreddit.display_name,
                'subscribers': subreddit.subscribers,
                'description': subreddit.public_description,
                'active_users': subreddit.active_user_count
            }
        except Exception as e:
            return {'error': str(e)}
