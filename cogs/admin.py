import logging

import discord, schedule
from discord.ext import commands

from config import *
from messages.admin import *
import utils.database as dbutils


class Admin(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["bk",], hidden=True)
    @commands.is_owner()
    async def backup(self, ctx):
        """Manually backup the database"""
        # TODO: Still only applicable for SQLite database.
        await ctx.send("**Backing up the database...**")

        backup_file = dbutils.backup()

        await ctx.send("**Database successfully backed up with filename `{0}`.**".format(
            backup_file
        ))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self, ctx):
        """(Owner) Shuts down the bot."""
        await ctx.send(MSG_SHUT_DOWN)
        await self.bot.logout()
        
    @commands.command(aliases=['rtt',], hidden=True)
    @commands.is_owner()
    async def rolestotext(self, ctx):
        """(Owner) Sends a message containing all the roles the guild has."""
        all_roles = ctx.guild.roles
        for _role in all_roles[::-1]:
            out_str = "`{0}` {1}\n".format(_role.id, _role.name)
            await ctx.send(out_str)

    @commands.command(aliases=['rlc',], hidden=True)
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


def backup_midnight():
    logging.info("Applying daily backup...")
    dbutils.backup()


def setup(bot):
    bot.add_cog(Admin(bot))
    schedule.every().day.at("00:00").do(backup_midnight)
