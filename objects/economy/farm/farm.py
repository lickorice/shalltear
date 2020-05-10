from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from config import *
from objects.base import Base
from objects.economy.farm.plot import Plot
from objects.economy.farm.upgrade import Upgrade


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
    upgrades = relationship("Upgrade", back_populates="farm", lazy="dynamic")

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
        new_farm.upgrades = []
        for UPGRADE in FARM_UPGRADES:
            new_farm.upgrades.append(Upgrade(
                name=UPGRADE, 
                base_price=FARM_UPGRADES[UPGRADE]["base"],
                upgrade_type=FARM_UPGRADES[UPGRADE]["type"]
            ))
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

    def get_price_multiplier(self):
        base_factor = 1
        for _upgrade in self.upgrades.filter(Upgrade.upgrade_type=="prices").all():
            base_factor *= (1+(0.05*_upgrade.level))
        return base_factor

    def get_harvest_multiplier(self):
        base_factor = 1
        for _upgrade in self.upgrades.filter(Upgrade.upgrade_type=="harvests").all():
            base_factor *= (1+(0.05*_upgrade.level))
        return base_factor

    def get_storage_multiplier(self):
        base_factor = 1
        for _upgrade in self.upgrades.filter(Upgrade.upgrade_type=="storage").all():
            base_factor *= (1+(0.05*_upgrade.level))
        return base_factor

    def upgrade(self, session, upgrade_name, up_count=1):
        _upgrade = self.upgrades.filter(Upgrade.name==upgrade_name).first()
        _upgrade.level += up_count
        session.add(_upgrade)
        session.commit()
    
    def get_upgrade_cost(self, upgrade_name, raw=False, up_count=1):
        _upgrade = self.upgrades.filter(Upgrade.name==upgrade_name).first()
        return _upgrade.get_next_level_cost(raw=raw, up_count=up_count)

    def get_name(self, session):
        if self.name is None:
            self.name = "Unnamed Farm"
            self.bot.db_session.add(self)
            self.bot.db_session.commit()
        return self.name

    def get_harvest_capacity(self):
        return int(self.harvest_capacity * self.get_storage_multiplier())

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

    def get_next_storage_upgrade_price(self, raw=False):
        silo_count = int( self.harvest_capacity / 100 )
        silo_price = int( BASE_STORAGE_UPGRADE_PRICE * (silo_count ** STORAGE_UPGRADE_PRICE_FACTOR) )
        if not raw:
            return silo_price / 10000
        return silo_price

    def has_storage(self, amount):
        return (self.current_harvest + amount <= self.get_harvest_capacity())

    def decrease_storage(self, session, amount):
        self.current_harvest = max(self.current_harvest - amount, 0)
        session.add(self)
        session.commit()

    def upgrade_storage(self, session):
        self.harvest_capacity += 100
        session.add(self)
        session.commit()

    def add_plot(self, session):
        self.plots.append(Plot())
        session.add(self)
        session.commit()
