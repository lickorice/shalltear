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

    plot_capacity = Column(Integer, default=3)

    harvests = relationship("Harvest", back_populates="farm", cascade="all, delete, delete-orphan")
    plots = relationship("Plot", back_populates="farm", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Farm id={0.id}, user_id={0.id}, plots={0.plots}>".format(self)\

    @staticmethod
    def get_all_farms_count(session):
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

    def get_all_plots(self):
        return self.plots

    def get_used_plot_count(self):
        return sum(_plot.plot_range for _plot in self.plots)

    def get_free_plot_count(self):
        return self.plot_capacity - self.get_used_plot_count()

    def get_plot_count(self):
        return self.plot_capacity

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
        self.plot_capacity += up_count
        session.add(self)
        session.commit()

    def has_plots(self, plot_range):
        return plot_range <= self.get_free_plot_count()

    def plant_crop(self, _plant, session, plot_range=1, commit_on_execution=True):
        if not self.has_plots(plot_range):
            raise Exception("Plot capacity not enough. {0} => {1}".format(
                plot_range, self.get_free_plot_count()
            ))
        new_plot = Plot(
            plant_id=_plant.id,
            planted_at=datetime.now(),
            plot_range=plot_range
        )
        self.plots.append(new_plot)
        session.add(self)
        if commit_on_execution:
            session.commit()

