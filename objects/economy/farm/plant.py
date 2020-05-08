from datetime import datetime
from random import randint
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime

from objects.base import Base
from objects.economy.farm.pricelog import PriceLog


class Plant(Base):
    __tablename__ = 'farm_plants'

    id = Column(Integer, primary_key=True)

    name = Column(String(64), unique=True) # Turnip
    buy_price = Column(BigInteger) # 50000
    base_harvest = Column(Integer) # 10

    base_sell_price = Column(BigInteger) # 20000
    current_sell_price = Column(BigInteger) # Set dynamically
    randomness_factor = Column(BigInteger) # / 10000

    growing_seconds = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def get_plants(session):
        all_plants = session.query(Plant).order_by(Plant.buy_price).all()
        return all_plants

    @staticmethod
    def get_plant(session, name):
        plant = session.query(Plant).filter(Plant.name.ilike(name)).first()
        return plant
    
    def get_buy_price(self):
        return self.buy_price / 10000
    
    def get_sell_price(self):
        return self.current_sell_price / 10000

    def randomize_price(self, session, commit_on_execution=True):
        _r = self.randomness_factor
        factor = randint(10000-_r, 10000+_r) / 10000
        self.current_sell_price = int(self.base_sell_price*factor)
        session.add(self)
        PriceLog.log_price(self, session, commit_on_execution=commit_on_execution)
        if commit_on_execution:
            session.commit()

    def set_base_price(self, session, price, raw=False):
        if not raw:
            price *= 10000
        self.base_sell_price = price
        session.add(self)
        session.commit()
