from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from config import BASE_PLOT_PRICE, PLOT_PRICE_FACTOR
from objects.base import Base
from objects.economy.farm.plot import Plot


class Farm(Base):
    __tablename__ = 'farm_farms'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)

    name = Column(String(32), default="Unnamed Farm")

    current_harvest = Column(BigInteger, default=0)
    harvest_capacity = Column(BigInteger, default=100)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    harvests = relationship("Harvest", back_populates="farm", cascade="all, delete, delete-orphan")
    plots = relationship("Plot", back_populates="farm")

    def __repr__(self):
        return "<Farm id={0.id}, user_id={0.id}, plots={0.plots}>".format(self)\

    @staticmethod
    def get_farms_count(session):
        return session.query(Farm).count()

    @staticmethod
    def create_farm(user, session):
        user_id = user.id
        new_farm = Farm(
            user_id = user_id,
        )
        new_farm.plots = [
            Plot(), Plot(), Plot() # Default 3 plots
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

    def get_name(self, session):
        if self.name is None:
            self.name = "Unnamed Farm"
            self.bot.db_session.add(self)
            self.bot.db_session.commit()
        return self.name

    def get_all_plots(self, session):
        return self.plots

    def get_available_plots(self, session):
        results = [i for i in self.plots if i.plant is None]
        return results

    def get_plot_count(self):
        return len(self.plots)

    def get_next_plot_price(self, raw=False):
        plot_count = self.get_plot_count() - 2
        plot_price = int( BASE_PLOT_PRICE * (plot_count ** PLOT_PRICE_FACTOR) )
        if not raw:
            return plot_price / 10000
        return plot_price

    def add_plot(self, session):
        self.plots.append(Plot())
        session.add(self)
        session.commit()
