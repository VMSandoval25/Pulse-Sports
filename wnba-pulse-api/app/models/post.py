"""
Defines Post: a top-level social item (thread/tweet/post).
Uses SocialFieldsMixin; links to Source (platform) and Channel (community/account).
Stores canonical_url for platform-agnostic linking and comment_count for quick rollups.
"""
from sqlalchemy import Column, BigInteger, Integer, Text, JSON, ForeignKey, UniqueConstraint, Index
from app.core.db import Base
from .mixins import SocialFieldsMixin

class Post(SocialFieldsMixin, Base):
    __tablename__ = "posts"
    id = Column(BigInteger, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    channel_id = Column(BigInteger, ForeignKey("channels.id"))

    title = Column(Text, nullable=False)
    canonical_url = Column(Text)          # platform-agnostic "open" URL
    comment_count = Column(Integer)

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_post_src_ext"),
        Index("ix_posts_created_at", "created_at"),
        Index("ix_posts_channel_id", "channel_id"),
    )
