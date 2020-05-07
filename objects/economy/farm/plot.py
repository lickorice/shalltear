from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base


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