import logging, asyncio, string, random
from datetime import timedelta, datetime
from math import log10

import discord, schedule
from discord.ext import commands

from config import *
from messages.farm import *
from messages.core import MSG_CMD_INVALID
from objects.core.profile import Profile
from objects.economy.core.account import EconomyAccount
from objects.economy.farm.farm import Farm as ORMFarm
from objects.economy.farm.harvest import Harvest
from objects.economy.farm.plant import Plant
from objects.economy.farm.pricelog import PriceLog
from utils.datetime import format_time_string


class Farm(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["f"])
    async def farm(self, ctx, target: discord.Member=None):
        """Show target's farm details."""
        if target is None:
            target = ctx.author
        _farm = ORMFarm.get_farm(target, self.bot.db_session)
        
        farm_name = _farm.get_name(self.bot.db_session)

        embed = discord.Embed(
            title="{0.name}#{0.discriminator}'s farm, {1}".format(target, farm_name),
            color=0xffd700
        )

        embed.add_field(name="Plots", value="{0} / {1}".format(
            _farm.get_plot_count(), FARM_PLOTS_MAX,
        ))
        embed.add_field(
            name="Storage", 
            value="{0.current_harvest} / {0.harvest_capacity}".format(_farm)
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["ftop"])
    async def farmtop(self, ctx):
        """Shows top farms in the server."""
        top_farms = ORMFarm.get_top_farms(self.bot.db_session)

        embed = discord.Embed(title="Top 10 Most Bountiful Farms", color=0xffd700)
        rank = 1
        for _farm in top_farms:
            _farm.plot_capacity
            user = self.bot.get_user(_farm.user_id)
            _profile = Profile.get_profile(user, self.bot.db_session)
            try:
                row_name = "#{1} **{2}** - ({0.name}#{0.discriminator})".format(user, rank, _farm.get_name(self.bot.db_session))
            except AttributeError:
                row_name = "#{1} **{2}** - ({0})".format("Unknown User", rank, _farm.get_name(self.bot.db_session))
            
            if rank == 1:
                rank_details = "🌟 "
            elif rank <= 5:
                rank_details = "⭐ "
            else:
                rank_details = ""
            
            if _profile.farm_prestige == 0:
                rank_details += "{0} Plots".format(_farm.plot_capacity)
            else:
                rank_details += "**Prestige Level {1}** - {0} Plots".format(_farm.plot_capacity, _profile.farm_prestige)
            embed.add_field(name=row_name, value=rank_details, inline=False)
            rank += 1

        await ctx.send(embed=embed)

    @commands.command()
    async def setfarmname(self, ctx, name):
        """Show target's farm details."""
        if len(name) > 32:
            await ctx.send(MSG_FARM_RENAME_NAME_TOO_LONG.format(ctx.author))
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
        
        await ctx.send(MSG_FARM_RENAME_SUCCESS.format(
            ctx.author, name, _account.get_balance()
        ))

    @commands.command(aliases=["fp"])
    async def farmplots(self, ctx, page_number: int=1):
        """Show the details of your plots."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _plots = _farm.plots

        plot_count = len(_plots)

        paginated_plots = [
            _plots[i:i+20] for i in range(0, plot_count, 20)
        ]

        if len(paginated_plots) == 0:
            paginated_plots = [[]]

        # Make sure page number is in bounds
        page_number = min(page_number, len(paginated_plots))
        page_number = max(page_number, 1)
        
        plot_str = "You have {} plots free out of {} total.\n".format(
            _farm.get_free_plot_count(), _farm.get_plot_count()
        )
        plot_count = 1 + (20 * (page_number-1))
        for _plot in paginated_plots[page_number-1]:
            plot_str += "Plot #{0:04d}: {1}\n".format(plot_count, _plot.get_status_str())
            plot_count += 1
        
        embed = discord.Embed(
            title="{0.name}#{0.discriminator}'s farm, {1}".format(ctx.author, _farm.name),
            color=0xffd700
        )

        embed.add_field(
            name=MSG_PLOTS_STATUS.format(page_number, len(paginated_plots)),
            value="```{}```".format(plot_str)
        )

        embed.set_footer(text="Showing 20 plots per page. s!fp [page_number]")

        await ctx.send(embed=embed)

        # await ctx.send(MSG_PLOTS_STATUS.format(
        #     ctx.author, _farm.name, 
        #     plot_str, 
        #     page_number, len(paginated_plots)
        # ))

    @commands.command(aliases=["p$",])
    async def plantprices(self, ctx, plant_name=None):
        """Show the current global plant prices."""
        try:
            page_number = int(plant_name)
            plant_name = None
        except TypeError:
            page_number = 1
        except ValueError:
            _plant = Plant.get_plant(self.bot.db_session, plant_name)

        if plant_name is not None:
            
            if _plant is None:
                ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
                return

            embed = discord.Embed(
                title="-=Current {0} Market Prices=-".format(_plant.name),
                color=0xffd700
            )
            bp = _plant.get_buy_price()
            sp = _plant.get_sell_price()
            embed.add_field(
                name="**`{0.tag}` - {0.name}**".format(_plant),
                value=MSG_PLANT_PRICES.format(
                  _plant, bp, sp, format_time_string(_plant.growing_seconds)  
                ),
                inline=False
            )
        else:
            all_plants = Plant.get_plants(self.bot.db_session)

            plant_count = len(all_plants)

            paginated_plants = [
                all_plants[i:i+10] for i in range(0, plant_count, 10)
            ]


            # Make sure page number is in bounds
            page_number = min(page_number, len(paginated_plants))
            page_number = max(page_number, 1)

            embed = discord.Embed(
                title="-=Current Global Market Prices=-" +
                "\nPage {0} of {1}".format(page_number, len(paginated_plants)),
                color=0xffd700
            )

            final_str = ""
            for _plant in paginated_plants[page_number-1]:
                bp = _plant.get_buy_price()
                sp = _plant.get_sell_price()
                embed.add_field(
                    name="**`{0.tag}` - {0.name}**".format(_plant),
                    value=MSG_PLANT_PRICES.format(
                    _plant, bp, sp, format_time_string(_plant.growing_seconds)  
                    ),
                    inline=False
                )
            embed.set_footer(
                text=MSG_PLANT_PRICES_FOOTER.format(
                    (timedelta(hours=1) + datetime.now().replace(
                        microsecond=0, second=0, minute=0)).strftime("%I:%M %p UTC+08:00")    
                )
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=["plot$",])
    @commands.cooldown(1, 1, type=commands.BucketType.user)
    async def plotprice(self, ctx, up_count: int=1):
        """Show the price of the next N plots. (N <= 1M)"""
        up_count = max(1, up_count)
        up_count = min(1000000, up_count)
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        
        plot_count = _farm.get_plot_count()
        to_max_plots = FARM_PLOTS_MAX - plot_count
        if to_max_plots == 0:
            await ctx.send("**{0.mention}, you have reached maximum plot count.**".format(ctx.author))
            return
        
        up_count = min(up_count, to_max_plots)
        
        result = _farm.get_next_plot_price(up_count=up_count)
        await ctx.send(MSG_PLOT_PRICE_CHECK.format(
            ctx.author, result, up_count
        ))

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def plotbuy(self, ctx, up_count: int=1):
        """Buy new N plots. (N <= 1M)"""
        up_count = max(1, up_count)
        up_count = min(1000000, up_count)
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        
        plot_count = _farm.get_plot_count()
        to_max_plots = FARM_PLOTS_MAX - plot_count
        if to_max_plots == 0:
            await ctx.send("**{0.mention}, you have reached maximum plot count.**".format(ctx.author))
            return
        
        up_count = min(up_count, to_max_plots)
        
        price = _farm.get_next_plot_price(raw=True, up_count=up_count)
        if _account.has_balance(price, raw=True):
            _farm.add_plot(self.bot.db_session, up_count=up_count)
            _account.add_debit(self.bot.db_session, price, name="PLOTBUY", raw=True)
            await ctx.send(MSG_PLOT_BUY_SUCCESS.format(
                ctx.author, _account.get_balance(), up_count
            ))
        else:
            await ctx.send(MSG_INSUFFICIENT_FUNDS_EXTRA.format(
                ctx.author, _account.get_balance(), price / 10000
            ))

    @commands.command(aliases=["silo$",])
    @commands.cooldown(1, 1, type=commands.BucketType.user)
    async def siloprice(self, ctx, up_count: int=1):
        """Show the price of up to the next 1M silos (storage upgrade)."""
        up_count = max(1, up_count)
        up_count = min(1000000, up_count)
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        result = _farm.get_next_storage_upgrade_price(up_count=up_count)
        await ctx.send(MSG_SILO_PRICE_CHECK.format(
            ctx.author, result, up_count
        ))

    @commands.command()
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def silobuy(self, ctx, up_count: int=1):
        """Buy new N silos (increases your storage by 100). (N <= 1M)"""
        up_count = max(1, up_count)
        up_count = min(1000000, up_count)
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        price = _farm.get_next_storage_upgrade_price(raw=True, up_count=up_count)
        if _account.has_balance(price, raw=True):
            _farm.upgrade_storage(self.bot.db_session, up_count)
            _account.add_debit(self.bot.db_session, price, name="SILOBUY", raw=True)
            await ctx.send(MSG_SILO_BUY_SUCCESS.format(
                ctx.author, _account.get_balance(), up_count
            ))
        else:
            await ctx.send(MSG_INSUFFICIENT_FUNDS_EXTRA.format(
                ctx.author, _account.get_balance(), price / 10000
            ))

    @commands.command(aliases=["rgpg"])
    @commands.is_owner()
    async def regenplantgraphs(self, ctx):
        """(Owner) Regenerate plant price graphs."""
        all_plants = Plant.get_plants(self.bot.db_session)
        for _plant in all_plants:
            _plant.generate_prices_graph(self.bot.db_session)
        
        await ctx.send("**Successfully regenerated all price graphs.**")
    
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
    async def trashplots(self, ctx):
        """Discard the plants on all your plots. No refunds."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        for i in range(len(_farm.plots)):
            del _farm.plots[i]
        await ctx.send(MSG_DISCARD_ALL.format(ctx.author))
    
    @commands.command()
    @commands.is_owner()
    async def reconsolidatestorage(self, ctx):
        """(Owner) Manually reconsolidate all farm capacities."""
        all_farms = ORMFarm.get_all_farms(self.bot.db_session)
        for _farm in all_farms:
            harvest_count = 0
            for _harvest in _farm.harvests:
                harvest_count += _harvest.amount
            _farm.current_harvest = harvest_count
            self.bot.db_session.add(_farm)
        self.bot.db_session.commit()
        logging.info("Reconsolidated storages of {} farms.".format(len(all_farms)))
        await ctx.send("**All farm storages reconsolidated!**")
    
    @commands.command(aliases=["rpp"])
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
            _str = "***{0.name}*** `[B: {1:,.2f} gil | S: {2:,.2f} gil]`\n".format(plant, bp, sp)
            final_str += _str
        await ctx.send("**Prices refreshed!**\n{}".format(final_str))

    @commands.command(aliases=["fpa"])
    @commands.cooldown(1, 1, type=commands.BucketType.user)
    async def farmplant(self, ctx, plant_name, plant_count=1):
        """Plant a crop on a number of your available plots."""
        # Plant validation
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return
        
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        
        free_plots = _farm.get_free_plot_count()
        plant_count = min(plant_count, free_plots)
        total_price = _plant.buy_price * plant_count
        
        # Balance validation
        if not _account.has_balance(total_price, raw=True):
            await ctx.send(MSG_INSUFFICIENT_FUNDS.format(ctx.author, _account.get_balance()))
            return
        
        # Plot capacity validation
        if free_plots == 0:
            await ctx.send(MSG_PLOT_NOT_FOUND.format(ctx.author))
            return

        _account.add_debit(
            self.bot.db_session, total_price,
            name="B:{0.id}={0.buy_price}".format(_plant),
            raw=True,
        )

        _farm.plant_crop(_plant, self.bot.db_session, plot_range=plant_count)

        await ctx.send(
            MSG_PLOT_PLANT.format(
                ctx.author, _plant,
                plant_count, total_price/10000,
                _account.get_balance()
            )
        )

    @commands.command(aliases=["sh"])
    async def showharvests(self, ctx):
        """Show your harvest inventory."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        
        harvested_plants = set([i.plant for i in _farm.harvests])

        id_to_plant_name = {_plant.id: _plant.name for _plant in harvested_plants}
        total_harvests = {_plant.id: 0 for _plant in harvested_plants}

        if len(_farm.harvests) == 0:
            await ctx.send(MSG_SHOW_HARVESTS_NONE.format(ctx.author))
            return

        for harvest in _farm.harvests:
            total_harvests[harvest.plant.id] += harvest.amount

        harvest_str = ""

        embed = discord.Embed(
            title="{0.name}#{0.discriminator}'s Harvests".format(ctx.author),
            color=0xffd700
        )

        for harvest in total_harvests:
            harvest_str += "**{0}**, {1} units\n".format(
                id_to_plant_name[harvest],
                total_harvests[harvest]
            )

        embed.add_field(name="Crops", value=harvest_str, inline=False)
        
        # await ctx.send(MSG_SHOW_HARVESTS.format(ctx.author, harvest_str))
        await ctx.send(embed=embed)

    @commands.command(aliases=["fh"])
    @commands.cooldown(1, 20, type=commands.BucketType.user)
    async def farmharvest(self, ctx, options=None):
        """Harvest all your harvestable crops."""
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        plot_count = len(_farm.plots)

        all_plots = False

        storage_needed = 0
        for _plot in _farm.plots:
            storage_needed += _plot.get_harvest_amount()

        # Storage validation
        if not _farm.has_storage(storage_needed):
            await ctx.send(MSG_HARVEST_NOT_ENOUGH_CAPACITY.format(
                ctx.author,
                max(_farm.harvest_capacity - _farm.current_harvest, 0),
                storage_needed
            ))
            return
        if storage_needed == 0:
            await ctx.send(MSG_HARVEST_NONE.format(ctx.author))
            return

        # Actual harvesting
        await ctx.send("Harvesting **{0.name}#{0.discriminator}**'s crops...\n".format(ctx.author))

        # Collect harvesting info
        harvest_stats = {}
        for i in range(len(_farm.plots))[::-1]:
            _harvest = _farm.plots[i].harvest(self.bot.db_session, commit_on_execution=False)
            if _harvest is None:
                continue

            if _harvest.plant.name not in harvest_stats:
                harvest_stats[_harvest.plant.name] = 0
            harvest_stats[_harvest.plant.name] += _harvest.amount

            if _harvest.delete_plot:
                del _farm.plots[i]

        # Collate harvest info
        harvest_str = ""
        for plant_name in harvest_stats:
            _plant = Plant.get_plant(self.bot.db_session, plant_name)
            new_harvest = Harvest(
                plant=_plant,
                amount=harvest_stats[plant_name],
            )

            _farm.harvests.append(new_harvest)

            self.bot.db_session.add(_farm)

            harvest_str += "**{0}**, {1} units\n".format(
                plant_name, harvest_stats[plant_name]
            )
        
        # Commit to DB
        self.bot.db_session.commit()
        
        await ctx.send(MSG_HARVEST_SUCCESS.format(ctx.author, harvest_str))
        
    @commands.command(aliases=["pstats", "pstat"])
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def plantstats(self, ctx, plant_name):
        """Check plant price stats for the past 48 refreshes."""
        _plant = Plant.get_plant(self.bot.db_session, plant_name)
        if _plant is None:
            await ctx.send(MSG_PLANT_NOT_FOUND.format(ctx.author))
            return

        mean_sale = 0

        plant_stats_24h = _plant.price_logs
        plant_stats_24h = plant_stats_24h[:24]
        
        for _stats in plant_stats_24h:
            mean_sale += _stats.price
        
        mean_sale /= len(plant_stats_24h)
        
        plant_top = _plant.get_highest_sell_price()

        embed = discord.Embed(
            title="Statistics for {0.name} `{0.tag}`".format(_plant),
            color=0xffd700
        )

        embed.add_field(name="Yield", value="`{0.base_harvest}` units".format(_plant))
        embed.add_field(name="Buy Price", value="💵 `{0:,.2f}` gil/unit".format(_plant.get_buy_price()))
        embed.add_field(
            name="Highest Recorded Sale Price",
            value="💵 `{0:,.2f}` gil/unit\nAt `{1}`".format(
                plant_top.price / 10000,
                plant_top.refreshed_at.strftime("%I:%M %p - %d %B '%y")
            ),
            inline=False
        )
        embed.add_field(
            name="Base Sale Price",
            value="💵 `{0:,.2f}` gil/unit".format(_plant.base_sell_price / 10000),
        )
        embed.add_field(
            name="Current Sale Price",
            value="💵 `{0:,.2f}` gil/unit".format(_plant.get_sell_price()),
        )
        embed.add_field(
            name="Mean Sale Price (Past 24 Hours)",
            value="💵 `{0:,.2f}` gil/unit".format(mean_sale / 10000),
            inline=False
        )
        embed.add_field(
            name="Current Demand",
            value="`{0:,} / {1:,}` units".format(
                _plant.current_demand, _plant.base_demand
            ),
            inline=False
        )

        graph_file = PLANT_PRICE_GRAPH_DIRECTORY + "{}.png".format(_plant.tag.upper())
        graph = discord.File(graph_file, filename="image.png")
        embed.set_image(url="attachment://image.png")

        await ctx.send(embed=embed, file=graph)
        # await ctx.send(embed=embed)

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
        
        plant_sell_price = _plant.get_sell_price(raw=True)
        raw_credit = total_amount * plant_sell_price
        _account.add_credit(
            self.bot.db_session, raw_credit,
            name="S:{0.id}={1}".format(_plant, total_amount),
            raw=True
        )
        
        _plant.decrement_demand(self.bot.db_session, total_amount)
        _farm.decrease_storage(self.bot.db_session, total_amount)

        await ctx.send(MSG_SELL_SUCCESS.format(
            ctx.author, total_amount, _plant, raw_credit / 10000, _account.get_balance(),
            plant_sell_price / 10000
        ))

    @commands.command(aliases=["fprestige", "fpr"])
    async def farmprestige(self, ctx):
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)
        _profile = Profile.get_profile(ctx.author, self.bot.db_session)

        def is_author(m):
            return m.author == ctx.author

        if not _farm.can_prestige():
            await ctx.send("**{0.mention}, you have to reach maximum plot capacity before doing a prestige reset.**".format(
                ctx.author
            ))
            return

        confirmation = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        await ctx.send("{0.mention}, please send `{1}` to confirm your prestige reset.".format(
            ctx.author, confirmation
        ))

        try:
            msg = await self.bot.wait_for("message", check=is_author, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("**{0.mention}, your confirmation timed out.**".format(ctx.author))
            return
        if msg.content != confirmation:
            await ctx.send("**{0.mention}, your confirmation did not match.**".format(ctx.author))
            return

        materia_diff = _profile.apply_farm_prestige(self.bot.db_session, _account.get_balance(raw=True))
        self.bot.db_session.delete(_farm)
        self.bot.db_session.delete(_account)
        self.bot.db_session.commit()

        await ctx.send("**{0.mention}, you have now reset your farm.** You are now **Farm Prestige level {1}**, and gained **{2} 💎 Materia**.".format(
            ctx.author, _profile.farm_prestige, materia_diff
        ))

    @commands.command()
    async def declarebankruptcy(self, ctx):
        _farm = ORMFarm.get_farm(ctx.author, self.bot.db_session)
        _account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)

        def is_author(m):
            return m.author == ctx.author

        confirmation = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        await ctx.send("{0.mention}, please send `{1}` to confirm bankruptcy.".format(
            ctx.author, confirmation
        ))

        try:
            msg = await self.bot.wait_for("message", check=is_author, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("**{0.mention}, your confirmation timed out.**".format(ctx.author))
            return
        if msg.content != confirmation:
            await ctx.send("**{0.mention}, your confirmation did not match.**".format(ctx.author))
            return

        await ctx.send("**{0.mention}, you have now declared your bankruptcy.**".format(ctx.author))
        self.bot.db_session.delete(_farm)
        self.bot.db_session.delete(_account)
        self.bot.db_session.commit()

def refresh_prices(bot):
    logging.info("Refreshing farm market prices...")
    all_plants = Plant.get_plants(bot.db_session)
    for plant in all_plants:
        plant.randomize_price(bot.db_session, commit_on_execution=False)
    bot.db_session.commit()


def setup(bot):
    bot.add_cog(Farm(bot))
    schedule.every().hour.at(":00").do(refresh_prices, bot)
