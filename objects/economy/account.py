from __future__ import annotations

from datetime import datetime
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime
from sqlalchemy.orm import relationship

from objects.base import Base
from objects.economy.transaction import EconomyTransaction


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
    def get_all_economy_accounts(session):
        return session.query(EconomyAccount).all()

    @staticmethod
    def get_economy_account(user, session) -> EconomyAccount:
        user_id = user.id
        result = session.query(EconomyAccount).filter_by(user_id=user_id).first()
        if result is None:
            return EconomyAccount.create_economy_account(user, session, not user.bot)
        return result

    @staticmethod
    def create_economy_account(user, session, enabled):
        user_id = user.id
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

    def has_balance(self, amount, raw=False):
        if not raw:
            amount *= 10000
        return amount <= self.balance

    def get_balance(self):
        return self.balance / 10000 # Convert to database-friendly format

    def reconsolidate_balance(self, session, commit_on_execution=True):
        _balance = 0
        for transaction in self.transactions:
            _balance += transaction.credit
            _balance -= transaction.debit

        result = self.balance == _balance

        self.balance = _balance
        session.add(self)
        logging.info("Consolidating account of user ID: {}".format(self.user_id))
        if commit_on_execution:
            session.commit()

        return result

    def add_credit(self, session, credit_amount, name="Not specified", raw=False):
        if not raw:
            credit_amount *= 10000 # Convert to database-friendly format
        self.balance += credit_amount
        self.transactions.append(
            EconomyTransaction(name=name, credit=credit_amount)
        )
        session.add(self)
        session.commit()

    def add_debit(self, session, debit_amount, name="Not specified", raw=False):
        if not raw:
            debit_amount *= 10000 # Convert to database-friendly format
        self.balance -= debit_amount
        self.transactions.append(
            EconomyTransaction(name=name, debit=debit_amount)
        )
        session.add(self)
        session.commit()
