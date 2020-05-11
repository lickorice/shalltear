from objects.economy.farm.plant import Plant
from random import randint

CURRENT_PLANTS = [
    {
        "name": "Turnip",
        "tag": "TRNP",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 7500,
        "growing_seconds": 300,
    },
    {
        "name": "Rice",
        "tag": "RICE",
        "base_harvest": 10,
        "buy_price": 50000,
        "base_sell_price": 6000,
        "randomness_factor": 1000,
        "growing_seconds": 300,
    },
    {
        "name": "Strawberry",
        "tag": "STBY",
        "base_harvest": 20,
        "buy_price": 100000,
        "base_sell_price": 7000,
        "randomness_factor": 2000,
        "growing_seconds": 600,
    },
    {
        "name": "Watermelon",
        "tag": "WTML",
        "base_harvest": 3,
        "buy_price": 20000000,
        "base_sell_price": 1000000,
        "randomness_factor": 4000,
        "growing_seconds": 3600,
    },
    {
        "name": "Pumpkin",
        "tag": "PMKN",
        "base_harvest": 1,
        "buy_price": 25000000,
        "base_sell_price": 40000000,
        "randomness_factor": 5000,
        "growing_seconds": 5400,
    },
    {
        "name": "Grapes",
        "tag": "GRPS",
        "base_harvest": 100,
        "buy_price": 50000000,
        "base_sell_price": 600000,
        "randomness_factor": 3000,
        "growing_seconds": 7200,
    },
    {
        "name": "Potato",
        "tag": "PTTO",
        "base_harvest": 25,
        "buy_price": 500000,
        "base_sell_price": 27500,
        "randomness_factor": 4000,
        "growing_seconds": 1800,
    },
    {
        "name": "Wheat",
        "tag": "WHET",
        "base_harvest": 50,
        "buy_price": 1000000,
        "base_sell_price": 22500,
        "randomness_factor": 4000,
        "growing_seconds": 60,
    },
    {
        "name": "Tomato",
        "tag": "TMTO",
        "base_harvest": 50,
        "buy_price": 2000000,
        "base_sell_price": 50000,
        "randomness_factor": 2000,
        "growing_seconds": 600,
    },
    {
        "name": "Sugarcane",
        "tag": "SGRC",
        "base_harvest": 100,
        "buy_price": 100000000,
        "base_sell_price": 2000000,
        "randomness_factor": 2000,
        "growing_seconds": 28800,
    },
    {
        "name": "Coconut",
        "tag": "COCO",
        "base_harvest": 20,
        "buy_price": 200000000,
        "base_sell_price": 25000000,
        "randomness_factor": 2000,
        "growing_seconds": 57600,
    },
    {
        "name": "Banana",
        "tag": "BNNA",
        "base_harvest": 25,
        "buy_price": 50000000,
        "base_sell_price": 260000,
        "randomness_factor": 5000,
        "growing_seconds": 900,
    },
    {
        "name": "Lemon",
        "tag": "LMON",
        "base_harvest": 75,
        "buy_price": 10000000,
        "base_sell_price": 170000,
        "randomness_factor": 2000,
        "growing_seconds": 1800,
    },
    {
        "name": "Hops",
        "tag": "HOPS",
        "base_harvest": 50,
        "buy_price": 50000000,
        "base_sell_price": 1300000,
        "randomness_factor": 2000,
        "growing_seconds": 2700,
    },
    {
        "name": "Lettuce",
        "tag": "LTTC",
        "base_harvest": 50,
        "buy_price": 50000000,
        "base_sell_price": 1300000,
        "randomness_factor": 5000,
        "growing_seconds": 1200,
    },
    {
        "name": "Pineapple",
        "tag": "PNPL",
        "base_harvest": 100,
        "buy_price": 500000000,
        "base_sell_price": 10000000,
        "randomness_factor": 1000,
        "growing_seconds": 14400,
    },
    {
        "name": "Pepper",
        "tag": "PPER",
        "base_harvest": 200,
        "buy_price": 750000000,
        "base_sell_price": 7500000,
        "randomness_factor": 2000,
        "growing_seconds": 21600,
    },
    {
        "name": "Mango",
        "tag": "MNGO",
        "base_harvest": 100,
        "buy_price": 300000000,
        "base_sell_price": 6000000,
        "randomness_factor": 7000,
        "growing_seconds": 10800,
    },
    {
        "name": "Passionfruit",
        "tag": "PNFT",
        "base_harvest": 250,
        "buy_price": 1500000000,
        "base_sell_price": 16000000,
        "randomness_factor": 2000,
        "growing_seconds": 86400,
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
