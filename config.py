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

BASE_PLOT_PRICE = 500000
PLOT_PRICE_FACTOR = 1.5

FARM_NAME_CHANGE_PRICE = 1000000

DEMAND_DIVISOR = 5