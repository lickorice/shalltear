import logging
from discord.ext import commands
from config import COMMAND_PREFIX


class BotCore(commands.Bot):
    async def on_ready(self):
        logging.info("Logged on as [{}]".format(self.user))

    # async def on_message(self, message):
    #     logging.info("Message from {0.author}: {0.content}".format(message))

