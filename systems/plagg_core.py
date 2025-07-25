from discord.ext import commands
import random

PLAGG_QUOTES = [
    "Got any cheese? 🧀",
    "Let's cause some chaos!",
    "Miraculous, simply the best!",
    "Don't blame me if things go wrong..."
]

class PlaggCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def plagg(self, ctx):
        """Get a random Plagg quote."""
        await ctx.send(random.choice(PLAGG_QUOTES))

async def setup(bot):
    await bot.add_cog(PlaggCore(bot)) 