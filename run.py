import os, json, logging, importlib

from sqlalchemy.ext.declarative import declarative_base

from config import *
from bot import BotCore

from objects import base

def create_secrets_file():
    """Generate/overwrite the secrets file for this bot."""    
    print("=========================================")
    print("Creating new secrets file {}...".format(SECRETS_FILE))
    print("Please enter your Discord bot's token:")
    token = input()
    secrets_json = {'token': token}
    with open(SECRETS_FILE, 'w') as f:
        f.write(json.dumps(secrets_json))
    print("Secrets file {} successfully created.".format(SECRETS_FILE))
    print("=========================================")


def get_discord_token():
    """Get the Discord bot token from the secrets file.
    If the secrets file is invalid or does not exist, it calls
    `create_secrets_file()` to create/overwrite it.

    Returns:
        {string} -- The bot token.
    """    
    if os.path.exists(SECRETS_FILE):
        f = open(SECRETS_FILE, 'r')
        try:
            data = json.load(f)
        except Exception as e:
            logging.error(type(e).__name__)
            logging.error("Secrets file {} is invalid.".format(SECRETS_FILE))
            f.close()
            create_secrets_file()
            f = open(SECRETS_FILE, 'r')
            data = json.load(f)
        f.close()
        return data['token']
    else:
        logging.error("[ERROR] File {} does not exist.".format(SECRETS_FILE))
        create_secrets_file()
        return get_discord_token()


def main():
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)

    logging.info("Starting the bot...")

    DISCORD_TOKEN = get_discord_token()

    # Instantiate our bot object
    bot = BotCore(command_prefix=COMMAND_PREFIX)

    # We need to preload the objects to add them to
    # possible migrations
    for OBJECT_NAME in ACTIVE_OBJECTS:
        k = importlib.import_module(OBJECT_NAME)

    # Create all tables if they do not exist
    base.Base.metadata.create_all(bot.engine)
    
    # Add our cogs in ACTIVE_COGS (see config)
    logging.info("Loading cogs...")
    for cog in ACTIVE_COGS:
        logging.info(" -- Loading '{}'".format(cog))
        bot.load_extension(cog)

    # Run our bot with token
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()

