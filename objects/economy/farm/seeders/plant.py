from objects.economy.farm.plant import Plant

CURRENT_PLANTS = [
    {
        "name": "Turnip",
        "buy_price": 50000,
        "base_sell_price": 20000,
        "sell_matrix": [100, 90, 100, 110, 120, 130, 80],
        "randomness_factor": 5000,
        "growing_seconds": 300,
    },
]

def seed(session):
    plant_names = [i.name for i in session.query(Plant).all()]
    for PLANT in CURRENT_PLANTS:
        if PLANT["name"] in plant_names: continue # Skip if exists
        session.add(Plant(
            name = PLANT["name"],
            buy_price = PLANT["buy_price"],
            base_sell_price = PLANT["base_sell_price"],
            current_sell_price = 10,
            randomness_factor = PLANT["randomness_factor"],
            growing_seconds = PLANT["growing_seconds"],
        ))
    session.commit()
