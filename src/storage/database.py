"""Database module for storing brand mentions."""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional

Base = declarative_base()


class Mention(Base):
    """Model for storing brand mentions."""

    __tablename__ = 'mentions'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # reddit, twitter, etc.
    platform_id = Column(String(255), unique=True, nullable=False)  # unique ID from platform
    author = Column(String(255))
    content = Column(Text)
    url = Column(String(500))
    created_at = Column(DateTime)
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Sentiment analysis
    sentiment_score = Column(Float)  # -1.0 to 1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral

    # Link detection
    has_links = Column(Boolean, default=False)
    extracted_links = Column(Text)  # JSON array of links

    # Metadata
    subreddit = Column(String(255))  # for Reddit
    post_score = Column(Integer)  # upvotes/likes
    num_comments = Column(Integer)
    is_reply = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Mention(platform='{self.platform}', author='{self.author}', sentiment='{self.sentiment_label}')>"


class Database:
    """Database manager for brand mentions."""

    def __init__(self, db_path: str = "brand_mentions.db"):
        """Initialize database connection."""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_mention(self, mention: Mention) -> bool:
        """Add a new mention to the database."""
        try:
            # Check if mention already exists
            existing = self.session.query(Mention).filter_by(
                platform_id=mention.platform_id
            ).first()

            if existing:
                return False  # Already exists

            self.session.add(mention)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error adding mention: {e}")
            return False

    def get_recent_mentions(self, limit: int = 50) -> List[Mention]:
        """Get most recent mentions."""
        return self.session.query(Mention).order_by(
            Mention.detected_at.desc()
        ).limit(limit).all()

    def get_mentions_by_sentiment(self, sentiment: str, limit: int = 50) -> List[Mention]:
        """Get mentions filtered by sentiment."""
        return self.session.query(Mention).filter_by(
            sentiment_label=sentiment
        ).order_by(Mention.detected_at.desc()).limit(limit).all()

    def get_mentions_with_links(self, limit: int = 50) -> List[Mention]:
        """Get mentions that contain links."""
        return self.session.query(Mention).filter_by(
            has_links=True
        ).order_by(Mention.detected_at.desc()).limit(limit).all()

    def get_stats(self) -> dict:
        """Get statistics about mentions."""
        total = self.session.query(Mention).count()
        positive = self.session.query(Mention).filter_by(sentiment_label='positive').count()
        negative = self.session.query(Mention).filter_by(sentiment_label='negative').count()
        neutral = self.session.query(Mention).filter_by(sentiment_label='neutral').count()
        with_links = self.session.query(Mention).filter_by(has_links=True).count()

        return {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'with_links': with_links
        }

    def close(self):
        """Close database connection."""
        self.session.close()
