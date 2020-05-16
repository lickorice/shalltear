from datetime import datetime, timedelta

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base
from objects.economy.farm.harvest import Harvest
from utils.datetime import format_time_string


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

    plot_range = Column(Integer, default=1)

    def __repr__(self):
        return "<Plot plant={0.plant}, planted_at={0.planted_at}>".format(self)

    @staticmethod
    def get_all_plots_count(session):
        return sum(_plot.plot_range for _plot in session.query(Plot).all())
    
    def get_status_str(self):
        return "[{0:04d}] {1} -- {2}".format(
            self.plot_range, self.plant.tag, self.get_remaining_harvest_time()
        )

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
        return "[{}]".format(format_time_string(time_difference.total_seconds()))

    def harvest(self, session, target_range=-1, force=False, commit_on_execution=True):
        if not force and not self.is_harvestable():
            return None

        target_range = min(target_range, self.plot_range)
        harvest_amount = self.plant.base_harvest
        if target_range == -1: # -1 = Harvest all
            harvest_amount *= self.plot_range
            self.plot_range = 0
        else:
            harvest_amount *= target_range
            self.plot_range -= target_range

        # Pass to an information wrapper
        harvest_info = HarvestInfo(
            plant=self.plant,
            amount=harvest_amount,
            delete_plot=True if self.plot_range == 0 else False
        )

        # Increment storage space used
        self.farm.current_harvest += harvest_amount

        # Database actions
        session.add(self)
        session.add(self.farm)

        if commit_on_execution:
            session.commit()

        return harvest_info

    def get_harvest_amount(self, target_range=-1):
        if not self.is_harvestable():
            return 0
        target_range = min(target_range, self.plot_range)
        if target_range == -1:
            return self.plant.base_harvest * self.plot_range
        else:
            return self.plant.base_harvest * target_range


class HarvestInfo:
    def __init__(self, plant, amount, delete_plot=False):
        self.plant = plant
        self.amount = amount
        self.delete_plot = delete_plot
