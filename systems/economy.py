import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta

class Economy(commands.Cog):
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

    @commands.command()
    async def daily(self, ctx):
        """Claim your daily reward of gold and items."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first! Use `!startrpg <class>`")
            return
        
        player = players[user_id]
        
        # Check if player has claimed daily reward
        last_daily = player.get('last_daily')
        if last_daily:
            try:
                last_daily_date = datetime.fromisoformat(last_daily)
                now = datetime.now()
                
                # Check if it's been less than 24 hours
                if now - last_daily_date < timedelta(hours=24):
                    time_left = timedelta(hours=24) - (now - last_daily_date)
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    await ctx.send(f"Plagg: {ctx.author.mention}, you've already claimed your daily reward! Come back in {hours}h {minutes}m.")
                    return
            except:
                pass
        
        # Calculate daily reward based on level
        base_gold = 50
        level_bonus = player['level'] * 5
        total_gold = base_gold + level_bonus
        
        # Add streak bonus
        streak = player.get('daily_streak', 0)
        streak_bonus = min(streak * 10, 100)  # Max 100 gold bonus
        total_gold += streak_bonus
        
        # Update player data
        player['gold'] += total_gold
        player['last_daily'] = datetime.now().isoformat()
        player['daily_streak'] = streak + 1
        
        # Random item reward (higher chance for higher levels)
        item_reward = None
        if random.random() < 0.3 + (player['level'] * 0.02):  # 30% base + 2% per level
            items = self.load_items()
            common_items = [item_id for item_id, item_data in items.items() if item_data.get('rarity') == 'common']
            if common_items:
                item_reward = random.choice(common_items)
                if 'inventory' not in player:
                    player['inventory'] = {}
                if item_reward not in player['inventory']:
                    player['inventory'][item_reward] = 0
                player['inventory'][item_reward] += 1
        
        players[user_id] = player
        self.save_players(players)
        
        # Create reward embed
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"Here's your daily reward, {ctx.author.display_name}!",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Gold Reward", value=f"+{total_gold} 🪙", inline=True)
        embed.add_field(name="Daily Streak", value=f"{player['daily_streak']} days", inline=True)
        
        if item_reward:
            items = self.load_items()
            item_data = items[item_reward]
            embed.add_field(name="Bonus Item", value=f"**{item_data['name']}** - {item_data['description']}", inline=False)
        
        embed.add_field(
            name="Reward Breakdown",
            value=f"Base: {base_gold} 🪙\nLevel Bonus: +{level_bonus} 🪙\nStreak Bonus: +{streak_bonus} 🪙",
            inline=False
        )
        
        embed.set_footer(text="Come back tomorrow for more rewards!")
        await ctx.send(embed=embed)

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        """Check your or another player's gold balance."""
        players = self.load_players()
        user = member or ctx.author
        user_id = str(user.id)
        
        if user_id not in players:
            if user == ctx.author:
                await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            else:
                await ctx.send(f"Plagg: {user.mention} hasn't started their adventure yet!")
            return
        
        player = players[user_id]
        gold = player.get('gold', 0)
        
        embed = discord.Embed(
            title="💰 Gold Balance",
            description=f"{user.display_name}'s financial status",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="Current Gold", value=f"{gold:,} 🪙", inline=True)
        embed.add_field(name="Level", value=player.get('level', 1), inline=True)
        
        # Add some fun flavor text based on gold amount
        if gold < 100:
            flavor = "A bit short on cash, eh? Time to go adventuring!"
        elif gold < 500:
            flavor = "Not bad! You're building up your fortune."
        elif gold < 1000:
            flavor = "Well off! You're doing quite well for yourself."
        elif gold < 5000:
            flavor = "Rich! You're living the high life!"
        else:
            flavor = "Filthy rich! You're practically a dragon with all that gold!"
        
        embed.add_field(name="Status", value=flavor, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        """Give gold to another player."""
        if amount <= 0:
            await ctx.send(f"Plagg: {ctx.author.mention}, you can't give negative or zero gold!")
            return
        
        if member == ctx.author:
            await ctx.send(f"Plagg: {ctx.author.mention}, you can't give gold to yourself!")
            return
        
        players = self.load_players()
        giver_id = str(ctx.author.id)
        receiver_id = str(member.id)
        
        if giver_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        if receiver_id not in players:
            await ctx.send(f"Plagg: {member.mention} hasn't started their adventure yet!")
            return
        
        giver = players[giver_id]
        receiver = players[receiver_id]
        
        if giver.get('gold', 0) < amount:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough gold to give {amount}!")
            return
        
        # Transfer gold
        giver['gold'] -= amount
        receiver['gold'] += amount
        
        players[giver_id] = giver
        players[receiver_id] = receiver
        self.save_players(players)
        
        embed = discord.Embed(
            title="💰 Gold Transfer",
            description=f"{ctx.author.display_name} gave gold to {member.display_name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Amount", value=f"{amount:,} 🪙", inline=True)
        embed.add_field(name="New Balance", value=f"{giver['gold']:,} 🪙", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def gamble(self, ctx, amount: int):
        """Gamble your gold for a chance to win more!"""
        if amount <= 0:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to bet a positive amount!")
            return
        
        players = self.load_players()
        user_id = str(ctx.author.id)
        
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to start your adventure first!")
            return
        
        player = players[user_id]
        
        if player.get('gold', 0) < amount:
            await ctx.send(f"Plagg: {ctx.author.mention}, you don't have enough gold to gamble {amount}!")
            return
        
        # Gambling logic
        chance = random.random()
        
        if chance < 0.4:  # 40% chance to lose
            loss = amount
            player['gold'] -= loss
            result = "lost"
            color = discord.Color.red()
            message = f"Better luck next time! You lost {loss:,} 🪙"
        elif chance < 0.7:  # 30% chance to break even
            result = "broke even"
            color = discord.Color.blue()
            message = f"At least you didn't lose anything!"
        elif chance < 0.9:  # 20% chance to win 1.5x
            win = int(amount * 1.5)
            player['gold'] += win
            result = "won"
            color = discord.Color.green()
            message = f"Congratulations! You won {win:,} 🪙"
        else:  # 10% chance to win 3x
            win = int(amount * 3)
            player['gold'] += win
            result = "won big"
            color = discord.Color.gold()
            message = f"JACKPOT! You won {win:,} 🪙"
        
        players[user_id] = player
        self.save_players(players)
        
        embed = discord.Embed(
            title="🎰 Gambling Result",
            description=message,
            color=color
        )
        
        embed.add_field(name="Bet Amount", value=f"{amount:,} 🪙", inline=True)
        embed.add_field(name="Result", value=result.title(), inline=True)
        embed.add_field(name="New Balance", value=f"{player['gold']:,} 🪙", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx, category: str = "gold"):
        """View the leaderboard for gold, level, or achievements."""
        players = self.load_players()
        
        if not players:
            await ctx.send("Plagg: No players have started their adventure yet!")
            return
        
        category = category.lower()
        
        if category == "gold":
            sorted_players = sorted(players.items(), key=lambda x: x[1].get('gold', 0), reverse=True)
            title = "💰 Richest Players"
            value_func = lambda p: f"{p.get('gold', 0):,} 🪙"
        elif category == "level":
            sorted_players = sorted(players.items(), key=lambda x: x[1].get('level', 1), reverse=True)
            title = "📈 Highest Level Players"
            value_func = lambda p: f"Level {p.get('level', 1)}"
        elif category == "achievements":
            sorted_players = sorted(players.items(), key=lambda x: len(x[1].get('achievements', [])), reverse=True)
            title = "🏆 Most Achievements"
            value_func = lambda p: f"{len(p.get('achievements', []))} achievements"
        else:
            await ctx.send(f"Plagg: Invalid category! Use: gold, level, or achievements")
            return
        
        embed = discord.Embed(
            title=title,
            description=f"Top players in {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        for i, (user_id, player) in enumerate(sorted_players[:10], 1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            value = value_func(player)
            
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            embed.add_field(
                name=f"{medal} {name}",
                value=value,
                inline=False
            )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    def load_items(self):
        items_file = os.path.join("data", "items.json")
        try:
            with open(items_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

async def setup(bot):
    await bot.add_cog(Economy(bot)) 