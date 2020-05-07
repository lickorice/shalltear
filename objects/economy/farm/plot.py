from datetime import datetime
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime

from objects.base import Base


class Plot(Base):
    __tablename__ = 'economy_accounts'

    id = Column(Integer, primary_key=True)
