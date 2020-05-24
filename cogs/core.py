import logging
from datetime import timedelta
from time import time

import discord
from discord.ext import commands

import config
from messages.core import *
from objects.core.profile import Profile

start_time = time()


class Core(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 60, type=commands.BucketType.user)
    @commands.command()
    async def ping(self, ctx):
        """Tests responsiveness."""
        latency_in_ms = "{} ms".format(int(self.bot.latency * 1000))
        await ctx.send(CMD_PING.format(latency_in_ms))

    @commands.cooldown(1, 20, type=commands.BucketType.user)
    @commands.command(aliases=['p'])
    async def profile(self, ctx, target: discord.Member=None):
        """Show target's profile."""
        if target is None:
            target = ctx.author

        _profile = Profile.get_profile(target, self.bot.db_session)
        embed = discord.Embed(
            title="{0.name}#{0.discriminator}'s Profile".format(target),
            color=target.color,
        )

        embed.set_thumbnail(url=target.avatar_url)

        embed.add_field(name="Level", value="**{0}**".format(_profile.level))
        embed.add_field(name="Experience", value="**{0}** ({1} to next level)".format(
            _profile.experience, _profile.to_next - _profile.experience
        ), inline=False)
        embed.add_field(name="Materia", value="**💎 {0}**".format(_profile.materia))
        embed.add_field(name="Stars", value="**🌟 {0}**".format(_profile.meme_stars))
        embed.add_field(name="Farm Prestige", value="**{0}**".format(_profile.farm_prestige))

        await ctx.send(embed=embed)

    
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

