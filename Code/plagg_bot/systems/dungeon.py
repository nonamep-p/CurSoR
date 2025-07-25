from discord.ext import commands

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add commands for dungeon crawling

async def setup(bot):
    await bot.add_cog(Dungeon(bot)) 