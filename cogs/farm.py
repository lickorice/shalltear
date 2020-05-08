import logging
from datetime import timedelta

import discord, schedule
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
        await ctx.send(MSG_FARM_STATUS.format(target, len(_farm.plots)))

    @commands.command(aliases=["fp"])
    async def farmplots(self, ctx):
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
        all_plants = Plant.get_plants(self.bot.db_session)
        final_str = ""
        for plant in all_plants:
            bp = plant.get_buy_price()
            sp = plant.get_sell_price()
            _str = "**{0.name}**: `[B: {1:.2f} gil | S: {2:.2f} gil]` - Yields **{0.base_harvest}** units per harvest, grows in `{3}`.\n".format(plant, bp, sp, get_growing_time_string(plant.growing_seconds))
            final_str += _str
        await ctx.send("***__Current global market prices:__***\n{}".format(final_str))

    @commands.command(aliases=["plot$",])
    async def plotprice(self, ctx):
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        result = _farm.get_next_plot_price()
        await ctx.send("{0.mention}, your next plot costs **💵 {1:.2f} gil**.".format(ctx.author, result))

    @commands.cooldown(1, 5, type=commands.BucketType.user)
    @commands.command()
    async def plotbuy(self, ctx):
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
    async def setplantprice(self, ctx, plant_name, base_price: float):
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        _plant.set_base_price(self.bot.db_session, base_price)

    @commands.command()
    @commands.is_owner()
    async def purgeplots(self, ctx, target: discord.Member=None):
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

    @commands.command(aliases=["fs"])
    async def farmsell(self, ctx, plant_name):
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
        
        raw_credit = total_amount * _plant.current_sell_price
        _account.add_credit(
            self.bot.db_session, raw_credit,
            name="S:{0.id}={0.current_sell_price}".format(_plant),
            raw=True
        )

        await ctx.send(MSG_SELL_SUCCESS.format(
            ctx.author, total_amount, _plant, raw_credit / 10000, _account.get_balance()
        ))

    # @commands.command(aliases=["fsa"])
    # async def farmsellall(self, ctx):
    #     pass


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
