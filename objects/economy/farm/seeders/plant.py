from objects.economy.farm.plant import Plant
from random import randint

CURRENT_PLANTS = [
    {
        "name": "Turnip", # 1 gil per 5 mins
        "tag": "TRNP",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 7500,
        "growing_seconds": 300,
    },
    {
        "name": "Rice", # 1 gil per 5 mins
        "tag": "RICE",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 1000,
        "growing_seconds": 300,
    },
    {
        "name": "Strawberry", # 2 gil per 5 mins
        "tag": "STBY",
        "base_harvest": 20,
        "buy_price": 100000,
        "base_sell_price": 7000,
        "randomness_factor": 2000,
        "growing_seconds": 600,
    },
    {
        "name": "Watermelon", # 4.16 gil per 5 mins
        "tag": "WTML",
        "base_harvest": 3,
        "buy_price": 1000000,
        "base_sell_price": 500000,
        "randomness_factor": 4000,
        "growing_seconds": 3600,
    },
    {
        "name": "Pumpkin", # 11.11 gil per 5 ins
        "tag": "PMKN",
        "base_harvest": 1,
        "buy_price": 2000000,
        "base_sell_price": 4000000,
        "randomness_factor": 5000,
        "growing_seconds": 5400,
    },
    {
        "name": "Grapes", # 14.58 gil per 5 mins
        "tag": "GRPS",
        "base_harvest": 50,
        "buy_price": 2500000,
        "base_sell_price": 120000,
        "randomness_factor": 3000,
        "growing_seconds": 7200,
    },
    {
        "name": "Potato", # 3.125 gil per 5 mins
        "tag": "PTTO",
        "base_harvest": 25,
        "buy_price": 500000,
        "base_sell_price": 27500,
        "randomness_factor": 4000,
        "growing_seconds": 1800,
    },
    {
        "name": "Wheat", # 62.5 gil per 5 mins
        "tag": "WHET",
        "base_harvest": 50,
        "buy_price": 1000000,
        "base_sell_price": 22500,
        "randomness_factor": 4000,
        "growing_seconds": 60,
    },
    {
        "name": "Tomato", # 25 gil per 5 mins
        "tag": "TMTO",
        "base_harvest": 50,
        "buy_price": 2000000,
        "base_sell_price": 50000,
        "randomness_factor": 2000,
        "growing_seconds": 600,
    },
    {
        "name": "Sugarcane", # 20 gil per 5 mins
        "tag": "SGRC",
        "base_harvest": 100,
        "buy_price": 10000000,
        "base_sell_price": 300000,
        "randomness_factor": 2000,
        "growing_seconds": 28800,
    },
    {
        "name": "Coconut", # 20 gil per 5 mins
        "tag": "COCO",
        "base_harvest": 20,
        "buy_price": 100000000,
        "base_sell_price": 19400000,
        "randomness_factor": 2000,
        "growing_seconds": 57600,
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
            tag = PLANT["tag"],
            base_harvest = PLANT["base_harvest"],
            buy_price = PLANT["buy_price"],
            base_sell_price = PLANT["base_sell_price"],
            current_sell_price = get_selling_price(PLANT),
            randomness_factor = PLANT["randomness_factor"],
            growing_seconds = PLANT["growing_seconds"],
        ))
    session.commit()
