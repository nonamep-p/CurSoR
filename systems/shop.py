import discord
from discord.ext import commands
import json
import os
import random

class ShopView(discord.ui.View):
    def __init__(self, items, player_gold):
        super().__init__(timeout=60)
        self.items = items
        self.player_gold = player_gold
        self.selected_item = None

class ShopButton(discord.ui.Button):
    def __init__(self, item_id, item_data, player_gold):
        super().__init__(label=f"Buy {item_data['name']} ({item_data['price']}g)", style=discord.ButtonStyle.primary)
        self.item_id = item_id
        self.item_data = item_data
        self.player_gold = player_gold

    async def callback(self, interaction: discord.Interaction):
        if self.player_gold >= self.item_data['price']:
            self.view.selected_item = self.item_id
            await interaction.response.send_message(f"You selected **{self.item_data['name']}** for {self.item_data['price']} gold!", ephemeral=True)
        else:
            await interaction.response.send_message(f"You don't have enough gold! You need {self.item_data['price']} gold but have {self.player_gold}.", ephemeral=True)

class Shop(commands.Cog):
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

    @commands.command()
    async def shop(self, ctx, category: str = None):
        """Browse the shop by category: weapons, armor, consumables, materials, accessories, all"""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first! Use `!startrpg <class>`")
            return
        
        player = players[user_id]
        player_gold = player.get("gold", 0)
        
        # Filter items by category
        if category and category.lower() != "all":
            category = category.lower()
            filtered_items = {}
            for item_id, item_data in items.items():
                if item_data.get("type") == category:
                    filtered_items[item_id] = item_data
            items = filtered_items
        
        if not items:
            await ctx.send(f"Plagg: {ctx.author.mention}, no items found in that category!")
            return
        
        # Create shop embed
        embed = discord.Embed(
            title="🏪 Plagg's Shop",
            description=f"Welcome to the shop! You have **{player_gold}** gold.\nUse `!buy <item_name>` to purchase items.",
            color=discord.Color.gold()
        )
        
        # Group items by rarity
        rarity_colors = {
            "common": discord.Color.light_grey(),
            "uncommon": discord.Color.green(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.orange()
        }
        
        rarity_emojis = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟠"
        }
        
        for rarity in ["common", "uncommon", "rare", "epic", "legendary"]:
            rarity_items = {k: v for k, v in items.items() if v.get("rarity") == rarity}
            if rarity_items:
                items_text = ""
                for item_id, item_data in rarity_items.items():
                    emoji = rarity_emojis.get(rarity, "⚪")
                    items_text += f"{emoji} **{item_data['name']}** - {item_data['price']}g\n"
                    items_text += f"   {item_data['description']}\n\n"
                
                embed.add_field(
                    name=f"{rarity.title()} Items",
                    value=items_text[:1024] if len(items_text) > 1024 else items_text,
                    inline=False
                )
        
        embed.set_footer(text=f"Use !buy <item_name> to purchase | !shop <category> to filter")
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, item_name: str = None, quantity: int = 1):
        """Buy an item from the shop."""
        if not item_name:
            await ctx.send(f"Plagg: {ctx.author.mention}, specify an item to buy! Use `!shop` to see available items.")
            return
        
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        player = players[user_id]
        player_gold = player.get("gold", 0)
        
        # Find item by name (case insensitive)
        item_id = None
        for iid, item_data in items.items():
            if item_data['name'].lower() == item_name.lower():
                item_id = iid
                break
        
        if not item_id:
            await ctx.send(f"Plagg: {ctx.author.mention}, that item doesn't exist! Use `!shop` to see available items.")
            return
        
        item_data = items[item_id]
        total_cost = item_data['price'] * quantity
        
        if player_gold < total_cost:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough gold! You need {total_cost} gold but have {player_gold}.")
            return
        
        # Process purchase
        player['gold'] -= total_cost
        
        # Add item to inventory
        if 'inventory' not in player:
            player['inventory'] = {}
        
        if item_id not in player['inventory']:
            player['inventory'][item_id] = 0
        
        player['inventory'][item_id] += quantity
        
        players[user_id] = player
        self.save_players(players)
        
        # Create purchase embed
        embed = discord.Embed(
            title="🛒 Purchase Successful!",
            description=f"You bought {quantity}x **{item_data['name']}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Item Details", value=item_data['description'], inline=False)
        embed.add_field(name="Cost", value=f"{total_cost} gold", inline=True)
        embed.add_field(name="Remaining Gold", value=f"{player['gold']} gold", inline=True)
        
        # Add rarity indicator
        rarity_emojis = {
            "common": "⚪",
            "uncommon": "🟢",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟠"
        }
        rarity_emoji = rarity_emojis.get(item_data.get("rarity", "common"), "⚪")
        embed.add_field(name="Rarity", value=f"{rarity_emoji} {item_data.get('rarity', 'common').title()}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def sell(self, ctx, item_name: str = None, quantity: int = 1):
        """Sell an item from your inventory."""
        if not item_name:
            await ctx.send(f"Plagg: {ctx.author.mention}, specify an item to sell! Use `!inventory` to see your items.")
            return
        
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        player = players[user_id]
        player_inventory = player.get("inventory", {})
        
        # Find item by name (case insensitive)
        item_id = None
        for iid, item_data in items.items():
            if item_data['name'].lower() == item_name.lower():
                item_id = iid
                break
        
        if not item_id:
            await ctx.send(f"Plagg: {ctx.author.mention}, that item doesn't exist!")
            return
        
        if item_id not in player_inventory or player_inventory[item_id] < quantity:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough {items[item_id]['name']} to sell!")
            return
        
        item_data = items[item_id]
        sell_price = int(item_data['price'] * 0.5)  # Sell for 50% of original price
        total_earnings = sell_price * quantity
        
        # Process sale
        player['gold'] += total_earnings
        player_inventory[item_id] -= quantity
        
        if player_inventory[item_id] <= 0:
            del player_inventory[item_id]
        
        player['inventory'] = player_inventory
        players[user_id] = player
        self.save_players(players)
        
        embed = discord.Embed(
            title="💰 Sale Successful!",
            description=f"You sold {quantity}x **{item_data['name']}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Earnings", value=f"{total_earnings} gold", inline=True)
        embed.add_field(name="New Gold Total", value=f"{player['gold']} gold", inline=True)
        embed.add_field(name="Remaining Items", value=f"{player_inventory.get(item_id, 0)}x {item_data['name']}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def price(self, ctx, item_name: str = None):
        """Check the price of an item."""
        if not item_name:
            await ctx.send(f"Plagg: {ctx.author.mention}, specify an item to check!")
            return
        
        items = self.load_items()
        
        # Find item by name (case insensitive)
        item_id = None
        for iid, item_data in items.items():
            if item_data['name'].lower() == item_name.lower():
                item_id = iid
                break
        
        if not item_id:
            await ctx.send(f"Plagg: {ctx.author.mention}, that item doesn't exist!")
            return
        
        item_data = items[item_id]
        sell_price = int(item_data['price'] * 0.5)
        
        embed = discord.Embed(
            title=f"💰 {item_data['name']} - Price Information",
            description=item_data['description'],
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Buy Price", value=f"{item_data['price']} gold", inline=True)
        embed.add_field(name="Sell Price", value=f"{sell_price} gold", inline=True)
        embed.add_field(name="Rarity", value=item_data.get("rarity", "common").title(), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def dailydeals(self, ctx):
        """View today's special deals and discounts."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        player = players[user_id]
        player_gold = player.get("gold", 0)
        
        # Generate daily deals (random selection with discounts)
        all_items = list(items.items())
        daily_items = random.sample(all_items, min(5, len(all_items)))
        
        embed = discord.Embed(
            title="🎯 Daily Deals",
            description=f"Special offers for today! You have **{player_gold}** gold.",
            color=discord.Color.red()
        )
        
        for item_id, item_data in daily_items:
            discount = random.randint(10, 50)  # 10-50% discount
            original_price = item_data['price']
            discounted_price = int(original_price * (1 - discount / 100))
            
            embed.add_field(
                name=f"🔥 {item_data['name']} - {discount}% OFF!",
                value=f"~~{original_price}g~~ **{discounted_price}g**\n"
                      f"{item_data['description']}\n"
                      f"Use: `!buy {item_data['name']}`",
                inline=False
            )
        
        embed.set_footer(text="Deals change daily! Check back tomorrow for new offers.")
        await ctx.send(embed=embed)

    @commands.command()
    async def shopcategories(self, ctx):
        """Show available shop categories."""
        embed = discord.Embed(
            title="🏪 Shop Categories",
            description="Browse items by category:",
            color=discord.Color.blue()
        )
        
        categories = {
            "weapons": "⚔️ Swords, staves, daggers, and other weapons",
            "armor": "🛡️ Armor pieces for protection",
            "consumables": "🧪 Potions, food, and other consumable items",
            "materials": "📦 Crafting materials and resources",
            "accessories": "💍 Rings, amulets, and other accessories",
            "all": "📋 Show all items"
        }
        
        for category, description in categories.items():
            embed.add_field(
                name=f"!shop {category}",
                value=description,
                inline=False
            )
        
        embed.set_footer(text="Use !shop <category> to browse items")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shop(bot)) 