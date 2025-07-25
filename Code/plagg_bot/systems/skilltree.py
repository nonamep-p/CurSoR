from discord.ext import commands

class SkillTree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add commands for skill tree management

async def setup(bot):
    await bot.add_cog(SkillTree(bot)) 