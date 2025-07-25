import discord
from discord.ext import commands
import random
import json
import os
from ui.visual import format_hp_bar
from systems.progression import Progression

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), '../data/players.json')
CLASSES_FILE = os.path.join(os.path.dirname(__file__), '../data/classes.json')
SKILLS_FILE = os.path.join(os.path.dirname(__file__), '../data/skills.json')

class CombatView(discord.ui.View):
    def __init__(self, actions):
        super().__init__(timeout=30)
        self.value = None
        for action in actions:
            self.add_item(CombatButton(action))

class CombatButton(discord.ui.Button):
    def __init__(self, action):
        super().__init__(label=action, style=discord.ButtonStyle.primary)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.action
        for item in self.view.children:
            item.disabled = True
        await interaction.response.edit_message(content=f"You chose **{self.action}**!", view=self.view)
        self.view.stop()

class Combat(commands.Cog):
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

    def load_skills(self):
        with open(SKILLS_FILE, 'r') as f:
            return json.load(f)

    async def do_turn(self, ctx, attacker, defender, players, skills, is_pvp=False):
        actions = ["Attack"]
        # Add available skills
        for skill_id in players[attacker]["skills"]:
            if skill_id in skills:
                actions.append(skills[skill_id]["name"])
        view = CombatView(actions)
        msg = await ctx.send(f"{ctx.author.mention}, choose your action:", view=view)
        await view.wait()
        action = view.value or "Attack"
        if action == "Attack":
            dmg = random.randint(10, 20)
            players[defender]["hp"] = max(players[defender]["hp"] - dmg, 0)
            self.save_players(players)
            await msg.edit(content=f"Plagg: {ctx.author.mention} attacks for {dmg} damage!", view=None)
        else:
            # Skill logic (simple example)
            for skill_id, skill in skills.items():
                if skill["name"] == action:
                    power = skill["power"]
                    players[defender]["hp"] = max(players[defender]["hp"] - power, 0)
                    self.save_players(players)
                    await msg.edit(content=f"Plagg: {ctx.author.mention} uses {action} for {power} damage!", view=None)
                    break
        # Show HP bars
        hp_text = f"{format_hp_bar(players[attacker]["hp"], players[attacker]["max_hp"])}\nvs\n{format_hp_bar(players[defender]["hp"], players[defender]["max_hp"])}"
        await ctx.send(hp_text)

    @commands.command()
    async def fight(self, ctx, opponent: discord.Member = None):
        """Start a PvP or PvE fight."""
        players = self.load_players()
        skills = self.load_skills()
        user_id = str(ctx.author.id)
        if user_id not in players:
            await ctx.send(f"Plagg: {ctx.author.mention}, you need to register first with !startrpg!")
            return
        if opponent and opponent != ctx.author:
            opp_id = str(opponent.id)
            if opp_id not in players:
                await ctx.send(f"Plagg: {opponent.mention} needs to register first with !startrpg!")
                return
            await ctx.send(f"Plagg: {ctx.author.mention} challenges {opponent.mention} to a duel! 🐾")
            # PvP: Each takes a turn until one is at 0 HP
            turn = 0
            while players[user_id]["hp"] > 0 and players[opp_id]["hp"] > 0:
                if turn % 2 == 0:
                    await self.do_turn(ctx, user_id, opp_id, players, skills, is_pvp=True)
                else:
                    await self.do_turn(ctx, opp_id, user_id, players, skills, is_pvp=True)
                turn += 1
            winner = ctx.author if players[user_id]["hp"] > 0 else opponent
            await ctx.send(f"Plagg: {winner.mention} wins the duel!")
            # Award achievement for first win
            if players[str(winner.id)]["achievements"] == [] or "first_blood" not in players[str(winner.id)]["achievements"]:
                Progression.award_achievement(self, players, str(winner.id), "first_blood")
            # Optionally reset HP after battle
        else:
            await ctx.send(f"Plagg: {ctx.author.mention} is fighting a wild akuma! 🦋")
            # PvE: Fight a simple enemy
            enemy = {"name": "Wild Akuma", "hp": 50, "max_hp": 50}
            while players[user_id]["hp"] > 0 and enemy["hp"] > 0:
                # Player turn
                actions = ["Attack"]
                for skill_id in players[user_id]["skills"]:
                    if skill_id in skills:
                        actions.append(skills[skill_id]["name"])
                view = CombatView(actions)
                msg = await ctx.send(f"{ctx.author.mention}, choose your action:", view=view)
                await view.wait()
                action = view.value or "Attack"
                if action == "Attack":
                    dmg = random.randint(10, 20)
                    enemy["hp"] = max(enemy["hp"] - dmg, 0)
                    await msg.edit(content=f"Plagg: {ctx.author.mention} attacks for {dmg} damage!", view=None)
                else:
                    for skill_id, skill in skills.items():
                        if skill["name"] == action:
                            power = skill["power"]
                            enemy["hp"] = max(enemy["hp"] - power, 0)
                            await msg.edit(content=f"Plagg: {ctx.author.mention} uses {action} for {power} damage!", view=None)
                            break
                hp_text = f"{format_hp_bar(players[user_id]["hp"], players[user_id]["max_hp"])}\nvs\n{format_hp_bar(enemy["hp"], enemy["max_hp"])}"
                await ctx.send(hp_text)
                # Enemy turn
                if enemy["hp"] > 0:
                    dmg = random.randint(5, 15)
                    players[user_id]["hp"] = max(players[user_id]["hp"] - dmg, 0)
                    self.save_players(players)
                    await ctx.send(f"Plagg: The wild akuma attacks for {dmg} damage!")
                    hp_text = f"{format_hp_bar(players[user_id]["hp"], players[user_id]["max_hp"])}\nvs\n{format_hp_bar(enemy["hp"], enemy["max_hp"])}"
                    await ctx.send(hp_text)
            if players[user_id]["hp"] > 0:
                await ctx.send(f"Plagg: {ctx.author.mention} defeated the wild akuma!")
                # Award achievement for first win
                if players[user_id]["achievements"] == [] or "first_blood" not in players[user_id]["achievements"]:
                    Progression.award_achievement(self, players, user_id, "first_blood")
            else:
                await ctx.send(f"Plagg: {ctx.author.mention} was defeated by the wild akuma!")
            # Optionally reset HP after battle

async def setup(bot):
    await bot.add_cog(Combat(bot)) 