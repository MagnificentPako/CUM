from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from models.base import Base

class ItemType(Base):
    __tablename__ = 'item_types'

    id = Column(Integer, primary_key=True)
    category = Column(String)
    name = Column(String)