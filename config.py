# Version
CURRENT_VERSION = "v0.0.2b"

# Command prefix
COMMAND_PREFIX = "s!"

# Location of secrets.json where the discord bot token is located.
SECRETS_FILE = "secrets.json"

# Logging format
LOGGING_FORMAT = "(%(asctime)s) [%(levelname)s] - %(message)s"

# Cogs in use
ACTIVE_COGS = [
    "cogs.admin",
    "cogs.core",
    "cogs.economy",
    "cogs.farm",
]

ACTIVE_OBJECTS = [
    "objects.economy.account",
    "objects.economy.transaction",
    "objects.economy.farm.farm",
    "objects.economy.farm.harvest",
    "objects.economy.farm.plot",
    "objects.economy.farm.plant",
]

ACTIVE_SEEDERS = [
    "objects.economy.farm.seeders.plant",
]

TRANSFER_TAX = 0.01

FARM_UPGRADES = {
    "farmers":
    {
        "type": "production",
        "upgrades": 0.05,
        "base": 1000000, "factor": 1.25
    },
    "tractors":
    {
        "type": "production",
        "upgrades": 0.05,
        "base": 10000000, "factor": 1.25
    },
    "cropdusters":
    {
        "type": "production",
        "upgrades": 0.05,
        "base": 100000000, "factor": 1.25
    },
    "accountants":
    {
        "type": "prices",
        "upgrades": 0.05,
        "base": 1000000, "factor": 1.25
    },
    "businessmen":
    {
        "type": "prices",
        "upgrades": 0.05,
        "base": 100000000, "factor": 1.25
    },
}

BASE_PLOT_PRICE = 500000
PLOT_PRICE_FACTOR = 1.45

BASE_STORAGE_UPGRADE_PRICE = 500000
STORAGE_UPGRADE_PRICE_FACTOR = 1.1

FARM_NAME_CHANGE_PRICE = 1000000

DEMAND_DIVISOR = 1