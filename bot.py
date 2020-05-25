import logging, asyncio

import discord, schedule
from discord.ext import commands

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import COMMAND_PREFIX, EXP_PER_MESSAGE
from objects.core.profile import Profile
from roles import *
from utils import xp as xputils


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

        leveled_up = None
        _profile = Profile.get_profile(message.author, self.db_session)
        if not message.content.startswith(COMMAND_PREFIX):
            message_exp = xputils.message_to_xp(message.content)
            leveled_up = _profile.process_xp(message_exp, self.db_session)

        if leveled_up is not None:
            _msg = await message.channel.send("**{0.mention}, you have leveled up!** You are now **Level {1}**." .format(
                message.author, _profile.level
            ))
            await _msg.delete(delay=5)
            
            if leveled_up != 2:
                all_leveled_roles = [
                    message.channel.guild.get_role(LEVELED_ROLES[_r][0]) for _r in LEVELED_ROLES
                ]
                await message.author.remove_roles(*all_leveled_roles)
                _msg = await message.channel.send("{0.mention}, you have reached the rank of **{1}!**" .format(
                    message.author, leveled_up[1]
                ))
                _role = message.channel.guild.get_role(leveled_up[0])
                await message.author.add_roles(_role)
                await _msg.delete(delay=5)


        await self.process_commands(message)

    async def on_command_error(self, ctx, err):
        if type(err) == discord.ext.commands.errors.CommandOnCooldown:
            await ctx.send("{0.mention}: **__{1}__**".format(ctx.author, err))
            return
        logging.error("Command error: {0} [author: {1.author}][cmd: {1.command}]".format(err, ctx))
        await ctx.send("**{0.mention}, that's an invalid command format.**".format(ctx.author))
