import logging
from datetime import timedelta, datetime

import discord, schedule
from discord.ext import commands

from config import FARM_NAME_CHANGE_PRICE
from messages.farm import *
from objects.economy.account import EconomyAccount
from objects.economy.farm.farm import Farm as ORMFarm
from objects.economy.farm.plant import Plant
from objects.economy.farm.pricelog import PriceLog

import matplotlib.pyplot as plt

class Farm(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["f"])
    async def farm(self, ctx, target: discord.Member=None):
        """Show target's farm details."""
        if target is None:
            target = ctx.author
        _farm = ORMFarm.get_farm(target, self.bot.db_session)
        if _farm.name is None:
            _farm.name = "Unnamed Farm"
            self.bot.db_session.add(_farm)
            self.bot.db_session.commit()

        embed = discord.Embed(
            title="{0.name}#{0.discriminator}'s farm, {1}".format(target, _farm.name),
            color=0xffd700
        )

        embed.add_field(name="Plots", value=len(_farm.plots))

        await ctx.send(embed=embed)

    @commands.command()
    async def setfarmname(self, ctx, name):
        """Show target's farm details."""
        if len(name) > 32:
            await ctx.send("**{0.mention}, a farm's name can only be 64 characters long.**".format(ctx.author))
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _farm.name = name
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)

        if not _account.has_balance(FARM_NAME_CHANGE_PRICE, raw=True):
            await ctx.send(MSG_INSUFFICIENT_FUNDS_EXTRA.format(
                ctx.author, _account.get_balance(), FARM_NAME_CHANGE_PRICE / 10000
            ))
            return

        _account.add_debit(
            self.bot.db_session, FARM_NAME_CHANGE_PRICE, 
            name="FARM NAME CHANGE", raw=True
        )

        self.bot.db_session.add(_farm)
        self.bot.db_session.commit()
        
        await ctx.send("{0.mention}, you successfully named your farm **{1}**. You now only have **💵 {2:.2f} gil**".format(
            ctx.author, name, _account.get_balance()
        ))

    @commands.command(aliases=["fp"])
    async def farmplots(self, ctx):
        """Show the details of your plots."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plots = _farm.get_all_plots(self.bot.db_session)
        
        plot_str = ""
        plot_count = 1
        for _plot in _plots:
            plot_str += "Plot #{}: {}\n".format(plot_count, _plot.get_status_str())
            plot_count += 1
        ""
        await ctx.send(MSG_PLOTS_STATUS.format(ctx.author, plot_str))

    @commands.command(aliases=["p$",])
    async def plantprices(self, ctx):
        """Show the current global plant prices."""
        all_plants = Plant.get_plants(self.bot.db_session)

        embed = discord.Embed(
            title="-=Current Global Market Prices=-",
            color=0xffd700
        )

        final_str = ""
        for plant in all_plants:
            bp = plant.get_buy_price()
            sp = plant.get_sell_price()
            embed.add_field(
                name="**`{0.tag}` - {0.name}**".format(plant),
                value=MSG_PLANT_PRICES.format(
                  plant, bp, sp, get_growing_time_string(plant.growing_seconds)  
                ),
                inline=False
            )
        embed.set_footer(
            text=MSG_PLANT_PRICES_FOOTER.format(
                (timedelta(hours=1) + datetime.now().replace(microsecond=0, second=0, minute=0)).strftime("%I:%M %p UTC+08:00")    
            )
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["plot$",])
    async def plotprice(self, ctx):
        """Show the price of the next plot."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        result = _farm.get_next_plot_price()
        await ctx.send("{0.mention}, your next plot costs **💵 {1:.2f} gil**.".format(ctx.author, result))

    @commands.cooldown(1, 1, type=commands.BucketType.user)
    @commands.command()
    async def plotbuy(self, ctx):
        """Buy a new plot."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        price = _farm.get_next_plot_price(raw=True)
        if _account.has_balance(price, raw=True):
            _farm.add_plot(self.bot.db_session)
            _account.add_debit(self.bot.db_session, price, name="PLOTBUY", raw=True)
            await ctx.send("{0.mention}, you have successfully bought a new plot! Your new balance is now **💵 {1:.2f} gil**.".format(ctx.author, _account.get_balance()))
        else:
            await ctx.send(MSG_INSUFFICIENT_FUNDS.format(ctx.author, _account.get_balance()))

    @commands.command()
    @commands.is_owner()
    async def setplanttag(self, ctx, plant_name, tag):
        """(Owner) Set a plant's shorthand tag."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        _plant.tag = tag
        self.bot.db_session.add(_plant)
        self.bot.db_session.commit()
        await ctx.send("**Successfully changed plant tag.**")
    
    @commands.command()
    @commands.is_owner()
    async def setplantprice(self, ctx, plant_name, base_price: float):
        """(Owner) Set a plant's base unit price."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        _plant.set_base_price(self.bot.db_session, base_price)

    @commands.command()
    @commands.is_owner()
    async def purgeplots(self, ctx, target: discord.Member=None):
        """(Owner) Purge the plants planted in a target's plots."""
        if target == None:
            target = ctx.author
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        for _plot in _farm.plots:
            _plot.plant = None
            _plot.planted_at = None
            self.bot.db_session.add(_plot)
        self.bot.db_session.add(_plot)
        await ctx.send("**{0.mention}'s plots have been purged.**".format(target))
    
    @commands.command()
    @commands.is_owner()
    async def refreshplantprices(self, ctx):
        """(Owner) Manually refresh the global market prices."""
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
    async def farmplant(self, ctx, plant_name, plant_count=1):
        """Plant a crop on a number of your available plots."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        
        total_price = _plant.buy_price * plant_count
        
        if not _account.has_balance(total_price, raw=True):
            await ctx.send(MSG_INSUFFICIENT_FUNDS.format(ctx.author, _account.get_balance()))
            return
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plots = _farm.get_available_plots(self.bot.db_session)
        if len(_plots) == None:
            await ctx.send(MSG_PLOT_NOT_FOUND.format(ctx.author))
            return
        if len(_plots) < plant_count:
            await ctx.send("**{0.mention}, you do not have enough available plots for that.** You only have **{1}** available and you're trying to plant on **{2}**.".format(
                ctx.author, len(_plots), plant_count
            ))
            return

        _account.add_debit(
            self.bot.db_session, total_price,
            name="B:{0.id}={0.buy_price}".format(_plant),
            raw=True,
        )

        for _plot in _plots[:plant_count]:
            _plot.plant_to_plot(_plant, self.bot.db_session, commit_on_execution=False)
        self.bot.db_session.commit()

        await ctx.send(MSG_PLOT_PLANT.format(ctx.author, _plant, plant_count, total_price/10000, _account.get_balance()))

    @commands.command(aliases=["sh"])
    async def showharvests(self, ctx):
        """Show your harvest inventory."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        
        harvested_plants = set([i.plant for i in _farm.harvests])
        print(_farm.harvests)

        id_to_plant_name = {_plant.id: _plant.name for _plant in harvested_plants}
        total_harvests = {_plant.id: 0 for _plant in harvested_plants}
        
        if len(_farm.harvests) == 0:
            await ctx.send(MSG_SHOW_HARVESTS_NONE.format(ctx.author))
            return

        for harvest in _farm.harvests:
            total_harvests[harvest.plant.id] += harvest.amount

        harvest_str = ""

        for harvest in total_harvests:
            harvest_str += "**{0}**, {1} units\n".format(
                id_to_plant_name[harvest],
                total_harvests[harvest]
            )
        
        await ctx.send(MSG_SHOW_HARVESTS.format(ctx.author, harvest_str))

    @commands.command(aliases=["fh"])
    async def farmharvest(self, ctx):
        """Harvest all your harvestable crops."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plots = _farm.get_all_plots(self.bot.db_session)
        harvestable_plots = []
        for _plot in _plots:
            if _plot.plant is None: continue
            if _plot.is_harvestable(): harvestable_plots.append(_plot)
        
        harvestable_plants = set([_plot.plant for _plot in harvestable_plots])
        id_to_plant_name = {_plant.id: _plant.name for _plant in harvestable_plants}
        total_harvests = {_plant.id: 0 for _plant in harvestable_plants}

        if len(harvestable_plots) is 0:
            await ctx.send(MSG_HARVEST_NONE.format(ctx.author))
            return

        for _plot in harvestable_plots:
            harvest = _plot.get_harvest(self.bot.db_session)
            total_harvests[harvest.plant.id] += harvest.amount

        self.bot.db_session.commit()

        harvest_str = ""
        for harvest in total_harvests:
            harvest_str += "**{0}**, {1} units\n".format(
                id_to_plant_name[harvest],
                total_harvests[harvest]
            )

        await ctx.send(MSG_HARVEST_SUCCESS.format(ctx.author, harvest_str))

    @commands.command(aliases=["pstats", "pstat"])
    async def plantstats(self, ctx, plant_name):
        """Check plant price stats for the past 48 refreshes."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))

        graph_filename = r"images\{}_graph.png".format(_plant.name.lower())

        await ctx.send(
            MSG_SHOW_STATS.format(_plant.name.capitalize()),
            file=discord.File(graph_filename)
        )

    @commands.command(aliases=["fs"])
    async def farmsell(self, ctx, plant_name):
        """Sell all of your target crop."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return

        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)

        total_amount = 0
        for i in range(len(_farm.harvests))[::-1]:
            if _farm.harvests[i].plant.id == _plant.id:
                total_amount += _farm.harvests[i].amount
                del _farm.harvests[i]

        if total_amount == 0:
            await ctx.send(MSG_SELL_NONE.format(ctx.author, _plant.name))
            return
        
        raw_credit = total_amount * _plant.get_sell_price(raw=True)
        _account.add_credit(
            self.bot.db_session, raw_credit,
            name="S:{0.id}={1}".format(_plant, total_amount),
            raw=True
        )
        
        _plant.decrement_demand(self.bot.db_session, total_amount)

        await ctx.send(MSG_SELL_SUCCESS.format(
            ctx.author, total_amount, _plant, raw_credit / 10000, _account.get_balance()
        ))

def get_growing_time_string(growing_time_in_seconds):
    growing_time = timedelta(seconds=growing_time_in_seconds)
    result_str = []
    hours, rem = divmod(growing_time.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    if growing_time.days:
        result_str.append("{}d".format(growing_time.days))
    if hours:
        result_str.append("{}h".format(hours))
    if minutes:
        result_str.append("{}m".format(minutes))
    if seconds:
        result_str.append("{}s".format(seconds))
    return ', '.join(result_str)


def refresh_prices(bot):
    logging.info("Refreshing farm market prices...")
    all_plants = Plant.get_plants(bot.db_session)
    for plant in all_plants:
        plant.randomize_price(bot.db_session, commit_on_execution=False)
    bot.db_session.commit()


def setup(bot):
    bot.add_cog(Farm(bot))
    schedule.every().hour.at(":00").do(refresh_prices, bot)
