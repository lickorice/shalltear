from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base
from objects.economy.farm.plot import Plot


class Farm(Base):
    __tablename__ = 'farm_farms'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)

    current_harvest = Column(BigInteger, default=0)
    harvest_capacity = Column(BigInteger, default=100)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    harvests = relationship("Harvest", back_populates="farm")
    plots = relationship("Plot", back_populates="farm")

    def __repr__(self):
        return "<Farm id={0.id}, user_id={0.id}, plots={0.plots}>".format(self)\

    @staticmethod
    def create_farm(user, session):
        user_id = user.id
        new_farm = Farm(
            user_id = user_id,
        )
        new_farm.plots = [
            Plot()
        ]
        session.add(new_farm)
        session.commit()
        return new_farm

    @staticmethod
    def get_farm(user, session):
        user_id = user.id
        result = session.query(Farm).filter_by(user_id=user_id).first()
        if result is None:
            return Farm.create_farm(user, session)
        return result

    def get_all_plots(self, session):
        return self.plots

    def get_available_plot(self, session):
        results = [i for i in self.plots if i.plant is None]
        if (len(results)) is 0:
            return None
        return results[0]
