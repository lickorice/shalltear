import logging

import discord
from discord.ext import commands

from config import TRANSFER_TAX
from messages.economy import *
from objects.economy.account import EconomyAccount
import utils.numbers as numutils


class Economy(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["$",])
    async def gil(self, ctx, target: discord.Member=None):
        """Returns target account's balance."""
        if target is None:
            target = ctx.author
        # Get current economy account
        account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        await ctx.send(CMD_GIL.format(target, numutils.millify(account.get_balance(), is_money=True)))

    @commands.command(aliases=["$top",])
    async def giltop(self, ctx):
        """Returns top 10 global accounts according to gil-on-hand."""
        top_accounts = EconomyAccount.get_top_economy_accounts(self.bot.db_session, number=10)

        embed = discord.Embed(title="Top 10 Wealthiest Users", color=0xffd700)
        rank = 1
        for account in top_accounts:
            user = self.bot.get_user(account.user_id)
            user_name = "#{1} **{0.name}#{0.discriminator}**".format(user, rank)
            gil_amount = "💵 {0} gil".format(numutils.millify(account.get_balance(), is_money=True))
            embed.add_field(name=user_name, value=gil_amount, inline=False)
            rank += 1

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def registerall(self, ctx):
        """(Owner) Gives all users in guild economy accounts."""
        registered = 0
        for member in ctx.guild.members:
            k = EconomyAccount.get_economy_account(member, self.bot.db_session, create_if_not_exists=False)
            if k is None:
                k = EconomyAccount.create_economy_account(
                    member, self.bot.db_session,
                    member.bot or member.system, commit_on_execution=False
                )
                registered += 1
        self.bot.db_session.commit()
        logging.info("Registered {0} new accounts in the Economy database.".format(registered))

    @commands.command()
    @commands.is_owner()
    async def admingive(self, ctx, amount: float, target: discord.Member=None):
        """(Owner) Grant target gil."""
        if amount < 0:
            await ctx.send(CMD_GIVE_INVALID_AMOUNT)
            return
        if target is None:
            target = ctx.author
        target_account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        target_account.add_credit(self.bot.db_session, amount, "Admin grant.")
        await ctx.send(CMD_ADMIN_GIVE.format(target, numutils.millify(amount, is_money=True)))

    @commands.command()
    @commands.is_owner()
    async def admintake(self, ctx, amount: float, target: discord.Member=None):
        """(Owner) Deduct target's gil."""
        if amount < 0:
            await ctx.send(CMD_GIVE_INVALID_AMOUNT)
            return
        if target is None:
            target = ctx.author
        target_account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        target_account.add_debit(self.bot.db_session, amount, "Admin grant.")
        await ctx.send(CMD_ADMIN_TAKE.format(target, numutils.millify(amount, is_money=True)))

    @commands.command()
    @commands.is_owner()
    async def reconsolidateall(self, ctx, target: discord.Member=None):
        """(Owner) Reconsolidate the whole database's balances."""
        if target is None:
            all_accounts = EconomyAccount.get_all_economy_accounts(self.bot.db_session)
            inconsistent_accounts = 0
            for account in all_accounts:
                # We disable committing here to optimize SQL query execution time
                result = account.reconsolidate_balance(self.bot.db_session, commit_on_execution=False)
                if not result:
                    inconsistent_accounts += 1
            self.bot.db_session.commit()
            await ctx.send(CMD_RECONSOLIDATE_MASS.format(len(all_accounts), inconsistent_accounts))
        else:
            target_account = EconomyAccount.get_economy_account(target, self.bot.db_session)
            result = target_account.reconsolidate_balance(self.bot.db_session)
            if result:
                await ctx.send(CMD_RECONSOLIDATE_TRUE.format(target))
            else:
                await ctx.send(CMD_RECONSOLIDATE_FALSE.format(target))

    @commands.command()
    async def give(self, ctx, amount: float, target: discord.Member):
        """Give gil to another user, with a 1 percent tax deduction.."""
        if amount < 0:
            await ctx.send(CMD_GIVE_INVALID_AMOUNT)
            return
        if target == ctx.author:
            await ctx.send("**{0.mention}, you can't transfer money to yourself.**")
        credit = amount * (1 - TRANSFER_TAX)
        debit = amount

        target_account = EconomyAccount.get_economy_account(target, self.bot.db_session)
        author_account = EconomyAccount.get_economy_account(ctx.author, self.bot.db_session)

        if not author_account.has_balance(debit):
            await ctx.send(
                CMD_GIVE_INSUFFICIENT_AMOUNT.format(ctx.author, numutils.millify(target_account.get_balance(), is_money=True))
            )
            return

        target_account.add_credit(self.bot.db_session, credit, "T:{}".format(ctx.author.id))
        author_account.add_debit(self.bot.db_session, debit, "T:{}".format(target.id))

        await ctx.send(CMD_GIVE_SUCCESS.format(ctx.author, numutils.millify(credit, is_money=True), target))


def setup(bot):
    bot.add_cog(Economy(bot))

