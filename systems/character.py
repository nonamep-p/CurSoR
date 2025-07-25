import discord
from discord.ext import commands
from ui.embeds import player_profile_embed
import json
import os

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """Show a player's profile."""
        user = member or ctx.author
        user_id = str(user.id)
        players_file = os.path.join("data", "players.json")
        try:
            with open(players_file, "r") as f:
                all_players = json.load(f)
        except Exception:
            all_players = {}
        player = all_players.get(user_id, {
            "username": user.display_name,
            "class": "Unassigned",
            "level": 1,
            "hp": 100,
            "max_hp": 100,
            "gold": 0
        })
        embed = player_profile_embed(player)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Character(bot)) 