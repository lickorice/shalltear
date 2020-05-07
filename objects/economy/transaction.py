from datetime import datetime

from sqlalchemy import Table, Column, Integer, BigInteger, MetaData, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from objects.base import Base


class EconomyTransaction(Base):
    __tablename__ = 'economy_transactions'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), default="Not specified")
    credit = Column(BigInteger, default=0)
    debit = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    account_id = Column(BigInteger, ForeignKey('economy_accounts.id'))

    account = relationship("EconomyAccount", back_populates="transactions")

    def __repr__(self):
        return "<Transaction id={0.id},>".format(self)
