import logging
from discord.ext import commands
from config import COMMAND_PREFIX


class BotCore(commands.Bot):
    async def on_ready(self):
        logging.info("Logged on as [{}]".format(self.user))

    async def on_message(self, message):
        logging.debug("Message from {0.author}: {0.content}".format(message))

        await self.process_commands(message)

    async def on_command_error(self, ctx, err):
        logging.error("Command error: {0} [author: {1.author}][cmd: {1.command}]".format(err, ctx))