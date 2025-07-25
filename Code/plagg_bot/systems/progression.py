from discord.ext import commands

class Progression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add commands and logic for XP, leveling, etc.

async def setup(bot):
    await bot.add_cog(Progression(bot)) 