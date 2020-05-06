from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime
from sqlalchemy.orm import relationship

from objects.base import Base
from objects.economy_transaction import EconomyTransaction


class EconomyAccount(Base):
    __tablename__ = 'economy_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    balance = Column(BigInteger)
    enabled = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    transactions = relationship("EconomyTransaction", back_populates="account")

    def __repr__(self):
        return "<User id={0.id}, enabled={0.enabled}, balance={0.balance}>".format(self)

    @staticmethod
    def get_economy_account(user_id, session):
        return session.query(EconomyAccount).filter_by(user_id=user_id).first()

    @staticmethod
    def create_economy_account(user_id, session, enabled):
        new_account = EconomyAccount(
            user_id = user_id,
            balance = 100000,
            enabled = enabled,
        )
        new_account.transactions = [
            EconomyTransaction(name="Initial Balance", credit=100000)
        ]
        session.add(new_account)
        session.commit()
        return new_account

    def get_balance(self):
        return self.balance / 10000 # Convert to database-friendly format

    def add_credit(self, session, credit_amount, name="Not specified"):
        credit_amount *= 10000 # Convert to database-friendly format
        print(self.balance, type(self.balance))
        self.balance += credit_amount
        self.transactions.append(
            EconomyTransaction(name=name, credit=credit_amount)
        )
        session.add(self)
        session.commit()

    def add_debit(self, session, debit_amount, name="Not specified"):
        debit_amount *= 10000 # Convert to database-friendly format
        self.balance -= debit_amount
        self.transactions.append(
            EconomyTransaction(name=name, debit=debit_amount)
        )
        session.add(self)
        session.commit()