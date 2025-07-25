import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)

# Modular cog loading
initial_cogs = [
    "systems.combat",
    "systems.character",
    "systems.inventory",
    "systems.economy",
    "systems.dungeon",
    "systems.shop",
    "systems.pvp",
    "systems.admin",
    "systems.achievement",
    "systems.guild",
    "systems.tutorial"
]

async def load_cogs():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await load_cogs()

bot.run(TOKEN) 