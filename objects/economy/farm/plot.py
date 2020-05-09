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

    @staticmethod
    def get_plots_count(session):
        return session.query(Plot).count()

    def plant_to_plot(self, _plant, session, commit_on_execution=True):
        self.plant = _plant
        self.planted_at = datetime.now()
        session.add(self)
        if commit_on_execution:
            session.commit()
    
    def get_status_str(self):
        if self.plant is None:
            return "-- EMPTY --"
        return "{0} -- {1}".format(self.plant.tag, self.get_remaining_harvest_time())

    def is_harvestable(self):
        if self.plant is None: return False
        harvest_datetime = self.planted_at + timedelta(seconds=self.plant.growing_seconds)
        time_difference = harvest_datetime - datetime.now()
        return time_difference < timedelta()

    def get_remaining_harvest_time(self):
        harvest_datetime = self.planted_at + timedelta(seconds=self.plant.growing_seconds)
        time_difference = harvest_datetime - datetime.now()
        if time_difference < timedelta():
            return "[HARVEST NOW]"
        result_str = []
        hours, rem = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        first_digit = True
        if time_difference.days:
            result_str.append("{}d".format(time_difference.days))
            first_digit = False
        if not first_digit or hours:
            result_str.append("{}h".format(hours))
            first_digit = False
        if not first_digit or  minutes:
            result_str.append("{}m".format(minutes))
            first_digit = False
        if not first_digit or  seconds:
            result_str.append("{}s".format(seconds))
            first_digit = False
        return "Fully grown in [{}]".format(', '.join(result_str))

    def harvest(self, session, commit_on_execution=True):
        if not self.is_harvestable():
            return None
        new_harvest = Harvest(
            amount = self.plant.base_harvest,
            plant = self.plant,
            farm = self.farm,
        )

        # Increment storage space used
        self.farm.current_harvest += self.get_harvest_amount()

        # Remove crop planted
        self.plant = None
        self.planted_at = None

        # Database actions
        session.add(self)
        session.add(self.farm)
        session.add(new_harvest)
        if commit_on_execution:
            session.commit()
        return new_harvest

    def get_harvest_amount(self):
        if not self.is_harvestable():
            return 0
        return self.plant.base_harvest
