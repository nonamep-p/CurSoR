import discord
from discord.ext import commands
from ui.embeds import help_embed
from ui.views import HelpDropdownView

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        async def update_embed(interaction, category):
            if category == "all" or category == "getting_started":
                embed = help_embed()
            else:
                embed = help_embed(category)
            await interaction.response.edit_message(embed=embed, view=HelpDropdownView(update_embed))
        embed = help_embed()
        view = HelpDropdownView(update_embed)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot)) 