from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base


class Harvest(Base):
    __tablename__ = 'farm_harvests'

    id = Column(Integer, primary_key=True)

    amount = Column(Integer)
    plant_id = Column(BigInteger, ForeignKey('farm_plants.id'))
    plant = relationship("Plant")

    farm_id = Column(BigInteger, ForeignKey('farm_farms.id'))
    farm = relationship("Farm", back_populates="harvests")

    growing_seconds = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
