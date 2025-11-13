"""
Defines Comment: a reaction node on a Post.
Uses SocialFieldsMixin; supports threading via parent_comment_id and depth (1 = top-level reply).
"""
from sqlalchemy import Column, BigInteger, Integer, Text, ForeignKey, UniqueConstraint, Index
from app.core.db import Base
from .mixins import SocialFieldsMixin

class Comment(SocialFieldsMixin, Base):
    __tablename__ = "comments"
    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    parent_comment_id = Column(BigInteger, ForeignKey("comments.id", ondelete="CASCADE"))
    parent_external_id = Column(Text)     # used during ingest/resolve step
    depth = Column(Integer, nullable=True, default=1)  # 1 = top-level under post

    __table_args__ = (
        UniqueConstraint("post_id", "external_id", name="uq_comment_post_ext"),
        Index("ix_comments_post_id", "post_id"),
        Index("ix_comments_parent_comment_id", "parent_comment_id"),
        Index("ix_comments_created_at", "created_at"),
    )
