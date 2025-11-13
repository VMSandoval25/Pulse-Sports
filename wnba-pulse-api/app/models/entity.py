# app/models/entity.py
from sqlalchemy import Column, BigInteger, Text, JSON
from app.core.db import Base

"""
Connects abbrevations, aliases to actual players, teams
"""

class Entity(Base):
    __tablename__ = "entities"

    id = Column(BigInteger, primary_key=True)
    type = Column(Text, nullable=False)          # 'player' | 'team'
    league = Column(Text, nullable=False)        # 'NBA'
    name = Column(Text, nullable=False)          # canonical
    short_name = Column(Text, nullable=True)
    team = Column(Text, nullable=True)                          # for players
    aliases = Column(JSON, nullable=False)       # list of strings
