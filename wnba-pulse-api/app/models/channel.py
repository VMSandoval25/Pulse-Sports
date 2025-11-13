"""
Defines Channel: a community/account/feed within a Source.
Examples: Reddit subreddit ('r/nba'), X account ('@NBA'), Threads profile ('nba').
Posts link here via channel_id; uniqueness by (source_id, external_id).
"""
from sqlalchemy import Column, BigInteger, Integer, Text, JSON, ForeignKey, UniqueConstraint, Index
from app.core.db import Base

class Channel(Base):
    __tablename__ = "channels"
    id = Column(BigInteger, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    external_id = Column(Text)            # subreddit name, user id, etc.
    handle = Column(Text)                 # "r/nba", "@NBA", etc.
    display_name = Column(Text)           # Human-friendly name
    metadata_json = Column(JSON)               # Source-specific extras
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_channel_src_ext"),
        Index("ix_channels_handle", "handle"),
    )
