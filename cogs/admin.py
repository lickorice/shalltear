import logging

import discord
from discord.ext import commands

from config import *
from messages.admin import *


class Admin(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def tester(self, ctx):
        guilds = self.bot.guilds
        for g in guilds:
            logging.info("[{0.id}] {0.name}".format(g))
            # await ctx.send("{0.name} ({0.id})".format(g))

    @commands.command()
    @commands.is_owner()
    async def kill(self, ctx):
        """(Owner) Shuts down the bot."""
        await ctx.send(MSG_SHUT_DOWN)
        await self.bot.logout()

    @commands.command(aliases=['rlc',])
    @commands.is_owner()
    async def reloadcogs(self, ctx, *cogs):
        """(Owner) Reload specified cogs. If no cog is specified, reloads all cogs."""
        if not len(cogs):
            to_reload_cogs = ACTIVE_COGS
        else:
            to_reload_cogs = [cog for cog in cogs if cog in ACTIVE_COGS]

        print("=====================================")
        logging.info("Starting reloading sequence...")
        print("=====================================")
        successful_cogs = []
        for cog in to_reload_cogs:
            logging.info("Reloading cog '{}'".format(cog))
            try:
                self.bot.reload_extension(cog)
                successful_cogs.append(cog)
                logging.info("Successfully reloaded cog '{}'".format(cog))
            except Exception as e:
                logging.error(e)
                logging.error("Reload failed for cog '{}'".format(cog))

        print("=====================================")
        cogs_success, total_cogs = len(successful_cogs), len(to_reload_cogs)
        logging.info("Successfully reloaded {}/{} cogs! ".format(cogs_success, total_cogs))
        print("=====================================")
        if cogs_success:
            await ctx.send("Successfully reloaded:\n{}".format('\n'.join(successful_cogs)))
        else:
            await ctx.send("No cogs have been successfully reloaded.")


def setup(bot):
    bot.add_cog(Admin(bot))

