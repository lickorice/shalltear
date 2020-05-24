import logging

import discord, schedule
from discord.ext import commands

from config import *


class Progression(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['adr',], hidden=True)
    @commands.is_owner()
    async def assignbaserole(self, ctx):
        """(Owner) Assign base default role."""
        pass

    @commands.command(aliases=['alr',], hidden=True)
    @commands.is_owner()
    async def assignleveledrole(self, ctx, *cogs):
        """(Owner) Assign leveled role."""
        pass


def setup(bot):
    bot.add_cog(Progression(bot))
