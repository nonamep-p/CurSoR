from discord.ext import commands
import discord
import json
import os
from ui.embeds import player_profile_embed

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), '../data/players.json')
CLASSES_FILE = os.path.join(os.path.dirname(__file__), '../data/classes.json')
ACHIEVEMENTS_FILE = os.path.join(os.path.dirname(__file__), '../data/achievements.json')
TITLES_FILE = os.path.join(os.path.dirname(__file__), '../data/titles.json')

class ClassSelectView(discord.ui.View):
    def __init__(self, classes):
        super().__init__(timeout=60)
        self.value = None
        for class_id, class_data in classes.items():
            self.add_item(ClassButton(class_id, class_data))

class ClassButton(discord.ui.Button):
    def __init__(self, class_id, class_data):
        super().__init__(label=class_data['name'], style=discord.ButtonStyle.primary)
        self.class_id = class_id
        self.class_data = class_data

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.class_id
        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(content=f"You chose **{self.class_data['name']}**!", view=self.view)
        self.view.stop()

class Progression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_players(self):
        with open(PLAYERS_FILE, 'r') as f:
            return json.load(f)

    def save_players(self, players):
        with open(PLAYERS_FILE, 'w') as f:
            json.dump(players, f, indent=2)

    def load_classes(self):
        with open(CLASSES_FILE, 'r') as f:
            return json.load(f)

    def load_achievements(self):
        with open(ACHIEVEMENTS_FILE, 'r') as f:
            return json.load(f)

    def load_titles(self):
        with open(TITLES_FILE, 'r') as f:
            return json.load(f)

    @commands.command()
    async def startrpg(self, ctx):
        """Register as a new player."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        if user_id in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you already have a profile! Use !profile to view it.")
            return
        # Default player data
        player = {
            "name": ctx.author.display_name,
            "class": "Unassigned",
            "level": 1,
            "xp": 0,
            "hp": 100,
            "max_hp": 100,
            "inventory": {},
            "skills": [],
        }
        players[user_id] = player
        self.save_players(players)
        await ctx.send(f"Plagg: Welcome, {ctx.author.mention}! Your journey begins. Use !profile to view your stats.")

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        """View your or another player's profile."""
        players = self.load_players()
        target = member or ctx.author
        user_id = str(target.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {target.mention} doesn't have a profile yet. Use !startrpg to start!")
            return
        embed = player_profile_embed(players[user_id])
        await ctx.send(embed=embed)

    @commands.command()
    async def chooseclass(self, ctx):
        """Choose your class (one-time only)."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        if players[user_id]["class"] != "Unassigned":
            await ctx.send(f"Plagg: {ctx.author.mention}, you've already chosen a class!")
            return
        classes = self.load_classes()
        view = ClassSelectView(classes)
        msg = await ctx.send(f"{ctx.author.mention}, choose your class:", view=view)
        await view.wait()
        chosen = view.value
        if not chosen:
            await msg.edit(content="Class selection timed out.", view=None)
            return
        class_data = classes[chosen]
        players[user_id]["class"] = class_data["name"]
        players[user_id]["hp"] = class_data["base_stats"]["hp"]
        players[user_id]["max_hp"] = class_data["base_stats"]["hp"]
        # Optionally add other base stats
        self.save_players(players)
        await msg.edit(content=f"Plagg: {ctx.author.mention} is now a **{class_data['name']}**!", view=None)

    @commands.command()
    async def achievements(self, ctx, member: discord.Member = None):
        """View your or another player's achievements."""
        players = self.load_players()
        achievements = self.load_achievements()
        target = member or ctx.author
        user_id = str(target.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {target.mention} doesn't have a profile yet. Use !startrpg to start!")
            return
        unlocked = players[user_id].get("achievements", [])
        if not unlocked:
            await ctx.send(f"Plagg: {target.mention} has no achievements yet.")
            return
        lines = [f"🏆 {achievements[aid]['name']}: {achievements[aid]['description']}" for aid in unlocked if aid in achievements]
        await ctx.send(f"**{target.display_name}'s Achievements:**\n" + "\n".join(lines))

    @commands.command()
    async def titles(self, ctx, member: discord.Member = None):
        """View your or another player's unlocked titles."""
        players = self.load_players()
        titles = self.load_titles()
        target = member or ctx.author
        user_id = str(target.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {target.mention} doesn't have a profile yet. Use !startrpg to start!")
            return
        unlocked = players[user_id].get("titles", [])
        if not unlocked:
            await ctx.send(f"Plagg: {target.mention} has no titles yet.")
            return
        lines = [f"🎖️ {titles[tid]['name']}: {titles[tid]['description']}" for tid in unlocked if tid in titles]
        await ctx.send(f"**{target.display_name}'s Titles:**\n" + "\n".join(lines))

    @commands.command()
    async def settitle(self, ctx, title_id: str):
        """Set your active title."""
        players = self.load_players()
        titles = self.load_titles()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        if title_id not in players[user_id].get("titles", []):
            await ctx.send(f"Plagg: {ctx.author.mention}, you haven't unlocked that title!")
            return
        players[user_id]["active_title"] = title_id
        self.save_players(players)
        await ctx.send(f"Plagg: {ctx.author.mention} equipped the title: {titles[title_id]['name']}!")

    @commands.command()
    async def prestige(self, ctx):
        """Reset your level to 1 and gain a prestige point."""
        players = self.load_players()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        player = players[user_id]
        if player.get("level", 1) < 50:
            await ctx.send(f"Plagg: {ctx.author.mention}, you must reach level 50 to prestige!")
            return
        player["level"] = 1
        player["xp"] = 0
        player["prestige"] = player.get("prestige", 0) + 1
        self.save_players(players)
        await ctx.send(f"Plagg: {ctx.author.mention} has prestiged! Total prestige: {player['prestige']}")

    def award_achievement(self, players, user_id, achievement_id):
        if "achievements" not in players[user_id]:
            players[user_id]["achievements"] = []
        if achievement_id not in players[user_id]["achievements"]:
            players[user_id]["achievements"].append(achievement_id)
            self.save_players(players)
            # Award title if achievement matches a title requirement
            titles = self.load_titles()
            for tid, tdata in titles.items():
                if tdata.get("requirement") == achievement_id:
                    self.award_title(players, user_id, tid)

    def award_title(self, players, user_id, title_id):
        if "titles" not in players[user_id]:
            players[user_id]["titles"] = []
        if title_id not in players[user_id]["titles"]:
            players[user_id]["titles"].append(title_id)
            self.save_players(players)

async def setup(bot):
    await bot.add_cog(Progression(bot)) 