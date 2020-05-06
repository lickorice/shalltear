import logging

import discord
from discord.ext import commands

from messages.core import *


class Core(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Tests responsiveness."""
        latency_in_ms = "{} ms".format(int(self.bot.latency * 1000))
        await ctx.send(CMD_PING.format(latency_in_ms))


def setup(bot):
    bot.add_cog(Core(bot))

