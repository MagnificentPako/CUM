from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import declarative_base
from models.base import Base

class StationMarketEntry(Base):
    __tablename__ = 'station_market'

    id = Column(BigInteger, primary_key=True)
    duration = Column(BigInteger)
    is_buy_order = Column(Boolean)
    issued = Column(DateTime)
    location_id = Column(BigInteger)
    min_volume = Column(BigInteger)
    order_id = Column(BigInteger)
    price = Column(Float)
    range = Column(String)
    type_id = Column(BigInteger, ForeignKey('item_types.id'))
    volume_remain = Column(BigInteger)
    volume_total = Column(BigInteger)
    source_char = Column(String, ForeignKey('char_tokens.id'))
    iteration = Column(BigInteger)