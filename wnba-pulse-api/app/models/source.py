"""
Defines Source: a platform registry row (e.g., 'reddit', 'x', 'threads').
Small cardinality. Referenced by Channel and Post for platform provenance.
"""
from sqlalchemy import Column, Integer, Text
from app.core.db import Base

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
