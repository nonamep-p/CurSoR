from discord.ext import commands

class Matchmaking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add commands for matchmaking

async def setup(bot):
    await bot.add_cog(Matchmaking(bot)) 