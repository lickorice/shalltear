from datetime import datetime, timedelta
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base
from objects.economy.farm.harvest import Harvest


class Plot(Base):
    __tablename__ = 'farm_plots'

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    farm_id = Column(BigInteger, ForeignKey('farm_farms.id'))
    farm = relationship("Farm", back_populates="plots")

    plant_id = Column(BigInteger, ForeignKey('farm_plants.id'))
    plant = relationship("Plant")

    planted_at = Column(DateTime, default=None)

    def __repr__(self):
        return "<Plot plant={0.plant}, planted_at={0.planted_at}>".format(self)

    def plant_to_plot(self, _plant, session):
        self.plant = _plant
        self.planted_at = datetime.now()
        session.add(self)
        session.commit()
    
    def get_status_str(self):
        status_str = ""
        if self.plant is None:
            status_str += "No plant currently planted."
            return status_str
        status_str += "Currently planted: {}\n".format(self.plant.name)
        status_str += "Expected yield: {} units\n".format(self.plant.base_harvest)
        status_str += "{}\n".format(self.get_remaining_harvest_time())
        return status_str

    def is_harvestable(self):
        if self.plant is None: return False
        harvest_datetime = self.planted_at + timedelta(seconds=self.plant.growing_seconds)
        time_difference = harvest_datetime - datetime.now()
        return time_difference < timedelta()

    def get_remaining_harvest_time(self):
        harvest_datetime = self.planted_at + timedelta(seconds=self.plant.growing_seconds)
        time_difference = harvest_datetime - datetime.now()
        if time_difference < timedelta():
            return "Can now be harvested."
        result_str = []
        hours, rem = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        if time_difference.days:
            result_str.append("{}d".format(time_difference.days))
        if hours:
            result_str.append("{}h".format(hours))
        if minutes:
            result_str.append("{}m".format(minutes))
        if seconds:
            result_str.append("{}s".format(seconds))
        return "Can be harvested in {}".format(', '.join(result_str))

    def get_harvest(self, session):
        new_harvest = Harvest(
            amount = self.plant.base_harvest,
            plant = self.plant,
            farm = self.farm,
        )
        self.plant = None
        self.planted_at = None
        session.add(self)
        session.add(new_harvest)
        return new_harvest
