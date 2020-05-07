import logging

import discord
from discord.ext import commands

from messages.farm import *


class Farm(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["fp"])
    async def farmplant(self, ctx):
        pass

    @commands.command(aliases=["fh"])
    async def farmharvest(self, ctx):
        pass

    @commands.command(aliases=["fs"])
    async def farmsell(self, ctx):
        pass

    @commands.command(aliases=["fsa"])
    async def farmsellall(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Farm(bot))

