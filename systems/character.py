import discord
from discord.ext import commands
from ui.embeds import player_profile_embed
import json
import os
import random

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_players(self):
        players_file = os.path.join("data", "players.json")
        try:
            with open(players_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_players(self, players):
        players_file = os.path.join("data", "players.json")
        with open(players_file, "w") as f:
            json.dump(players, f, indent=2)

    def load_classes(self):
        classes_file = os.path.join("data", "classes.json")
        try:
            with open(classes_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def calculate_stats(self, player_data, class_data):
        """Calculate player stats based on level and class"""
        level = player_data.get("level", 1)
        base_stats = class_data.get("base_stats", {})
        stat_growth = class_data.get("stat_growth", {})
        
        stats = {}
        for stat in base_stats:
            base_value = base_stats[stat]
            growth_value = stat_growth.get(stat, 0)
            stats[stat] = base_value + (growth_value * (level - 1))
        
        return stats

    @commands.command()
    async def startrpg(self, ctx, class_name: str = None):
        """Start your RPG adventure! Choose a class: warrior, mage, rogue, paladin, archer, berserker, druid, monk"""
        players = self.load_players()
        classes = self.load_classes()
        user_id = str(ctx.author.id)
        
        if user_id in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you've already started your adventure! Use !profile to see your character.")
            return
        
        if not class_name:
            class_list = ", ".join(classes.keys())
            await ctx.send(f"Plagg: {ctx.author.mention}, choose a class: **{class_list}**\nExample: `!startrpg warrior`")
            return
        
        class_name = class_name.lower()
        if class_name not in classes:
            class_list = ", ".join(classes.keys())
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a valid class! Choose from: **{class_list}**")
            return
        
        class_data = classes[class_name]
        stats = self.calculate_stats({"level": 1}, class_data)
        
        # Create new player
        player_data = {
            "username": ctx.author.display_name,
            "class": class_name,
            "level": 1,
            "exp": 0,
            "exp_to_next": 100,
            "hp": stats["hp"],
            "max_hp": stats["hp"],
            "mp": stats["mp"],
            "max_mp": stats["mp"],
            "attack": stats["attack"],
            "defense": stats["defense"],
            "magic": stats["magic"],
            "speed": stats["speed"],
            "gold": 50,
            "inventory": {},
            "equipment": {
                "weapon": None,
                "armor": None,
                "accessory": None
            },
            "skills": class_data.get("skills", []),
            "skill_levels": {},
            "achievements": [],
            "dungeon_progress": {
                "forest": {"current_floor": 1, "completed_floors": []},
                "cave": {"current_floor": 1, "completed_floors": []},
                "castle": {"current_floor": 1, "completed_floors": []},
                "abyss": {"current_floor": 1, "completed_floors": []}
            },
            "daily_quests": {
                "last_reset": None,
                "completed_today": 0,
                "quests": []
            },
            "created_at": str(ctx.message.created_at)
        }
        
        # Give starting equipment
        starting_equipment = class_data.get("starting_equipment", [])
        for item in starting_equipment:
            player_data["inventory"][item] = player_data["inventory"].get(item, 0) + 1
        
        players[user_id] = player_data
        self.save_players(players)
        
        embed = discord.Embed(
            title="🎮 Adventure Begins!",
            description=f"Welcome to the world, **{ctx.author.display_name}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="Class", value=f"**{class_data['name']}**", inline=True)
        embed.add_field(name="Description", value=class_data['description'], inline=False)
        embed.add_field(name="Starting Stats", value=f"HP: {stats['hp']} | MP: {stats['mp']} | ATK: {stats['attack']} | DEF: {stats['defense']}", inline=False)
        embed.add_field(name="Starting Equipment", value=", ".join(starting_equipment) if starting_equipment else "None", inline=False)
        embed.set_footer(text="Use !help to see available commands!")
        
        await ctx.send(f"Plagg: {ctx.author.mention} has started their adventure!", embed=embed)

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """Show a player's profile."""
        user = member or ctx.author
        user_id = str(user.id)
        players = self.load_players()
        classes = self.load_classes()
        
        if user_id not in players:
            if user == ctx.author:
                await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first! Use `!startrpg <class>`")
            else:
                await ctx.send(f"Plagg: {user.mention} hasn't started their adventure yet!")
            return
        
        player = players[user_id]
        class_data = classes.get(player["class"], {})
        
        # Calculate current stats with equipment bonuses
        base_stats = self.calculate_stats(player, class_data)
        current_stats = base_stats.copy()
        
        # Add equipment bonuses
        equipment = player.get("equipment", {})
        items = self.load_items()
        
        for slot, item_id in equipment.items():
            if item_id and item_id in items:
                item = items[item_id]
                for stat, bonus in item.items():
                    if stat in ["attack", "defense", "magic", "speed", "hp", "mp"]:
                        current_stats[stat] = current_stats.get(stat, 0) + bonus
        
        embed = discord.Embed(
            title=f"📊 {user.display_name}'s Profile",
            color=discord.Color.blue()
        )
        
        # Basic info
        embed.add_field(
            name="Character Info",
            value=f"**Class:** {class_data.get('name', 'Unknown')}\n"
                  f"**Level:** {player['level']}\n"
                  f"**Experience:** {player['exp']}/{player['exp_to_next']}\n"
                  f"**Gold:** {player['gold']} 🪙",
            inline=True
        )
        
        # Stats
        stats_text = f"**HP:** {player['hp']}/{current_stats['hp']}\n"
        stats_text += f"**MP:** {player['mp']}/{current_stats['mp']}\n"
        stats_text += f"**Attack:** {current_stats['attack']}\n"
        stats_text += f"**Defense:** {current_stats['defense']}\n"
        stats_text += f"**Magic:** {current_stats['magic']}\n"
        stats_text += f"**Speed:** {current_stats['speed']}"
        
        embed.add_field(name="Stats", value=stats_text, inline=True)
        
        # Equipment
        equipment_text = ""
        for slot, item_id in equipment.items():
            if item_id and item_id in items:
                equipment_text += f"**{slot.title()}:** {items[item_id]['name']}\n"
            else:
                equipment_text += f"**{slot.title()}:** None\n"
        
        embed.add_field(name="Equipment", value=equipment_text, inline=True)
        
        # Skills
        skills = player.get("skills", [])
        if skills:
            skills_text = ", ".join(skills[:5])  # Show first 5 skills
            if len(skills) > 5:
                skills_text += f" (+{len(skills) - 5} more)"
            embed.add_field(name="Skills", value=skills_text, inline=False)
        
        # Achievements
        achievements = player.get("achievements", [])
        if achievements:
            embed.add_field(name="Achievements", value=f"{len(achievements)} achievements earned!", inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Adventure started: {player.get('created_at', 'Unknown')}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def classinfo(self, ctx, class_name: str = None):
        """Get information about available classes."""
        classes = self.load_classes()
        
        if not class_name:
            embed = discord.Embed(
                title="🎭 Available Classes",
                description="Choose your path to adventure!",
                color=discord.Color.purple()
            )
            
            for class_id, class_data in classes.items():
                embed.add_field(
                    name=f"{class_data['name']}",
                    value=f"{class_data['description']}\n"
                          f"HP: {class_data['base_stats']['hp']} | MP: {class_data['base_stats']['mp']} | "
                          f"ATK: {class_data['base_stats']['attack']} | DEF: {class_data['base_stats']['defense']}",
                    inline=False
                )
            
            embed.set_footer(text="Use !classinfo <class_name> for detailed information")
            await ctx.send(embed=embed)
            return
        
        class_name = class_name.lower()
        if class_name not in classes:
            class_list = ", ".join(classes.keys())
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a valid class! Available classes: **{class_list}**")
            return
        
        class_data = classes[class_name]
        embed = discord.Embed(
            title=f"🎭 {class_data['name']}",
            description=class_data['description'],
            color=discord.Color.gold()
        )
        
        # Base stats
        base_stats = class_data['base_stats']
        stats_text = f"**HP:** {base_stats['hp']}\n"
        stats_text += f"**MP:** {base_stats['mp']}\n"
        stats_text += f"**Attack:** {base_stats['attack']}\n"
        stats_text += f"**Defense:** {base_stats['defense']}\n"
        stats_text += f"**Magic:** {base_stats['magic']}\n"
        stats_text += f"**Speed:** {base_stats['speed']}"
        
        embed.add_field(name="Base Stats", value=stats_text, inline=True)
        
        # Stat growth
        stat_growth = class_data['stat_growth']
        growth_text = f"**HP:** +{stat_growth['hp']}/level\n"
        growth_text += f"**MP:** +{stat_growth['mp']}/level\n"
        growth_text += f"**Attack:** +{stat_growth['attack']}/level\n"
        growth_text += f"**Defense:** +{stat_growth['defense']}/level\n"
        growth_text += f"**Magic:** +{stat_growth['magic']}/level\n"
        growth_text += f"**Speed:** +{stat_growth['speed']}/level"
        
        embed.add_field(name="Stat Growth", value=growth_text, inline=True)
        
        # Skills
        skills = class_data.get('skills', [])
        if skills:
            embed.add_field(name="Starting Skills", value=", ".join(skills), inline=False)
        
        # Starting equipment
        equipment = class_data.get('starting_equipment', [])
        if equipment:
            embed.add_field(name="Starting Equipment", value=", ".join(equipment), inline=False)
        
        embed.set_footer(text=f"Use !startrpg {class_name} to choose this class!")
        await ctx.send(embed=embed)

    def load_items(self):
        items_file = os.path.join("data", "items.json")
        try:
            with open(items_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

async def setup(bot):
    await bot.add_cog(Character(bot)) 