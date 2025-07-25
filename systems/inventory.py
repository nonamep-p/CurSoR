from discord.ext import commands
import discord
import json
import os
from ui.inventory_render import render_inventory
from systems.progression import Progression

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), '../data/players.json')
ITEMS_FILE = os.path.join(os.path.dirname(__file__), '../data/items.json')

PLAGG_COMMENTS = {
    "cheese": "Mmm, cheese! The only item that matters! 🧀",
    "miraculous_ring": "Careful, that's powerful stuff!"
}

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_players(self):
        with open(PLAYERS_FILE, 'r') as f:
            return json.load(f)

    def save_players(self, players):
        with open(PLAYERS_FILE, 'w') as f:
            json.dump(players, f, indent=2)

    def load_items(self):
        with open(ITEMS_FILE, 'r') as f:
            return json.load(f)

    def ensure_gold(self, player):
        if "gold" not in player:
            player["gold"] = 50

    RECIPES = {
        "enchanted_cheese": {"cheese": 2, "magic_dust": 1}
    }

    @commands.command()
    async def inventory(self, ctx, member: discord.Member = None):
        """View your or another player's inventory."""
        players = self.load_players()
        items = self.load_items()
        target = member or ctx.author
        user_id = str(target.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {target.mention} doesn't have a profile yet. Use !startrpg to start!")
            return
        self.ensure_gold(players[user_id])
        inv = players[user_id].get("inventory", {})
        if not inv:
            await ctx.send(f"Plagg: {target.mention} has an empty inventory. Time to get some cheese!")
            return
        text = render_inventory(inv, items)
        await ctx.send(f"**{target.display_name}'s Inventory:**\n{text}\nGold: {players[user_id]['gold']}")

    @commands.command()
    async def shop(self, ctx):
        """List items available in the shop."""
        items = self.load_items()
        lines = [f"**{item['name']}** ({item_id}): {item['description']} - {item['price']} gold" for item_id, item in items.items()]
        await ctx.send("**Shop Items:**\n" + "\n".join(lines))

    @commands.command()
    async def buy(self, ctx, item: str, qty: int = 1):
        """Buy an item from the shop."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        self.ensure_gold(players[user_id])
        if item not in items:
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a real item!")
            return
        price = items[item]["price"] * qty
        if players[user_id]["gold"] < price:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough gold!")
            return
        inv = players[user_id].setdefault("inventory", {})
        inv[item] = inv.get(item, 0) + qty
        players[user_id]["gold"] -= price
        self.save_players(players)
        comment = PLAGG_COMMENTS.get(item, "Nice buy!")
        await ctx.send(f"Plagg: {ctx.author.mention} bought {qty} {items[item]['name']}(s) for {price} gold. {comment}")

    @commands.command()
    async def sell(self, ctx, item: str, qty: int = 1):
        """Sell an item from your inventory."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        self.ensure_gold(players[user_id])
        inv = players[user_id].get("inventory", {})
        if item not in inv or inv[item] < qty:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough {item}!")
            return
        if item not in items:
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a real item!")
            return
        sell_price = max(1, items[item]["price"] // 2) * qty
        inv[item] -= qty
        if inv[item] == 0:
            del inv[item]
        players[user_id]["gold"] += sell_price
        self.save_players(players)
        comment = PLAGG_COMMENTS.get(item, "Easy money!")
        await ctx.send(f"Plagg: {ctx.author.mention} sold {qty} {items[item]['name']}(s) for {sell_price} gold. {comment}")

    @commands.command()
    async def useitem(self, ctx, item: str):
        """Use an item from your inventory."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        self.ensure_gold(players[user_id])
        inv = players[user_id].get("inventory", {})
        if item not in inv or inv[item] <= 0:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have any {item}!")
            return
        item_data = items.get(item)
        if not item_data:
            await ctx.send(f"Plagg: {ctx.author.mention}, I don't even know what that is!")
            return
        # Example: Cheese restores HP
        if item_data["type"] == "consumable":
            effect = item_data.get("effect", {})
            hp_restore = effect.get("hp", 0)
            players[user_id]["hp"] = min(players[user_id]["hp"] + hp_restore, players[user_id]["max_hp"])
            inv[item] -= 1
            if inv[item] == 0:
                del inv[item]
            # Cheese Lover achievement
            if item == "cheese":
                cheese_eaten = players[user_id].get("cheese_eaten", 0) + 1
                players[user_id]["cheese_eaten"] = cheese_eaten
                if cheese_eaten >= 10:
                    Progression.award_achievement(self, players, user_id, "cheese_lover")
            self.save_players(players)
            comment = PLAGG_COMMENTS.get(item, "Yum!")
            await ctx.send(f"Plagg: {ctx.author.mention} used {item_data['name']} and restored {hp_restore} HP! {comment}")
        else:
            await ctx.send(f"Plagg: {ctx.author.mention}, you can't use that item directly!")

    @commands.command()
    async def giveitem(self, ctx, member: discord.Member, item: str, qty: int = 1):
        """Give an item to another player."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        target_id = str(member.id)
        if user_id not in players or target_id not in players:
            await ctx.send(f"Plagg: Both players must be registered!")
            return
        self.ensure_gold(players[user_id])
        self.ensure_gold(players[target_id])
        inv = players[user_id].get("inventory", {})
        if item not in inv or inv[item] < qty:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough {item}!")
            return
        if item not in items:
            await ctx.send(f"Plagg: {ctx.author.mention}, that's not a real item!")
            return
        # Remove from sender
        inv[item] -= qty
        if inv[item] == 0:
            del inv[item]
        # Add to receiver
        target_inv = players[target_id].setdefault("inventory", {})
        target_inv[item] = target_inv.get(item, 0) + qty
        self.save_players(players)
        comment = PLAGG_COMMENTS.get(item, "Share the cheese!")
        await ctx.send(f"Plagg: {ctx.author.mention} gave {qty} {item}(s) to {member.mention}. {comment}")

    @commands.command()
    async def craft(self, ctx, item: str):
        """Craft an item if you have the required materials."""
        players = self.load_players()
        items = self.load_items()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        self.ensure_gold(players[user_id])
        if item not in self.RECIPES:
            await ctx.send(f"Plagg: {ctx.author.mention}, you can't craft that!")
            return
        recipe = self.RECIPES[item]
        inv = players[user_id].setdefault("inventory", {})
        # Check materials
        for mat, amt in recipe.items():
            if inv.get(mat, 0) < amt:
                await ctx.send(f"Plagg: {ctx.author.mention}, you need {amt}x {mat} to craft {item}!")
                return
        # Remove materials
        for mat, amt in recipe.items():
            inv[mat] -= amt
            if inv[mat] == 0:
                del inv[mat]
        # Add crafted item
        inv[item] = inv.get(item, 0) + 1
        self.save_players(players)
        await ctx.send(f"Plagg: {ctx.author.mention} crafted 1 {items[item]['name']}! Now that's some magical cheese!")

async def setup(bot):
    await bot.add_cog(Inventory(bot)) 