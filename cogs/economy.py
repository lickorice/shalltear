import logging

import discord
from discord.ext import commands

from messages.core import *
from objects.economy_account import EconomyAccount


class Economy(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["$",])
    async def gil(self, ctx):
        """Returns current account's balance."""
        target_id = ctx.author.id
        # Get current economy account
        account = EconomyAccount.get_economy_account(target_id, self.bot.db_session)
        if account is None:
            account = EconomyAccount.create_economy_account(
                target_id, self.bot.db_session, not ctx.author.bot
            )
        print(account)


def setup(bot):
    bot.add_cog(Economy(bot))

