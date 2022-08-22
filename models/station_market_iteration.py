from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from models.base import Base

class StationMarketIteration(Base):
    __tablename__ = 'station_market_iterations'

    source_char = Column(String,  ForeignKey('char_tokens.id'), primary_key=True)
    iteration = Column(Integer, primary_key=True)