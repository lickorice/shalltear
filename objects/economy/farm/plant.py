from datetime import datetime
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime

from objects.base import Base


class Plant(Base):
    __tablename__ = 'farm_plants'

    id = Column(Integer, primary_key=True)

    name = Column(String(64)) # Turnip
    buy_price = Column(BigInteger) # 50000
    base_sell_price = Column(BigInteger) # 500000
    current_sell_price = Column(BigInteger) # Set dynamically
    randomness_factor = Column(BigInteger) # / 10000

    growing_seconds = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
