from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from config import *
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
    def get_top_farms(session, number=10):
        all_farms = session.query(Farm).all()
        all_farms = sorted(all_farms, key=lambda x:len(x.plots), reverse=True)
        return all_farms[:number]
    
    @staticmethod
    def get_all_farms(session):
        return session.query(Farm).all()

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

    def get_next_plot_price(self, raw=False, up_count=1):
        plot_count = self.get_plot_count() - 2
        plot_price = 0
        to_max_plots = FARM_PLOTS_MAX - plot_count
        if to_max_plots == 0:
            return 0
        up_count = min(up_count, to_max_plots)
        for i in range(plot_count, plot_count+up_count):
            plot_price += int( BASE_PLOT_PRICE * (i ** PLOT_PRICE_FACTOR) )
        if not raw:
            return plot_price / 10000
        return plot_price

    def get_next_storage_upgrade_price(self, raw=False, up_count=1):
        silo_count = int( self.harvest_capacity / 100 )
        silo_price = 0
        for i in range(up_count):
            silo_price += int( BASE_STORAGE_UPGRADE_PRICE * ((silo_count+i) ** STORAGE_UPGRADE_PRICE_FACTOR) )
        if not raw:
            return silo_price / 10000
        return silo_price

    def has_storage(self, amount):
        return (self.current_harvest + amount <= self.harvest_capacity)

    def decrease_storage(self, session, amount):
        self.current_harvest = max(self.current_harvest - amount, 0)
        session.add(self)
        session.commit()

    def upgrade_storage(self, session, up_count=1):
        self.harvest_capacity += 100 * (up_count)
        session.add(self)
        session.commit()

    def add_plot(self, session, up_count=1):
        self.plots += [Plot() for i in range(up_count)]
        session.add(self)
        session.commit()
