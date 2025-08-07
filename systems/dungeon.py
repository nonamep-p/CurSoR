import discord
from discord.ext import commands
import random
import json
import os
from ui.visual import format_hp_bar

class DungeonView(discord.ui.View):
    def __init__(self, actions):
        super().__init__(timeout=30)
        self.value = None
        for action in actions:
            self.add_item(DungeonButton(action))

class DungeonButton(discord.ui.Button):
    def __init__(self, action):
        super().__init__(label=action, style=discord.ButtonStyle.primary)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.action
        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(content=f"You chose **{self.action}**!", view=self.view)
        self.view.stop()

class Dungeon(commands.Cog):
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

    def load_dungeons(self):
        dungeons_file = os.path.join("data", "dungeons.json")
        try:
            with open(dungeons_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_monsters(self):
        monsters_file = os.path.join("data", "monsters.json")
        try:
            with open(monsters_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_items(self):
        items_file = os.path.join("data", "items.json")
        try:
            with open(items_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    @commands.command()
    async def dungeons(self, ctx):
        """List available dungeons and their requirements."""
        dungeons = self.load_dungeons()
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first! Use `!startrpg <class>`")
            return
        
        player = players[user_id]
        embed = discord.Embed(
            title="🗺️ Available Dungeons",
            description="Explore these dangerous locations for loot and experience!",
            color=discord.Color.dark_green()
        )
        
        for dungeon_id, dungeon_data in dungeons.items():
            progress = player.get("dungeon_progress", {}).get(dungeon_id, {"current_floor": 1, "completed_floors": []})
            current_floor = progress["current_floor"]
            completed_floors = progress["completed_floors"]
            
            # Get floor info
            floor_data = dungeon_data["floors"].get(str(current_floor), {})
            min_level = floor_data.get("min_level", 1)
            
            status = "✅ Available" if player["level"] >= min_level else f"❌ Requires Level {min_level}"
            progress_text = f"Floor {current_floor}/3 | Completed: {len(completed_floors)}"
            
            embed.add_field(
                name=f"🏰 {dungeon_data['name']}",
                value=f"{dungeon_data['description']}\n"
                      f"**Status:** {status}\n"
                      f"**Progress:** {progress_text}",
                inline=False
            )
        
        embed.set_footer(text="Use !enter <dungeon_name> to enter a dungeon")
        await ctx.send(embed=embed)

    @commands.command()
    async def enter(self, ctx, dungeon_name: str = None):
        """Enter a dungeon to fight monsters and find loot."""
        if not dungeon_name:
            await ctx.send(f"Plagg: {ctx.author.mention}, specify a dungeon! Available: forest, cave, castle, abyss")
            return
        
        players = self.load_players()
        dungeons = self.load_dungeons()
        monsters = self.load_monsters()
        items = self.load_items()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first! Use `!startrpg <class>`")
            return
        
        player = players[user_id]
        dungeon_name = dungeon_name.lower()
        
        if dungeon_name not in dungeons:
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a valid dungeon! Available: forest, cave, castle, abyss")
            return
        
        dungeon_data = dungeons[dungeon_name]
        progress = player.get("dungeon_progress", {}).get(dungeon_name, {"current_floor": 1, "completed_floors": []})
        current_floor = progress["current_floor"]
        
        floor_data = dungeon_data["floors"].get(str(current_floor), {})
        min_level = floor_data.get("min_level", 1)
        
        if player["level"] < min_level:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to be level {min_level} to enter this floor!")
            return
        
        # Check if player has enough HP
        if player["hp"] <= 0:
            await ctx.send(f"Plagg: {ctx.author.mention}, you're too injured to enter a dungeon! Rest first.")
            return
        
        embed = discord.Embed(
            title=f"🏰 Entering {dungeon_data['name']}",
            description=f"Floor {current_floor}: {floor_data['name']}\n{floor_data['description']}",
            color=discord.Color.dark_red()
        )
        
        # Show available monsters
        monster_list = floor_data.get("monsters", [])
        monster_text = ""
        for monster_id in monster_list:
            if monster_id in monsters:
                monster = monsters[monster_id]
                monster_text += f"• **{monster['name']}** - {monster['description']}\n"
        
        embed.add_field(name="Monsters Found Here", value=monster_text, inline=False)
        
        # Show potential rewards
        reward_items = floor_data.get("items", [])
        reward_text = ""
        for item_id in reward_items:
            if item_id in items:
                item = items[item_id]
                reward_text += f"• **{item['name']}** - {item['description']}\n"
        
        embed.add_field(name="Potential Loot", value=reward_text, inline=False)
        embed.add_field(name="Rewards", value=f"EXP: {floor_data.get('exp_reward', 0)} | Gold: {floor_data.get('gold_reward', 0)}", inline=True)
        
        await ctx.send(embed=embed)
        
        # Start dungeon encounter
        await self.start_dungeon_encounter(ctx, player, dungeon_name, current_floor, monsters, items)

    async def start_dungeon_encounter(self, ctx, player, dungeon_name, floor_num, monsters, items):
        """Handle a dungeon encounter with monsters."""
        dungeons = self.load_dungeons()
        dungeon_data = dungeons[dungeon_name]
        floor_data = dungeon_data["floors"][str(floor_num)]
        
        # Choose a random monster
        monster_list = floor_data.get("monsters", [])
        if not monster_list:
            await ctx.send("Plagg: This floor seems empty...")
            return
        
        monster_id = random.choice(monster_list)
        if monster_id not in monsters:
            await ctx.send("Plagg: Something went wrong with the monster selection!")
            return
        
        monster = monsters[monster_id]
        
        # Check for boss
        boss_id = floor_data.get("boss")
        if boss_id and boss_id in monsters:
            # 10% chance to encounter boss
            if random.random() < 0.1:
                monster = monsters[boss_id]
                monster_id = boss_id
        
        embed = discord.Embed(
            title=f"⚔️ {monster['name']} appears!",
            description=monster['description'],
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Monster Stats",
            value=f"HP: {monster['hp']} | Attack: {monster['attack']} | Defense: {monster['defense']} | Speed: {monster['speed']}",
            inline=False
        )
        
        embed.add_field(
            name="Your Stats",
            value=f"HP: {player['hp']} | Attack: {player['attack']} | Defense: {player['defense']} | Speed: {player['speed']}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Start combat
        await self.dungeon_combat(ctx, player, monster, monster_id, dungeon_name, floor_num, monsters, items)

    async def dungeon_combat(self, ctx, player, monster, monster_id, dungeon_name, floor_num, monsters, items):
        """Handle combat between player and monster."""
        monster_hp = monster['hp']
        player_hp = player['hp']
        
        embed = discord.Embed(
            title="⚔️ Combat Started!",
            description=f"Fighting {monster['name']}!",
            color=discord.Color.orange()
        )
        
        # Show initial HP bars
        embed.add_field(
            name="Health Bars",
            value=f"**You:** {format_hp_bar(player_hp, player['max_hp'])}\n"
                  f"**{monster['name']}:** {format_hp_bar(monster_hp, monster['hp'])}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Combat loop
        turn = 0
        while player_hp > 0 and monster_hp > 0:
            turn += 1
            
            # Player's turn
            if turn % 2 == 1:
                # Simple AI for player - just attack
                damage = max(1, player['attack'] - monster['defense'])
                monster_hp = max(0, monster_hp - damage)
                
                embed = discord.Embed(
                    title="⚔️ Your Turn",
                    description=f"You attack {monster['name']} for **{damage}** damage!",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="Health Bars",
                    value=f"**You:** {format_hp_bar(player_hp, player['max_hp'])}\n"
                          f"**{monster['name']}:** {format_hp_bar(monster_hp, monster['hp'])}",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
                if monster_hp <= 0:
                    break
                    
                await asyncio.sleep(1)  # Brief pause for readability
            
            # Monster's turn
            else:
                damage = max(1, monster['attack'] - player['defense'])
                player_hp = max(0, player_hp - damage)
                
                embed = discord.Embed(
                    title="⚔️ Monster's Turn",
                    description=f"{monster['name']} attacks you for **{damage}** damage!",
                    color=discord.Color.red()
                )
                
                embed.add_field(
                    name="Health Bars",
                    value=f"**You:** {format_hp_bar(player_hp, player['max_hp'])}\n"
                          f"**{monster['name']}:** {format_hp_bar(monster_hp, monster['hp'])}",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
                if player_hp <= 0:
                    break
                    
                await asyncio.sleep(1)  # Brief pause for readability
        
        # Combat result
        if player_hp > 0:
            await self.handle_victory(ctx, player, monster, monster_id, dungeon_name, floor_num, monsters, items)
        else:
            await self.handle_defeat(ctx, player, monster)

    async def handle_victory(self, ctx, player, monster, monster_id, dungeon_name, floor_num, monsters, items):
        """Handle player victory in dungeon combat."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        # Give rewards
        exp_gained = monster['exp_reward']
        gold_gained = monster['gold_reward']
        
        # Update player stats
        player['exp'] += exp_gained
        player['gold'] += gold_gained
        player['hp'] = max(1, player['hp'])  # Don't let player die from victory
        
        # Check for level up
        level_up = False
        while player['exp'] >= player['exp_to_next']:
            player['exp'] -= player['exp_to_next']
            player['level'] += 1
            player['exp_to_next'] = int(player['exp_to_next'] * 1.2)  # Increase exp requirement
            level_up = True
        
        # Handle loot drops
        loot_drops = []
        for item_id in monster.get('loot_table', []):
            if random.random() < 0.3:  # 30% chance for each item
                if item_id not in player['inventory']:
                    player['inventory'][item_id] = 0
                player['inventory'][item_id] += 1
                loot_drops.append(item_id)
        
        # Save player data
        players[user_id] = player
        self.save_players(players)
        
        # Create victory embed
        embed = discord.Embed(
            title="🎉 Victory!",
            description=f"You defeated {monster['name']}!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Rewards", value=f"EXP: +{exp_gained} | Gold: +{gold_gained}", inline=True)
        
        if loot_drops:
            loot_text = ""
            for item_id in loot_drops:
                if item_id in items:
                    loot_text += f"• **{items[item_id]['name']}**\n"
            embed.add_field(name="Loot Found", value=loot_text, inline=True)
        
        if level_up:
            embed.add_field(name="🎊 Level Up!", value=f"You are now level {player['level']}!", inline=False)
        
        embed.add_field(name="Current Status", value=f"HP: {player['hp']} | EXP: {player['exp']}/{player['exp_to_next']} | Gold: {player['gold']}", inline=False)
        
        await ctx.send(embed=embed)

    async def handle_defeat(self, ctx, player, monster):
        """Handle player defeat in dungeon combat."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        # Penalty for defeat
        gold_lost = min(player['gold'], 10)  # Lose up to 10 gold
        player['gold'] -= gold_lost
        player['hp'] = 1  # Set to 1 HP
        
        # Save player data
        players[user_id] = player
        self.save_players(players)
        
        embed = discord.Embed(
            title="💀 Defeat!",
            description=f"You were defeated by {monster['name']}!",
            color=discord.Color.dark_red()
        )
        
        embed.add_field(name="Penalties", value=f"Gold Lost: {gold_lost} | HP: 1", inline=True)
        embed.add_field(name="Advice", value="Rest to recover HP before trying again!", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def rest(self, ctx):
        """Rest to recover HP and MP."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        player = players[user_id]
        
        # Calculate recovery
        hp_recovery = min(player['max_hp'] - player['hp'], 50)  # Recover up to 50 HP
        mp_recovery = min(player['max_mp'] - player['mp'], 30)  # Recover up to 30 MP
        
        player['hp'] = min(player['max_hp'], player['hp'] + hp_recovery)
        player['mp'] = min(player['max_mp'], player['mp'] + mp_recovery)
        
        players[user_id] = player
        self.save_players(players)
        
        embed = discord.Embed(
            title="😴 Rest Complete",
            description="You feel refreshed!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Recovery", value=f"HP: +{hp_recovery} | MP: +{mp_recovery}", inline=True)
        embed.add_field(name="Current Status", value=f"HP: {player['hp']}/{player['max_hp']} | MP: {player['mp']}/{player['max_mp']}", inline=True)
        
        await ctx.send(embed=embed)

import asyncio

async def setup(bot):
    await bot.add_cog(Dungeon(bot)) 