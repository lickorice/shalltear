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

    
    @commands.command()
    async def help(self, ctx, command=None):
        """Shows all the features the bot is able to do."""
        all_commands = [cmd for cmd in self.bot.commands]
        if command == None:
            embed = discord.Embed(title="Commands for Shalltear", color=0xff1155)
            for cog in self.bot.cogs:
                commands_for_cog = [f'`{c.name}`' for c in all_commands if not c.hidden and c.cog_name == cog]
                s = ' '.join(commands_for_cog)
                embed.add_field(name=cog, inline=False, value=s)
            await ctx.send("Do `s!help <command>` for more information.")
        else:
            if command not in [c.name for c in all_commands]:
                await ctx.send(MSG_CMD_NOT_FOUND.format(ctx.author))
                return
            cmd = [c for c in all_commands if c.name == command][0]
            if cmd.aliases:
                name = f'{cmd.name} [{"/".join(cmd.aliases)}]'
            else:
                name = cmd.name
            if cmd.clean_params:
                name += f' <{", ".join(cmd.clean_params)}>'
            name = '`{}`'.format(name)
            embed = discord.Embed(title=cmd.cog_name, color=0xff1155)
            embed.add_field(name=name, value=cmd.help)
        await ctx.send(embed=embed)

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

