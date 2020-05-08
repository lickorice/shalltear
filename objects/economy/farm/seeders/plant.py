from objects.economy.farm.plant import Plant
from random import randint

CURRENT_PLANTS = [
    {
        "name": "Turnip",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 5000,
        "growing_seconds": 300,
    },
    {
        "name": "Rice",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 1000,
        "growing_seconds": 300,
    },
    {
        "name": "Strawberry",
        "base_harvest": 20,
        "buy_price": 100000,
        "base_sell_price": 7000,
        "randomness_factor": 2000,
        "growing_secon\ds": 600,
    },
    {
        "name": "Watermelon",
        "base_harvest": 3,
        "buy_price": 1000000,
        "base_sell_price": 500000,
        "randomness_factor": 4000,
        "growing_seconds": 3600,
    },
]

def get_selling_price(plant):
    price = plant["base_sell_price"]
    threshold = plant["randomness_factor"]
    factor = randint(10000-threshold, 10000+threshold) / 10000
    return int(price * factor)


def seed(session):
    plant_names = [i.name for i in session.query(Plant).all()]
    for PLANT in CURRENT_PLANTS:
        if PLANT["name"] in plant_names: continue # Skip if exists
        session.add(Plant(
            name = PLANT["name"],
            base_harvest = PLANT["base_harvest"],
            buy_price = PLANT["buy_price"],
            base_sell_price = PLANT["base_sell_price"],
            current_sell_price = get_selling_price(PLANT),
            randomness_factor = PLANT["randomness_factor"],
            growing_seconds = PLANT["growing_seconds"],
        ))
    session.commit()
