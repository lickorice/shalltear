from datetime import datetime, timedelta
from random import randint
import logging

from sqlalchemy import Table, Column, Boolean, Integer, BigInteger, String, MetaData, DateTime

from config import DEMAND_DIVISOR
from objects.base import Base
from objects.economy.farm.plot import Plot
from objects.economy.farm.farm import Farm
from objects.economy.farm.pricelog import PriceLog

import matplotlib.pyplot as plt

class Plant(Base):
    __tablename__ = 'farm_plants'

    id = Column(Integer, primary_key=True)

    name = Column(String(64), unique=True) # Turnip
    tag = Column(String(4), unique=True) # TRNP
    buy_price = Column(BigInteger) # 50000
    base_harvest = Column(Integer) # 10

    base_sell_price = Column(BigInteger) # 20000
    current_sell_price = Column(BigInteger) # Set dynamically
    randomness_factor = Column(BigInteger) # / 10000

    growing_seconds = Column(BigInteger)

    current_demand = Column(BigInteger)
    base_demand = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def get_plants(session):
        all_plants = session.query(Plant).order_by(Plant.buy_price).all()
        return all_plants

    @staticmethod
    def get_plant(session, name):
        plant = session.query(Plant).filter(Plant.name.ilike(name)).first()
        if plant is None:
            plant = session.query(Plant).filter(Plant.tag.ilike(name)).first()
        return plant
    
    def get_buy_price(self):
        return self.buy_price / 10000
    
    def get_sell_price(self, raw=False):
        cd, bd = self.current_demand, self.base_demand
        sell_price = (self.current_sell_price / 2) * 4**((cd**2)/(bd**2))
        sell_price = int(sell_price)
        if raw:
            return sell_price
        return sell_price / 10000

    def decrement_demand(self, session, amount):
        self.current_demand = max(self.current_demand - amount, 0)
        session.add(self)
        session.commit()

    def generate_graph(self, session):
        time_now = datetime.now()
        
        _plantstats = PriceLog.get_plant_price_logs(self, session)
        number_of_entries = 48 if len(_plantstats) >= 48 else len(_plantstats)
        _plantstats = _plantstats[len(_plantstats) - number_of_entries:len(_plantstats)]

        # Define x-axis labels
        def x_label(time):
            return time.strftime("%d | %H:%M")

        # Format y-axis labels
        def y_label(price):
            return round((price / 2) * 4 / 10000, 2)
        
        # Graph axes
        time_x = [x_label(log.refreshed_at) for log in _plantstats]
        price_y = [y_label(log.price) for log in _plantstats]

        # Clear plot and generate new graph
        plt.clf()
        plt.title(
            "{0} as of {1}".format(self.tag, x_label(time_now)),
            fontsize=8
        )
        plt.plot(time_x, price_y)
        plt.xticks(fontsize=6, rotation=90)
        plt.yticks(fontsize=6)

        # Affix label per point
        for x,y in zip(time_x, price_y):
            label = "{:.2f}".format(y)
            plt.annotate(
                label,
                (x,y),
                fontsize=6,
                textcoords="offset points",
                xytext=(0,10),
                ha='center'
            )

        # Save graph
        plt.savefig(r"images\{}_graph.png".format(self.name.lower()))
        logging.info("Successfully generated {} graph.".format(self.name))

    def randomize_price(self, session, commit_on_execution=True):
        _farms = Farm.get_farms_count(session)
        _plots = Plot.get_plots_count(session)
        
        # Demand calculation
        growth_rate = 3600 / min(self.growing_seconds, 3600)
        _demand = self.base_harvest * growth_rate * (_plots)
        logging.info("{}: {}".format(self.name, _demand))
        self.base_demand = max(int(_demand / DEMAND_DIVISOR), 1)
        self.current_demand = max(int(_demand / DEMAND_DIVISOR), 1)
        
        # Price calculation
        _r = self.randomness_factor
        factor = randint(10000-_r, 10000+_r) / 10000
        self.current_sell_price = int(self.base_sell_price*factor)

        session.add(self)
        PriceLog.log_price(self, session, commit_on_execution=commit_on_execution)
        
        if commit_on_execution:
            session.commit()

        self.generate_graph(session)

    def set_base_price(self, session, price, raw=False):
        if not raw:
            price *= 10000
        self.base_sell_price = price
        session.add(self)
        session.commit()