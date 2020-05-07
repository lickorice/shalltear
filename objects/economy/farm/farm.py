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
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
