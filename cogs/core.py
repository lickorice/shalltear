import logging
from datetime import timedelta
from time import time

import discord
from discord.ext import commands

from messages.core import *
from config import CURRENT_VERSION

start_time = time()


class Core(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Tests responsiveness."""
        latency_in_ms = "{} ms".format(int(self.bot.latency * 1000))
        await ctx.send(CMD_PING.format(latency_in_ms))

    @commands.command(aliases=['info'])
    async def about(self, ctx):
        """Shows information about the bot."""
        difference = int(round(time() - start_time))
        uptime_str = str(timedelta(seconds=difference))
        embed = discord.Embed(title="About Bot", color=0xe73895)
        embed.add_field(
            name="Author",
            value="Carlos Panganiban"
        )
        embed.add_field(
            name="Source Code",
            value="https://github.com/lickorice/shalltear"
        )
        embed.add_field(
            name="Uptime",
            value=uptime_str,
            inline=False
        )
        embed.add_field(
            name="Version",
            value=CURRENT_VERSION
        )
        embed.set_footer(text="cgpanganiban@up.edu.ph | University of the Philippines Diliman")
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))

