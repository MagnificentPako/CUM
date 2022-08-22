from sqlalchemy import Column, String, Integer, DateTime
from models.base import Base

class Character(Base):
    __tablename__ = 'char_tokens'

    id = Column(String, primary_key=True)
    token_type = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    character_id = Column(Integer)
    expires_at = Column(Integer)

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )