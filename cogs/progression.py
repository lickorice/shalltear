import logging

import discord, schedule
from discord.ext import commands

from config import *
from objects.core.profile import Profile
from roles import *


class Progression(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['rcr',], hidden=True)
    @commands.is_owner()
    async def reconsolidateroles(self, ctx):
        """(Owner) Register all users and assign them the proper roles"""
        all_users = ctx.guild.members
        
        # Store all roles in an id:Role dict
        id_to_leveled_roles = {
            LEVELED_ROLES[_r][0]: ctx.guild.get_role(LEVELED_ROLES[_r][0]) for _r in LEVELED_ROLES
        }

        # Also store all roles in a List
        all_leveled_roles = list(id_to_leveled_roles.values())

        # Iterate over all users
        for i in range(len(all_users)):
            _user = all_users[i]
            if _user.bot:
                continue
            _profile = Profile.get_profile(_user, self.bot.db_session)
            await _user.remove_roles(*all_leveled_roles)
            true_role = id_to_leveled_roles[_profile.get_top_leveled_role()]
            await _user.add_roles(true_role)
            await ctx.send("`[{0:08}/{1:08}]` Processed **{2}** => [`{3}`]".format(
                i+1, len(all_users)+1, _user.name, true_role.name
            ))
        await ctx.send("Role consolidation complete.")

    @commands.command(aliases=['stlvl',], hidden=True)
    @commands.is_owner()
    async def setlevel(self, ctx, target: discord.Member, lvl: int):
        """(Owner) Set the level of a user."""
        _profile = Profile.get_profile(target, self.bot.db_session)
        _profile.level = lvl-1
        _profile.level_up()
        self.bot.db_session.add(_profile)
        self.bot.db_session.commit()
        await ctx.send("Set the level of **{0}** to **{1}**.".format(
            target.name, lvl
        ))



def setup(bot):
    bot.add_cog(Progression(bot))
