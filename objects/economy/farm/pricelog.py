from datetime import datetime, timedelta
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base

class PriceLog(Base):
    __tablename__ = 'farm_price_logs'

    id = Column(Integer, primary_key=True)

    refreshed_at = Column(DateTime, default=datetime.now)

    plant_id = Column(BigInteger, ForeignKey('farm_plants.id'))
    plant = relationship("Plant", back_populates="price_logs")
    price = Column(BigInteger)
    demand = Column(BigInteger)

    def __repr__(self):
        return "<PriceLog plant_name={0.plant.name}, price={0.price}>".format(self)

    @staticmethod
    def log_price(plant, session, commit_on_execution=True):
        new_price_log = PriceLog(
            plant_id = plant.id,
            price = plant.get_sell_price(raw=True),
            demand = plant.base_demand
        )
        session.add(new_price_log)
        if commit_on_execution:
            session.commit()
