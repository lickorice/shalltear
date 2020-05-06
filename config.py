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
]

ACTIVE_OBJECTS = [
    "objects.economy.account",
    "objects.economy.transaction",
]