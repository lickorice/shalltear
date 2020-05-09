from datetime import datetime
import logging

from sqlalchemy import Table, Column, Integer, BigInteger, String, UniqueConstraint, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from objects.base import Base


class Upgrade(Base):
    __tablename__ = 'farm_upgrades'

    id = Column(Integer, primary_key=True)

    name = Column(String(32))
    upgrade_type = Column(String(32))

    level = Column(Integer, default=0)
    base_price = Column(BigInteger)
    factor = Column(BigInteger, default=1.25)

    farm_id = Column(BigInteger, ForeignKey('farm_farms.id'))
    farm = relationship("Farm", back_populates="upgrades")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (UniqueConstraint("name", "farm_id", name="nfid_c"),)

    def __repr__(self):
        return "<Upgrade name={0.name}, farm_id={0.farm_id}, level={0.level}>".format(self)

    def get_next_level_cost(self, raw=False):
        if not raw:
            return (self.base_price * ((self.level+1)**self.factor)) / 10000
        return (self.base_price * ((self.level+1)**self.factor))
