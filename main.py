import discord
from discord.ext import commands
import json
import random
import asyncio
import os
from datetime import datetime, timedelta
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Update file paths to use root directory
PLAYERS_FILE = "players.json"
CLASSES_FILE = "classes.json"
ITEMS_FILE = "items.json"
SKILLS_FILE = "skills.json"
DUNGEONS_FILE = "dungeons.json"

# Player data system

def load_player_data(user_id):
    # DEFAULT PLAYER TEMPLATE - CREATE EXACTLY THIS STRUCTURE
    default_player = {
        "id": str(user_id),
        "username": "Unknown",
        "level": 1,
        "xp": 0,
        "xp_required": 100,
        "gold": 50,
        "class": "novice",
        "stats": {
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "str": 10,
            "int": 10,
            "agi": 10,
            "luk": 10,
            "spd": 10,
            "def": 5,
            "res": 5
        },
        "combat_stats": {
            "crit_rate": 5,
            "crit_dmg": 150,
            "accuracy": 90,
            "dodge": 5,
            "block": 10
        },
        "skills": {},
        "inventory": [],
        "equipment": {
            "weapon": None,
            "armor": None,
            "accessory": None
        },
        "status_effects": [],
        "achievements": [],
        "quests": [],
        "created_at": str(datetime.now())
    }
    return default_player

def save_player_data(user_id, player_data):
    # VALIDATE ALL REQUIRED FIELDS EXIST
    required_fields = ["id", "username", "level", "xp", "xp_required", "gold", "class"]
    for field in required_fields:
        if field not in player_data:
            player_data[field] = load_player_data(user_id)[field]

    # ENSURE ALL STAT FIELDS EXIST
    stat_fields = ["hp", "max_hp", "mp", "max_mp", "str", "int", "agi", "luk", "spd", "def", "res"]
    if "stats" not in player_data:
        player_data["stats"] = {}
    for field in stat_fields:
        if field not in player_data["stats"]:
            player_data["stats"][field] = load_player_data(user_id)["stats"][field]

    # ENSURE ALL COMBAT STAT FIELDS EXIST
    combat_fields = ["crit_rate", "crit_dmg", "accuracy", "dodge", "block"]
    if "combat_stats" not in player_data:
        player_data["combat_stats"] = {}
    for field in combat_fields:
        if field not in player_data["combat_stats"]:
            player_data["combat_stats"][field] = load_player_data(user_id)["combat_stats"][field]

    # SAVE TO JSON FILE (SIMULATING PROFILE STORAGE)
    try:
        with open(PLAYERS_FILE, "r") as f:
            all_players = json.load(f)
    except FileNotFoundError:
        all_players = {}

    all_players[str(user_id)] = player_data

    with open(PLAYERS_FILE, "w") as f:
        json.dump(all_players, f, indent=2)

# ADD THIS FUNCTION TO HANDLE STEALTH - COPY EXACTLY
def apply_stealth(player_data):
    """Apply stealth status to player - makes them invisible in combat"""
    # CHECK IF PLAYER ALREADY HAS STEALTH
    stealth_effect = None
    for effect in player_data.get("status_effects", []):
        if effect.get("name") == "STEALTH":
            stealth_effect = effect
            break

    # IF NO STEALTH, ADD IT
    if not stealth_effect:
        stealth_status = {
            "name": "STEALTH",
            "duration": 3,  # 3 TURNS MAXIMUM
            "effects": {
                "dodge": 90,        # 90% DODGE CHANCE
                "invisible": True,   # CANNOT BE TARGETED
                "enemy_accuracy_reduction": 30  # ENEMIES MISS MORE
            },
            "visual_indicator": "👻 INVISIBLE"
        }
        if "status_effects" not in player_data:
            player_data["status_effects"] = []
        player_data["status_effects"].append(stealth_status)
        return True, "You fade into the shadows...  ghostlike silence envelops you"
    else:
        return False, "You're already in stealth mode!"

# ADD AMBUSH MECHANIC CHECKER
def check_ambush(player_data, target_data):
    """Check if player gets ambush bonus (first attack from stealth)"""
    # LOOK FOR STEALTH STATUS
    stealth_active = False
    for effect in player_data.get("status_effects", []):
        if effect.get("name") == "STEALTH":
            stealth_active = True
            break

    # IF STEALTH ACTIVE, APPLY AMBUSH
    if stealth_active:
        # REMOVE STEALTH AFTER AMBUSH
        player_data["status_effects"] = [
            effect for effect in player_data.get("status_effects", [])
            if effect.get("name") != "STEALTH"
        ]
        return True, 2.5  # 2.5x DAMAGE MULTIPLIER
    return False, 1.0  # NORMAL DAMAGE

# ADD THIS TO DAMAGE CALCULATION
def calculate_damage_with_ambush(attacker, defender, base_damage):
    """Calculate damage with ambush bonus if applicable"""
    is_ambush, ambush_multiplier = check_ambush(attacker, defender)
    if is_ambush:
        final_damage = base_damage * ambush_multiplier
        # ADD VISUAL FEEDBACK
        print("🎯 AMBUSH! Critical strike from the shadows!")  # WILL BE REPLACED WITH DISCORD MESSAGE
        return final_damage, True
    return base_damage, False

# ADD THIS FUNCTION TO HANDLE BLOCK STACKS - COPY EXACTLY
def add_block_stack(player_data):
    """Add BLOCK stack to warrior player"""
    # CHECK PLAYER CLASS
    if player_data.get("class") != "warrior":
        return False, "Only warriors can gain BLOCK stacks"

    # FIND EXISTING BLOCK STACKS
    block_stacks = 0
    for effect in player_data.get("status_effects", []):
        if effect.get("name") == "BLOCK_STACK":
            block_stacks = effect.get("stacks", 0)
            break

    # ADD STACK IF BELOW MAX
    if block_stacks < 3:  # MAX 3 STACKS
        # REMOVE EXISTING BLOCK STACK EFFECT
        player_data["status_effects"] = [
            effect for effect in player_data.get("status_effects", [])
            if effect.get("name") != "BLOCK_STACK"
        ]

        # ADD UPDATED BLOCK STACKS
        block_effect = {
            "name": "BLOCK_STACK",
            "stacks": block_stacks + 1,
            "effects": {
                "damage_reduction": 50 * (block_stacks + 1),  # 50% PER STACK
                "counter_chance": 20 * (block_stacks + 1)     # COUNTER CHANCE
            },
            "visual_indicator": f"🛡️ BLOCK (+{block_stacks + 1})"
        }
        player_data["status_effects"].append(block_effect)
        return True, f"BLOCK stack gained! You now have {block_stacks + 1} stacks"
    else:
        return False, "Maximum BLOCK stacks reached (3)"

# ADD THIS TO DAMAGE REDUCTION LOGIC
def apply_block_reduction(damage, player_data):
    """Apply damage reduction from BLOCK stacks"""
    block_stacks = 0
    for effect in player_data.get("status_effects", []):
        if effect.get("name") == "BLOCK_STACK":
            block_stacks = effect.get("stacks", 0)
            break

    if block_stacks > 0:
        reduction = 0.5 * block_stacks  # 50% REDUCTION PER STACK
        reduced_damage = damage * (1 - reduction)
        # CONSUME ALL BLOCK STACKS AFTER USE
        player_data["status_effects"] = [
            effect for effect in player_data.get("status_effects", [])
            if effect.get("name") != "BLOCK_STACK"
        ]
        return max(1, reduced_damage), f"🛡️ BLOCK! Damage reduced by {int(reduction * 100)}%"
    return damage, None

# ADD SHIELD SLAM SKILL THAT CONSUMES BLOCK STACKS
def shield_slam_damage(player_data, target_data, base_power=80):
    """Special warrior skill that consumes BLOCK stacks for bonus damage"""
    # COUNT BLOCK STACKS
    block_stacks = 0
    for effect in player_data.get("status_effects", []):
        if effect.get("name") == "BLOCK_STACK":
            block_stacks = effect.get("stacks", 0)
            break

    if block_stacks > 0:
        # CONSUME BLOCK STACKS
        player_data["status_effects"] = [
            effect for effect in player_data.get("status_effects", [])
            if effect.get("name") != "BLOCK_STACK"
        ]

        # CALCULATE BONUS DAMAGE
        bonus_damage = base_power * (0.5 * block_stacks)  # 50% BONUS PER STACK
        total_damage = base_power + bonus_damage

        return total_damage, f"🛡️ Shield Slam! {block_stacks} BLOCK stacks consumed for +{int(bonus_damage)} bonus damage!"
    else:
        return base_power, "🛡️ Shield Slam! (No BLOCK stacks to enhance)"

# ADD THIS COMBAT TURN FUNCTION
def process_combat_turn(attacker_data, defender_data, action_type="attack"):
    """Process one combat turn with all mechanics applied"""

    # STEP 1: CHECK STEALTH STATE
    stealth_message = ""
    if action_type == "attack":
        is_ambush, ambush_mult = check_ambush(attacker_data, defender_data)
        if is_ambush:
            stealth_message = "🎯 AMBUSH! "

    # STEP 2: CALCULATE BASE DAMAGE
    str_bonus = attacker_data["stats"]["str"] * 2
    base_damage = 20 + str_bonus  # BASE ATTACK POWER

    # STEP 3: APPLY AMBUSH BONUS
    if stealth_message:
        base_damage = int(base_damage * 2.5)

    # STEP 4: APPLY WARRIOR SHIELD SLAM IF USED
    if action_type == "skill" and attacker_data.get("class") == "warrior":
        base_damage, skill_message = shield_slam_damage(attacker_data, defender_data)
        stealth_message = skill_message

    # STEP 5: APPLY BLOCK REDUCTION IF DEFENDER IS WARRIOR
    final_damage, block_message = apply_block_reduction(base_damage, defender_data)

    # STEP 6: UPDATE DEFENDER HP
    defender_data["stats"]["hp"] = max(0, defender_data["stats"]["hp"] - final_damage)

    # STEP 7: GENERATE RESULT MESSAGE
    hp_left = defender_data["stats"]["hp"]
    result_message = f"{stealth_message}Hit for {final_damage} damage! {hp_left} HP remaining"
    if block_message:
        result_message += f"\n{block_message}"

    return result_message, defender_data["stats"]["hp"] <= 0

# ADD THIS TO RANDOMLY GIVE BLOCK STACKS TO WARRIORS
def combat_round_end(player_data):
    """Called at end of each combat round to apply passive effects"""
    # WARRIOR BLOCK STACK CHANCE
    if player_data.get("class") == "warrior":
        if random.randint(1, 100) <= 50:  # 50% CHANCE
            success, message = add_block_stack(player_data)
            return message
    return None

# SKILL TREE SYSTEM

def load_skills_data():
    with open(SKILLS_FILE, "r") as f:
        return json.load(f)

def get_player_skills(player_data):
    return player_data.get("skills", {})

def can_unlock_skill(player_data, class_name, skill_id, skills_data):
    # Check if already unlocked
    if skill_id in get_player_skills(player_data):
        return False, "Skill already unlocked."
    # Check if player has enough skill points
    skill_tree = skills_data[class_name]["tree"]
    skill = skill_tree[skill_id]
    if player_data.get("skill_points", 0) < skill["cost"]:
        return False, "Not enough skill points."
    # Check requirements
    for req in skill["requirements"]:
        if req not in get_player_skills(player_data):
            return False, f"Missing prerequisite: {req}"
    return True, ""

def unlock_skill(player_data, class_name, skill_id, skills_data):
    skill_tree = skills_data[class_name]["tree"]
    skill = skill_tree[skill_id]
    player_data["skills"][skill_id] = True
    player_data["skill_points"] = player_data.get("skill_points", 0) - skill["cost"]
    return skill["name"], skill["description"]

# SKILL EFFECT INTEGRATION

def apply_passive_skills(player_data, class_name, skills_data):
    """Apply passive skill effects to player stats at battle start."""
    skills = player_data.get("skills", {})
    tree = skills_data[class_name]["tree"]
    # Example: Iron Will (warrior)
    if "iron_will" in skills:
        player_data["stats"]["max_hp"] = int(player_data["stats"]["max_hp"] * 1.2)
        player_data["stats"]["hp"] = player_data["stats"]["max_hp"]
    # Add more passive effects as needed
    return player_data

def get_active_skills(player_data, class_name, skills_data):
    """Return a list of unlocked active skills for the player."""
    skills = player_data.get("skills", {})
    tree = skills_data[class_name]["tree"]
    # For now, treat all skills except Iron Will as active
    return [sid for sid in skills if sid != "iron_will"]

def use_active_skill(skill_id, attacker, defender, skills_data, class_name):
    """Apply the effect of an active skill during combat."""
    tree = skills_data[class_name]["tree"]
    if skill_id == "ambush":
        # Double damage if attacking from stealth
        base_damage = 20 + attacker["stats"]["str"] * 2
        final_damage = int(base_damage * 2)
        defender["stats"]["hp"] = max(0, defender["stats"]["hp"] - final_damage)
        return f"🗡️ Ambush! Double damage: {final_damage} dealt!"
    elif skill_id == "shield_expert":
        # Parry: block all damage this turn
        attacker["status_effects"].append({"name": "PARRY", "duration": 1})
        return "🛡️ Shield Expert! You will parry the next attack."
    elif skill_id == "poison_blade":
        # Apply poison to defender
        defender["status_effects"].append({"name": "POISON", "duration": 3, "damage": 5})
        return "☠️ Poison Blade! Target is poisoned for 3 turns."
    # Add more active skill effects as needed
    return "Skill used."

# Example integration in combat (pseudo):
# At battle start:
# attacker = apply_passive_skills(attacker, class_name, skills_data)
# defender = apply_passive_skills(defender, class_name, skills_data)
# During turn:
# active_skills = get_active_skills(attacker, class_name, skills_data)
# if player chooses a skill:
#   msg = use_active_skill(skill_id, attacker, defender, skills_data, class_name)
#   await ctx.send(msg)

# PvE Dungeon System
recent_loot = []

@bot.command()
async def dungeon(ctx, floors: int = 5):
    """Enter a procedural dungeon with random events."""
    user_id = str(ctx.author.id)
    player = load_player_data(user_id)
    loot_table = ["gold", "potion", "rare_gem", "ancient_scroll"]
    events = ["monster", "trap", "treasure", "empty"]
    loot_gained = []
    await ctx.send(f"🏰 {ctx.author.mention} enters a {floors}-floor dungeon!")
    for floor in range(1, floors + 1):
        event = random.choices(events, weights=[0.4, 0.2, 0.3, 0.1])[0]
        await ctx.send(f"Floor {floor}: Event - {event.title()}")
        if event == "monster":
            dmg = random.randint(5, 20)
            player["stats"]["hp"] = max(1, player["stats"]["hp"] - dmg)
            await ctx.send(f"👹 Monster attacks! You lose {dmg} HP. (HP: {player['stats']['hp']})")
        elif event == "trap":
            dmg = random.randint(10, 25)
            player["stats"]["hp"] = max(1, player["stats"]["hp"] - dmg)
            await ctx.send(f"⚠️ Trap triggered! You lose {dmg} HP. (HP: {player['stats']['hp']})")
        elif event == "treasure":
            loot = random.choice(loot_table)
            loot_gained.append(loot)
            await ctx.send(f"💎 You found treasure: {loot}!")
        else:
            await ctx.send("...Nothing happens.")
        await asyncio.sleep(1)
    # Add loot to player inventory
    if loot_gained:
        if "inventory" not in player:
            player["inventory"] = []
        player["inventory"].extend(loot_gained)
        recent_loot.extend([(ctx.author.name, l) for l in loot_gained])
        await ctx.send(f"🎁 Dungeon complete! Loot: {', '.join(loot_gained)}")
    else:
        await ctx.send("Dungeon complete! No loot this time.")
    save_player_data(user_id, player)

@bot.command()
async def loot(ctx):
    """View recent loot drops from dungeons."""
    if not recent_loot:
        await ctx.send("No loot has been found yet.")
        return
    lines = [f"{name}: {item}" for name, item in recent_loot[-10:]]
    await ctx.send("**Recent Loot Drops:**\n" + "\n".join(lines))

@bot.command()
async def leaderboard(ctx):
    """Show top 10 players by gold."""
    try:
        with open(PLAYERS_FILE, "r") as f:
            all_players = json.load(f)
    except FileNotFoundError:
        await ctx.send("No player data found.")
        return
    players = list(all_players.values())
    players.sort(key=lambda p: p.get("gold", 0), reverse=True)
    lines = [f"{i+1}. {p.get('username', 'Unknown')} — {p.get('gold', 0)} gold" for i, p in enumerate(players[:10])]
    await ctx.send("**Top 10 Players by Gold:**\n" + "\n".join(lines))

@bot.command()
async def build(ctx, action: str = None, skill_id: str = None):
    """View or allocate skill points. Usage: $build [unlock] [skill_id]"""
    user_id = str(ctx.author.id)
    # Load player data
    try:
        with open(PLAYERS_FILE, "r") as f:
            all_players = json.load(f)
    except FileNotFoundError:
        all_players = {}
    player_data = all_players.get(user_id, load_player_data(user_id))
    class_name = player_data.get("class", "warrior")
    skills_data = load_skills_data()
    skill_tree = skills_data[class_name]["tree"]
    # Ensure skill_points and skills exist
    if "skill_points" not in player_data:
        player_data["skill_points"] = 3
    if "skills" not in player_data:
        player_data["skills"] = {}
    # Unlock skill
    if action == "unlock" and skill_id:
        if skill_id not in skill_tree:
            await ctx.send(f"❌ Skill `{skill_id}` does not exist for your class.")
            return
        can_unlock, reason = can_unlock_skill(player_data, class_name, skill_id, skills_data)
        if not can_unlock:
            await ctx.send(f"❌ {reason}")
            return
        name, desc = unlock_skill(player_data, class_name, skill_id, skills_data)
        save_player_data(user_id, player_data)
        await ctx.send(f"✅ Unlocked skill: **{name}** — {desc}")
        return
    # Show skill tree
    lines = [f"**Skill Points:** {player_data['skill_points']}\n"]
    for sid, skill in skill_tree.items():
        unlocked = "✅" if sid in player_data["skills"] else "❌"
        reqs = ", ".join(skill["requirements"]) if skill["requirements"] else "None"
        lines.append(f"{unlocked} `{sid}`: **{skill['name']}** (Cost: {skill['cost']})\n    {skill['description']}\n    Prerequisites: {reqs}")
    await ctx.send("\n".join(lines))

@bot.command()
async def battle(ctx, opponent: discord.Member = None):
    """Start battle with skill system integration."""
    if not opponent:
        await ctx.send("❌ You need to mention an opponent! `$battle @user`")
        return
    if opponent.id == ctx.author.id:
        await ctx.send("❌ You can't battle yourself!")
        return
    # Load player data
    attacker = load_player_data(ctx.author.id)
    defender = load_player_data(opponent.id)
    attacker["username"] = ctx.author.name
    defender["username"] = opponent.name
    # Load skills data
    skills_data = load_skills_data()
    attacker_class = attacker.get("class", "warrior")
    defender_class = defender.get("class", "warrior")
    # Apply passive skills
    attacker = apply_passive_skills(attacker, attacker_class, skills_data)
    defender = apply_passive_skills(defender, defender_class, skills_data)
    # Save updated data
    save_player_data(ctx.author.id, attacker)
    save_player_data(opponent.id, defender)
    await ctx.send(f"⚔️ **BATTLE START!** {ctx.author.mention} vs {opponent.mention}")
    round_num = 1
    while attacker["stats"]["hp"] > 0 and defender["stats"]["hp"] > 0 and round_num <= 20:
        await ctx.send(f"\n**ROUND {round_num}**")
        # ATTACKER TURN
        attacker_skills = get_active_skills(attacker, attacker_class, skills_data)
        action = "attack"
        if attacker_skills:
            skill_options = ", ".join(attacker_skills)
            await ctx.send(f"{ctx.author.mention}, choose your action: `attack` or one of your skills: {skill_options}")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await bot.wait_for('message', check=check, timeout=30)
                if msg.content.strip().lower() in attacker_skills:
                    action = msg.content.strip().lower()
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} took too long! Defaulting to attack.")
        if action == "attack":
            result, defender_dead = process_combat_turn(attacker, defender, "attack")
            await ctx.send(f"{ctx.author.mention}: {result}")
        else:
            msg = use_active_skill(action, attacker, defender, skills_data, attacker_class)
            await ctx.send(f"{ctx.author.mention}: {msg}")
            defender_dead = defender["stats"]["hp"] <= 0
        if defender_dead:
            await ctx.send(f"🎉 {ctx.author.mention} wins the battle!")
            break
        # DEFENDER TURN
        defender_skills = get_active_skills(defender, defender_class, skills_data)
        action = "attack"
        if defender_skills:
            skill_options = ", ".join(defender_skills)
            await ctx.send(f"{opponent.mention}, choose your action: `attack` or one of your skills: {skill_options}")
            def check(m):
                return m.author == opponent and m.channel == ctx.channel
            try:
                msg = await bot.wait_for('message', check=check, timeout=30)
                if msg.content.strip().lower() in defender_skills:
                    action = msg.content.strip().lower()
            except asyncio.TimeoutError:
                await ctx.send(f"{opponent.mention} took too long! Defaulting to attack.")
        if action == "attack":
            result, attacker_dead = process_combat_turn(defender, attacker, "attack")
            await ctx.send(f"{opponent.mention}: {result}")
        else:
            msg = use_active_skill(action, defender, attacker, skills_data, defender_class)
            await ctx.send(f"{opponent.mention}: {msg}")
            attacker_dead = attacker["stats"]["hp"] <= 0
        if attacker_dead:
            await ctx.send(f"🎉 {opponent.mention} wins the battle!")
            break
        # ROUND END EFFECTS
        attacker_message = combat_round_end(attacker)
        defender_message = combat_round_end(defender)
        if attacker_message:
            await ctx.send(f"{ctx.author.mention}: {attacker_message}")
        if defender_message:
            await ctx.send(f"{opponent.mention}: {defender_message}")
        round_num += 1
        await asyncio.sleep(2)

merchant_items = [
    {"id": "potion", "name": "Potion", "price": 15},
    {"id": "rare_gem", "name": "Rare Gem", "price": 100},
    {"id": "ancient_scroll", "name": "Ancient Scroll", "price": 50},
    {"id": "elixir", "name": "Elixir", "price": 40}
]

@bot.command()
async def merchant(ctx):
    """View today's shop items."""
    # Rotate items daily
    day = int(time.time() // 86400)
    random.seed(day)
    shop = random.sample(merchant_items, k=3)
    lines = [f"{item['id']}: {item['name']} — {item['price']} gold" for item in shop]
    await ctx.send("**Today's Merchant Shop:**\n" + "\n".join(lines))

@bot.command()
async def buy(ctx, item_id: str):
    """Buy an item from the merchant."""
    user_id = str(ctx.author.id)
    player = load_player_data(user_id)
    # Rotate items daily
    day = int(time.time() // 86400)
    random.seed(day)
    shop = {item["id"]: item for item in random.sample(merchant_items, k=3)}
    if item_id not in shop:
        await ctx.send(f"❌ {item_id} is not available in today's shop.")
        return
    item = shop[item_id]
    if player["gold"] < item["price"]:
        await ctx.send(f"❌ Not enough gold. You have {player['gold']}.")
        return
    player["gold"] -= item["price"]
    if "inventory" not in player:
        player["inventory"] = []
    player["inventory"].append(item_id)
    save_player_data(user_id, player)
    await ctx.send(f"✅ Bought {item['name']} for {item['price']} gold. Gold left: {player['gold']}")

@bot.command()
async def sell(ctx, item_id: str):
    """Sell an item from your inventory for half price."""
    user_id = str(ctx.author.id)
    player = load_player_data(user_id)
    # Find item in merchant_items for price
    item = next((i for i in merchant_items if i["id"] == item_id), None)
    if not item:
        await ctx.send(f"❌ {item_id} cannot be sold here.")
        return
    if "inventory" not in player or item_id not in player["inventory"]:
        await ctx.send(f"❌ You don't have {item_id} to sell.")
        return
    player["inventory"].remove(item_id)
    gold_earned = item["price"] // 2
    player["gold"] += gold_earned
    save_player_data(user_id, player)
    await ctx.send(f"✅ Sold {item['name']} for {gold_earned} gold. Gold now: {player['gold']}")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN")) 