import logging

import discord
from discord.ext import commands

from messages.farm import *
from objects.economy.account import EconomyAccount
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
    async def farmplots(self, ctx):
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plots = _farm.get_all_plots(self.bot.db_session)
        
        plot_str = ""
        plot_count = 1
        for _plot in _plots:
            plot_str += "Plot #{}:\n```{}```\n".format(plot_count, _plot.get_status_str())
            plot_count += 1
        
        await ctx.send(MSG_PLOTS_STATUS.format(ctx.author, plot_str))

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
    async def farmplant(self, ctx, plant_name):
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        if not account.has_balance(_plant.buy_price, raw=True):
            await ctx.send(MSG_INSUFFICIENT_FUNDS.format(ctx.author, account.get_balance()))
            return
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plot = _farm.get_available_plot(self.bot.db_session)
        if _plot is None:
            await ctx.send(MSG_PLOT_NOT_FOUND.format(ctx.author))
            return

        account.add_debit(
            self.bot.db_session, _plant.buy_price,
            name="B:{0.id}={0.buy_price}".format(_plant),
            raw=True,
        )

        _plot.plant_to_plot(_plant, self.bot.db_session)
        await ctx.send(MSG_PLOT_PLANT.format(ctx.author, _plant, account.get_balance()))

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

