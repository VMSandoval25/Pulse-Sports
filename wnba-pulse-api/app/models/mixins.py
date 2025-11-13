"""
Defines SocialFieldsMixin to DRY shared social-content columns used by Post and Comment.
Columns: external_id, author, body, score, created_at, collected_at, raw_payload.
"""
from sqlalchemy import Column, Text, Integer, DateTime, JSON

class SocialFieldsMixin:
    external_id = Column(Text, nullable=False)      # platform-native id
    author = Column(Text)                           # username/display at ingest time
    body = Column(Text)                             # text body (post body or comment body)
    score = Column(Integer)                         # point-in-time engagement score
    created_at = Column(DateTime(timezone=True))    # platform creation time (aware)
    collected_at = Column(DateTime(timezone=True))  # time we ingested the record
    raw_payload = Column(JSON)                      # original source payload for audits/debug
