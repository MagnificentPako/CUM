from models.base import Base
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Float, ForeignKey, Boolean

class CorpWalletEntry(Base):
    __tablename__ = "corp_wallet"

    id = Column(BigInteger, primary_key=True)
    amount = Column(BigInteger)
    balance = Column(Float)
    context_id = Column(BigInteger)
    context_id_type = Column(String)
    date = Column(DateTime)
    description = Column(String)
    first_party_id = Column(BigInteger, primary_key=True)
    reason = Column(String)
    ref_type = Column(String)
    second_party_id = Column(BigInteger, primary_key=True)
    source = Column(String)