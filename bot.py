import logging, asyncio

import discord, schedule
from discord.ext import commands

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import COMMAND_PREFIX, EXP_PER_MESSAGE
from objects.core.profile import Profile


class BotCore(commands.AutoShardedBot):

    # TODO: Remove hardcoding on engine URI
    engine = create_engine("sqlite:///data.db", echo=False)
    SQLSession = sessionmaker(bind=engine, expire_on_commit=False)
    db_session = SQLSession()

    async def on_ready(self):
        logging.info("Logged on as [{}]".format(self.user))
        logging.info("Using discord.py version {}".format(discord.__version__))

    async def on_message(self, message):
        if message.author.bot:
            return

        logging.debug("Message from {0.author}: {0.content}".format(message))
        schedule.run_pending()

        leveled_up = False
        _profile = Profile.get_profile(message.author, self.db_session)
        if not message.content.startswith("s!"):
            leveled_up = _profile.process_xp(EXP_PER_MESSAGE, self.db_session)

        if leveled_up:
            message = await message.channel.send("**{0.mention}, you have leveled up!** You are now **Level {1}**." .format(
                message.author, _profile.level
            ))
            await message.delete(delay=5)

        await self.process_commands(message)

    async def on_command_error(self, ctx, err):
        if type(err) == discord.ext.commands.errors.CommandOnCooldown:
            await ctx.send("{0.mention}: **__{1}__**".format(ctx.author, err))
            return
        logging.error("Command error: {0} [author: {1.author}][cmd: {1.command}]".format(err, ctx))
        await ctx.send("**{0.mention}, that's an invalid command format.**".format(ctx.author))
