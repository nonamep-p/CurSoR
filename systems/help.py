import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, category: str = None):
        """Show help information for commands."""
        if not category:
            embed = discord.Embed(
                title="🎮 Plagg RPG Bot - Help",
                description="Welcome to the adventure! Here are the available command categories:",
                color=discord.Color.blue()
            )
            
            categories = {
                "character": "👤 Character creation and management",
                "combat": "⚔️ Combat and fighting mechanics",
                "dungeon": "🏰 Dungeon exploration and adventures",
                "inventory": "🎒 Inventory and item management",
                "shop": "🏪 Shopping and economy",
                "progression": "📈 Leveling and progression",
                "social": "👥 Social features and interactions",
                "admin": "⚙️ Administrative commands"
            }
            
            for cat, desc in categories.items():
                embed.add_field(
                    name=f"!help {cat}",
                    value=desc,
                    inline=False
                )
            
            embed.add_field(
                name="Getting Started",
                value="1. Use `!startrpg <class>` to create your character\n"
                      "2. Use `!classinfo` to see available classes\n"
                      "3. Use `!profile` to view your character\n"
                      "4. Use `!enter <dungeon>` to start adventuring!",
                inline=False
            )
            
            embed.set_footer(text="Use !help <category> for detailed command information")
            await ctx.send(embed=embed)
            return
        
        category = category.lower()
        
        if category == "character":
            embed = discord.Embed(
                title="👤 Character Commands",
                description="Commands for character creation and management:",
                color=discord.Color.green()
            )
            
            commands_info = {
                "!startrpg <class>": "Start your RPG adventure with a chosen class\nAvailable classes: warrior, mage, rogue, paladin, archer, berserker, druid, monk",
                "!profile [@user]": "View your character profile or another player's profile",
                "!classinfo [class]": "Get information about available classes or a specific class",
                "!rest": "Rest to recover HP and MP"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.set_footer(text="Example: !startrpg warrior")
            
        elif category == "combat":
            embed = discord.Embed(
                title="⚔️ Combat Commands",
                description="Commands for combat and fighting:",
                color=discord.Color.red()
            )
            
            commands_info = {
                "!fight [@opponent]": "Start a PvP fight or PvE encounter",
                "!enter <dungeon>": "Enter a dungeon to fight monsters",
                "!rest": "Rest to recover HP and MP after combat"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.set_footer(text="Combat happens automatically in dungeons!")
            
        elif category == "dungeon":
            embed = discord.Embed(
                title="🏰 Dungeon Commands",
                description="Commands for dungeon exploration:",
                color=discord.Color.dark_green()
            )
            
            commands_info = {
                "!dungeons": "List all available dungeons and your progress",
                "!enter <dungeon>": "Enter a specific dungeon to explore\nAvailable: forest, cave, castle, abyss",
                "!rest": "Rest to recover HP and MP between dungeon runs"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.add_field(
                name="Dungeon Information",
                value="• Each dungeon has multiple floors with increasing difficulty\n"
                      "• Higher floors require higher levels\n"
                      "• Bosses appear randomly on each floor\n"
                      "• Defeat monsters to gain EXP, gold, and loot!",
                inline=False
            )
            
            embed.set_footer(text="Example: !enter forest")
            
        elif category == "inventory":
            embed = discord.Embed(
                title="🎒 Inventory Commands",
                description="Commands for managing your inventory and items:",
                color=discord.Color.gold()
            )
            
            commands_info = {
                "!inventory [@user]": "View your inventory or another player's inventory",
                "!useitem <item>": "Use a consumable item from your inventory",
                "!equip <item>": "Equip an item to your character",
                "!unequip <slot>": "Unequip an item from a slot (weapon, armor, accessory)",
                "!craft <item>": "Craft an item using materials in your inventory"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.add_field(
                name="Item Types",
                value="• **Weapons**: Increase attack power\n"
                      "• **Armor**: Increase defense\n"
                      "• **Accessories**: Provide special bonuses\n"
                      "• **Consumables**: One-time use items\n"
                      "• **Materials**: Used for crafting",
                inline=False
            )
            
            embed.set_footer(text="Example: !inventory")
            
        elif category == "shop":
            embed = discord.Embed(
                title="🏪 Shop Commands",
                description="Commands for shopping and economy:",
                color=discord.Color.purple()
            )
            
            commands_info = {
                "!shop [category]": "Browse the shop by category\nCategories: weapons, armor, consumables, materials, accessories, all",
                "!buy <item> [quantity]": "Buy an item from the shop",
                "!sell <item> [quantity]": "Sell an item from your inventory",
                "!price <item>": "Check the buy/sell price of an item",
                "!dailydeals": "View today's special deals and discounts",
                "!shopcategories": "Show all available shop categories"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.add_field(
                name="Shop Tips",
                value="• Items are grouped by rarity (Common, Uncommon, Rare, Epic, Legendary)\n"
                      "• Sell items for 50% of their original price\n"
                      "• Daily deals offer discounted items\n"
                      "• Use categories to find specific types of items",
                inline=False
            )
            
            embed.set_footer(text="Example: !shop weapons")
            
        elif category == "progression":
            embed = discord.Embed(
                title="📈 Progression Commands",
                description="Commands for leveling and progression:",
                color=discord.Color.blue()
            )
            
            commands_info = {
                "!profile": "View your current level, EXP, and stats",
                "!enter <dungeon>": "Gain EXP by defeating monsters in dungeons",
                "!fight [@opponent]": "Gain EXP through PvP combat",
                "!achievements": "View your earned achievements"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.add_field(
                name="Progression System",
                value="• Gain EXP by defeating monsters and completing dungeons\n"
                      "• Level up to increase your stats\n"
                      "• Each class has different stat growth rates\n"
                      "• Equipment provides additional stat bonuses\n"
                      "• Achievements track your accomplishments",
                inline=False
            )
            
            embed.set_footer(text="Keep adventuring to level up!")
            
        elif category == "social":
            embed = discord.Embed(
                title="👥 Social Commands",
                description="Commands for social interactions:",
                color=discord.Color.teal()
            )
            
            commands_info = {
                "!profile [@user]": "View another player's character profile",
                "!inventory [@user]": "View another player's inventory",
                "!giveitem @user <item> [quantity]": "Give an item to another player",
                "!leaderboard": "View the top players by level or achievements"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.add_field(
                name="Social Features",
                value="• Compare your progress with other players\n"
                      "• Trade items with friends\n"
                      "• Compete on leaderboards\n"
                      "• Share your achievements",
                inline=False
            )
            
            embed.set_footer(text="Work together to become stronger!")
            
        elif category == "admin":
            embed = discord.Embed(
                title="⚙️ Admin Commands",
                description="Administrative commands (Server Admin only):",
                color=discord.Color.dark_red()
            )
            
            commands_info = {
                "!giveitem @user <item> [quantity]": "Give an item to a player",
                "!setlevel @user <level>": "Set a player's level",
                "!setgold @user <amount>": "Set a player's gold amount",
                "!reset @user": "Reset a player's character data"
            }
            
            for cmd, desc in commands_info.items():
                embed.add_field(name=cmd, value=desc, inline=False)
            
            embed.set_footer(text="These commands require administrator permissions")
            
        else:
            embed = discord.Embed(
                title="❌ Invalid Category",
                description=f"'{category}' is not a valid help category.",
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="Available Categories",
                value="character, combat, dungeon, inventory, shop, progression, social, admin",
                inline=False
            )
            
            embed.set_footer(text="Use !help to see all categories")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def commands(self, ctx):
        """Show a quick reference of all available commands."""
        embed = discord.Embed(
            title="📋 Quick Command Reference",
            description="All available commands:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Character",
            value="`!startrpg` `!profile` `!classinfo` `!rest`",
            inline=True
        )
        
        embed.add_field(
            name="Combat",
            value="`!fight` `!enter`",
            inline=True
        )
        
        embed.add_field(
            name="Dungeons",
            value="`!dungeons` `!enter`",
            inline=True
        )
        
        embed.add_field(
            name="Inventory",
            value="`!inventory` `!useitem` `!equip` `!unequip` `!craft`",
            inline=True
        )
        
        embed.add_field(
            name="Shop",
            value="`!shop` `!buy` `!sell` `!price` `!dailydeals`",
            inline=True
        )
        
        embed.add_field(
            name="Social",
            value="`!giveitem` `!leaderboard`",
            inline=True
        )
        
        embed.add_field(
            name="Help",
            value="`!help` `!commands`",
            inline=True
        )
        
        embed.set_footer(text="Use !help <category> for detailed information")
        await ctx.send(embed=embed)

    @commands.command()
    async def tutorial(self, ctx):
        """Show a beginner's tutorial."""
        embed = discord.Embed(
            title="🎓 Beginner's Tutorial",
            description="Welcome to Plagg RPG! Here's how to get started:",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Step 1: Choose Your Class",
            value="Use `!classinfo` to see all available classes\n"
                  "Each class has different stats and abilities\n"
                  "Example: `!startrpg warrior`",
            inline=False
        )
        
        embed.add_field(
            name="Step 2: Check Your Character",
            value="Use `!profile` to view your character\n"
                  "See your stats, level, and equipment\n"
                  "Your stats increase as you level up",
            inline=False
        )
        
        embed.add_field(
            name="Step 3: Start Adventuring",
            value="Use `!dungeons` to see available locations\n"
                  "Use `!enter forest` to start your first adventure\n"
                  "Fight monsters to gain EXP and loot",
            inline=False
        )
        
        embed.add_field(
            name="Step 4: Manage Your Items",
            value="Use `!inventory` to see your items\n"
                  "Use `!shop` to buy new equipment\n"
                  "Use `!equip <item>` to wear items",
            inline=False
        )
        
        embed.add_field(
            name="Step 5: Rest and Recover",
            value="Use `!rest` to recover HP and MP\n"
                  "You'll need this between dungeon runs\n"
                  "Don't let your HP reach 0!",
            inline=False
        )
        
        embed.add_field(
            name="Tips for Success",
            value="• Start with the Forest dungeon (easiest)\n"
                  "• Buy health potions from the shop\n"
                  "• Equip better weapons and armor as you find them\n"
                  "• Rest between adventures to stay healthy\n"
                  "• Use `!help` for more detailed information",
            inline=False
        )
        
        embed.set_footer(text="Good luck on your adventure!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot)) 