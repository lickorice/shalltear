import discord
from discord.ext import commands


class Core(commands.Cog):
    def  __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, *, member: discord.Member = None):
        """Tests responsiveness."""
        member = member or ctx.author
        await ctx.send("Pong!")


def setup(bot):
    bot.add_cog(Core(bot))

