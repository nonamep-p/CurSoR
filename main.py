import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

COGS = [
    'systems.combat',
    'systems.progression',
    'systems.inventory',
    'systems.skilltree',
    'systems.dungeon',
    'systems.matchmaking',
    'systems.plagg_core',
    'ui.visual',
    'ui.embeds',
    'ui.buttons',
    'ui.skilltree_render',
    'ui.inventory_render',
]

@bot.event
async def on_ready():
    print(f"[Plagg] Ready to cause some chaos as {bot.user}!")

async def load_all_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")

async def main():
    await load_all_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 