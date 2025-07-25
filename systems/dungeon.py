from discord.ext import commands
import discord
import json
import os
import random
from systems.progression import Progression

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), '../data/players.json')
DUNGEONS_FILE = os.path.join(os.path.dirname(__file__), '../data/dungeons.json')

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_players(self):
        with open(PLAYERS_FILE, 'r') as f:
            return json.load(f)

    def save_players(self, players):
        with open(PLAYERS_FILE, 'w') as f:
            json.dump(players, f, indent=2)

    def load_dungeons(self):
        with open(DUNGEONS_FILE, 'r') as f:
            return json.load(f)

    @commands.command()
    async def dungeons(self, ctx):
        """List available dungeons."""
        dungeons = self.load_dungeons()
        desc = "\n".join([f"**{d['name']}**: {d['description']}" for d in dungeons.values()])
        await ctx.send(f"**Available Dungeons:**\n{desc}")

    @commands.command()
    async def dungeon(self, ctx, dungeon_name: str = None):
        """Explore a dungeon (e.g., !dungeon sewers)."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        dungeons = self.load_dungeons()
        if not dungeon_name or dungeon_name not in dungeons:
            await ctx.send(f"Plagg: {ctx.author.mention}, specify a valid dungeon. Use !dungeons to list them.")
            return
        dungeon = dungeons[dungeon_name]
        await ctx.send(f"Plagg: {ctx.author.mention} enters the **{dungeon['name']}**! {dungeon['description']}")
        # Simulate 3 random encounters
        for i in range(1, 4):
            encounter = random.choice(dungeon['enemies'])
            await ctx.send(f"Room {i}: You encounter a **{encounter}**!")
            # Simple win/lose simulation
            if random.random() < 0.8:
                await ctx.send(f"Plagg: {ctx.author.mention} defeats the {encounter}!")
            else:
                await ctx.send(f"Plagg: {ctx.author.mention} was defeated by the {encounter}! Dungeon run ends.")
                return
        # Rewards
        reward = random.choice(dungeon['rewards'])
        inv = players[user_id].setdefault('inventory', {})
        inv[reward] = inv.get(reward, 0) + 1
        # Award dungeon_crawler achievement
        Progression.award_achievement(self, players, user_id, "dungeon_crawler")
        self.save_players(players)
        await ctx.send(f"Plagg: {ctx.author.mention} completes the dungeon and finds a **{reward}**!")

async def setup(bot):
    await bot.add_cog(Dungeon(bot)) 