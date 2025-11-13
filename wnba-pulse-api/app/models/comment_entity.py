# app/models/comment_entity.py
from sqlalchemy import Column, BigInteger, ForeignKey
from app.core.db import Base

"""
Builds relationship between comment and entity
"""

class CommentEntity(Base):
    __tablename__ = "comment_entities"
    comment_id = Column(BigInteger, ForeignKey("comments.id"), primary_key=True)
    entity_id = Column(BigInteger, ForeignKey("entities.id"), primary_key=True)
