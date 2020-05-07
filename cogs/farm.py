import logging

import discord
from discord.ext import commands

from messages.farm import *
from objects.economy.farm.farm import Farm as ORMFarm
from objects.economy.farm.plant import Plant


class Farm(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["f"])
    async def farm(self, ctx, target: discord.Member=None):
        if target is None:
            target = ctx.author
        _farm = ORMFarm.get_farm(target, self.bot.db_session)
        await ctx.send(MSG_FARM_STATUS.format(target, len(_farm.plots), _farm))

    @commands.command(aliases=["fpo"])
    async def farmplots(self, ctx, target: discord.Member=None):
        if target is None:
            target = ctx.author

    @commands.command(aliases=["p$",])
    async def plantprices(self, ctx):
        all_plants = Plant.get_plants(self.bot.db_session)
        final_str = ""
        for plant in all_plants:
            bp = plant.get_buy_price()
            sp = plant.get_sell_price()
            _str = "**{0.name}** `[B: {1:.2f} gil | S: {2:.2f} gil]`\n".format(plant, bp, sp)
            final_str += _str
        await ctx.send("{}".format(final_str))

    @commands.command()
    @commands.is_owner()
    async def refreshplantprices(self, ctx):
        all_plants = Plant.get_plants(self.bot.db_session)
        for plant in all_plants:
            plant.randomize_price(self.bot.db_session)
        final_str = ""
        for plant in all_plants:
            bp = plant.get_buy_price()
            sp = plant.get_sell_price()
            _str = "***{0.name}*** `[B: {1:.2f} gil | S: {2:.2f} gil]`\n".format(plant, bp, sp)
            final_str += _str
        await ctx.send("**Prices refreshed!**\n{}".format(final_str))

    @commands.command(aliases=["fpa"])
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

