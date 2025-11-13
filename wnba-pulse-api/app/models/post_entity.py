# app/models/post_entity.py
from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from app.core.db import Base

"""
Builds the relationship between a Post id and an Entity ID
Will later be able to query using post id and filter which entites were mentioned 
(more than one entity can be mentioned in a post)
"""

class PostEntity(Base):
    __tablename__ = "post_entities"

    post_id = Column(BigInteger, ForeignKey("posts.id"), primary_key=True)
    entity_id = Column(BigInteger, ForeignKey("entities.id"), primary_key=True)
