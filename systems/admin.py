import discord
from discord.ext import commands
import json
import os

class Admin(commands.Cog):
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

    def load_items(self):
        items_file = os.path.join("data", "items.json")
        try:
            with open(items_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    async def cog_check(self, ctx):
        """Check if user has admin permissions."""
        return ctx.author.guild_permissions.administrator or ctx.author.id == ctx.guild.owner_id

    @commands.command()
    async def giveitem(self, ctx, member: discord.Member, item_name: str, quantity: int = 1):
        """Give an item to a player (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        players = self.load_players()
        items = self.load_items()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        # Find item by name (case insensitive)
        item_id = None
        for iid, item_data in items.items():
            if item_data['name'].lower() == item_name.lower():
                item_id = iid
                break
        
        if not item_id:
            await ctx.send(f"Plagg: That item doesn't exist!")
            return
        
        # Add item to player's inventory
        if 'inventory' not in players[user_id]:
            players[user_id]['inventory'] = {}
        
        if item_id not in players[user_id]['inventory']:
            players[user_id]['inventory'][item_id] = 0
        
        players[user_id]['inventory'][item_id] += quantity
        self.save_players(players)
        
        item_data = items[item_id]
        embed = discord.Embed(
            title="🎁 Item Given",
            description=f"Admin {ctx.author.display_name} gave {quantity}x **{item_data['name']}** to {member.display_name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Item", value=item_data['description'], inline=True)
        embed.add_field(name="Quantity", value=quantity, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def setlevel(self, ctx, member: discord.Member, level: int):
        """Set a player's level (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        if level < 1 or level > 100:
            await ctx.send("Plagg: Level must be between 1 and 100!")
            return
        
        players = self.load_players()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        old_level = players[user_id]['level']
        players[user_id]['level'] = level
        players[user_id]['exp'] = 0
        players[user_id]['exp_to_next'] = 100
        
        self.save_players(players)
        
        embed = discord.Embed(
            title="📊 Level Set",
            description=f"Admin {ctx.author.display_name} set {member.display_name}'s level",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Old Level", value=old_level, inline=True)
        embed.add_field(name="New Level", value=level, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def setgold(self, ctx, member: discord.Member, amount: int):
        """Set a player's gold amount (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        if amount < 0:
            await ctx.send("Plagg: Gold amount cannot be negative!")
            return
        
        players = self.load_players()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        old_gold = players[user_id].get('gold', 0)
        players[user_id]['gold'] = amount
        
        self.save_players(players)
        
        embed = discord.Embed(
            title="💰 Gold Set",
            description=f"Admin {ctx.author.display_name} set {member.display_name}'s gold",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Old Gold", value=f"{old_gold} 🪙", inline=True)
        embed.add_field(name="New Gold", value=f"{amount} 🪙", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def reset(self, ctx, member: discord.Member):
        """Reset a player's character data (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        players = self.load_players()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        # Store old data for confirmation
        old_data = players[user_id].copy()
        
        # Remove player data
        del players[user_id]
        self.save_players(players)
        
        embed = discord.Embed(
            title="🔄 Character Reset",
            description=f"Admin {ctx.author.display_name} reset {member.display_name}'s character",
            color=discord.Color.red()
        )
        
        embed.add_field(name="Old Level", value=old_data.get('level', 1), inline=True)
        embed.add_field(name="Old Gold", value=f"{old_data.get('gold', 0)} 🪙", inline=True)
        embed.add_field(name="Old Class", value=old_data.get('class', 'Unknown'), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def heal(self, ctx, member: discord.Member):
        """Fully heal a player (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        players = self.load_players()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        old_hp = players[user_id]['hp']
        old_mp = players[user_id]['mp']
        
        players[user_id]['hp'] = players[user_id]['max_hp']
        players[user_id]['mp'] = players[user_id]['max_mp']
        
        self.save_players(players)
        
        embed = discord.Embed(
            title="💚 Player Healed",
            description=f"Admin {ctx.author.display_name} fully healed {member.display_name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="HP", value=f"{old_hp} → {players[user_id]['hp']}", inline=True)
        embed.add_field(name="MP", value=f"{old_mp} → {players[user_id]['mp']}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def playerinfo(self, ctx, member: discord.Member):
        """View detailed player information (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        players = self.load_players()
        user_id = str(member.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        player = players[user_id]
        
        embed = discord.Embed(
            title=f"📊 Admin View - {member.display_name}",
            description="Detailed player information",
            color=discord.Color.blue()
        )
        
        # Basic info
        embed.add_field(
            name="Character Info",
            value=f"**Class:** {player['class']}\n"
                  f"**Level:** {player['level']}\n"
                  f"**EXP:** {player['exp']}/{player['exp_to_next']}\n"
                  f"**Gold:** {player['gold']} 🪙",
            inline=True
        )
        
        # Stats
        embed.add_field(
            name="Stats",
            value=f"**HP:** {player['hp']}/{player['max_hp']}\n"
                  f"**MP:** {player['mp']}/{player['max_mp']}\n"
                  f"**Attack:** {player['attack']}\n"
                  f"**Defense:** {player['defense']}\n"
                  f"**Magic:** {player['magic']}\n"
                  f"**Speed:** {player['speed']}",
            inline=True
        )
        
        # Inventory
        inventory = player.get('inventory', {})
        if inventory:
            inv_text = ""
            for item_id, quantity in list(inventory.items())[:5]:  # Show first 5 items
                inv_text += f"• {item_id}: {quantity}\n"
            if len(inventory) > 5:
                inv_text += f"... and {len(inventory) - 5} more items"
        else:
            inv_text = "Empty"
        
        embed.add_field(name="Inventory", value=inv_text, inline=True)
        
        # Equipment
        equipment = player.get('equipment', {})
        equip_text = ""
        for slot, item in equipment.items():
            equip_text += f"**{slot.title()}:** {item or 'None'}\n"
        
        embed.add_field(name="Equipment", value=equip_text, inline=True)
        
        # Achievements
        achievements = player.get('achievements', [])
        embed.add_field(name="Achievements", value=f"{len(achievements)} earned", inline=True)
        
        # Created date
        created = player.get('created_at', 'Unknown')
        embed.add_field(name="Created", value=created, inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Admin view by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def serverstats(self, ctx):
        """View server-wide statistics (Admin only)."""
        if not await self.cog_check(ctx):
            await ctx.send("Plagg: You need administrator permissions to use this command!")
            return
        
        players = self.load_players()
        
        if not players:
            await ctx.send("Plagg: No players have started their adventure yet!")
            return
        
        # Calculate statistics
        total_players = len(players)
        total_level = sum(p.get('level', 1) for p in players.values())
        total_gold = sum(p.get('gold', 0) for p in players.values())
        avg_level = total_level / total_players if total_players > 0 else 0
        
        # Class distribution
        class_counts = {}
        for player in players.values():
            player_class = player.get('class', 'Unknown')
            class_counts[player_class] = class_counts.get(player_class, 0) + 1
        
        # Top players
        sorted_players = sorted(players.items(), key=lambda x: x[1].get('level', 1), reverse=True)
        top_players = sorted_players[:5]
        
        embed = discord.Embed(
            title="📊 Server Statistics",
            description=f"Statistics for {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="General Stats",
            value=f"**Total Players:** {total_players}\n"
                  f"**Average Level:** {avg_level:.1f}\n"
                  f"**Total Gold:** {total_gold:,} 🪙",
            inline=True
        )
        
        # Class distribution
        class_text = ""
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            class_text += f"**{class_name.title()}:** {count}\n"
        
        embed.add_field(name="Class Distribution", value=class_text, inline=True)
        
        # Top players
        top_text = ""
        for i, (user_id, player) in enumerate(top_players, 1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            level = player.get('level', 1)
            top_text += f"{i}. **{name}** - Level {level}\n"
        
        embed.add_field(name="Top Players", value=top_text, inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot)) 