# 🎮 Plagg Discord RPG Bot

A comprehensive Discord RPG bot featuring character progression, dungeon crawling, combat systems, and an extensive economy. Built with modular architecture for easy expansion and customization.

## 🌟 Features

### Core Gameplay (MVP)
- **Universal Combat System** - PvE battles with monsters, PvP duels, real-time stats
- **Character Creation & Progression** - 8 unique classes with different stats and abilities
- **Inventory & Equipment** - 200+ unique items across 5 rarity tiers
- **Basic Economy** - Gold system, shop purchases, item trading
- **Dungeon Crawling** - 4 dungeons with progressive floors and bosses
- **Interactive UI** - Rich embeds, buttons, and visual feedback

### Character System
- **8 Unique Classes**: Warrior, Mage, Rogue, Paladin, Archer, Berserker, Druid, Monk
- **Stat Progression**: HP, MP, Attack, Defense, Magic, Speed with class-specific growth
- **Skill System**: Class-specific abilities with mana costs and cooldowns
- **Equipment Slots**: Weapon, Armor, and Accessory slots with stat bonuses

### Dungeon System
- **4 Dungeons**: Forest, Cave, Castle, Abyss with increasing difficulty
- **Progressive Floors**: Each dungeon has 3 floors with level requirements
- **Monster Variety**: 40+ unique monsters with different abilities and loot tables
- **Boss Encounters**: Special boss monsters with rare loot drops
- **Environmental Hazards**: Special events and challenges

### Economy & Trading
- **Comprehensive Shop**: Items organized by category and rarity
- **Daily Deals**: Special discounted items that change daily
- **Trading System**: Give items to other players
- **Crafting**: Combine materials to create new items
- **Rarity System**: Common, Uncommon, Rare, Epic, Legendary items

### Social Features
- **Player Profiles**: View detailed character information
- **Leaderboards**: Compare progress with other players
- **Achievement System**: Track accomplishments and milestones
- **Social Interactions**: View other players' inventories and profiles

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Discord.py library

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-rpg-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot**
   - Edit `config.py` and add your Discord bot token
   - Or set the `DISCORD_TOKEN` environment variable

4. **Run the bot**
   ```bash
   python main.py
   ```

## 📖 Commands

### Getting Started
- `!startrpg <class>` - Create your character with a chosen class
- `!classinfo [class]` - View information about available classes
- `!profile [@user]` - View your or another player's profile
- `!tutorial` - Show beginner's tutorial

### Character Management
- `!rest` - Rest to recover HP and MP
- `!equip <item>` - Equip an item to your character
- `!unequip <slot>` - Unequip an item from a slot

### Combat & Adventure
- `!dungeons` - List available dungeons and progress
- `!enter <dungeon>` - Enter a dungeon to fight monsters
- `!fight [@opponent]` - Start a PvP or PvE fight

### Inventory & Items
- `!inventory [@user]` - View inventory
- `!useitem <item>` - Use a consumable item
- `!craft <item>` - Craft an item using materials

### Shop & Economy
- `!shop [category]` - Browse shop by category
- `!buy <item> [quantity]` - Buy items from shop
- `!sell <item> [quantity]` - Sell items for gold
- `!price <item>` - Check item prices
- `!dailydeals` - View today's special deals

### Social Features
- `!giveitem @user <item> [quantity]` - Give items to other players
- `!leaderboard` - View top players

### Help & Information
- `!help [category]` - Get detailed help information
- `!commands` - Quick command reference

## 🏗️ Project Structure

```
discord-rpg-bot/
├── main.py                 # Bot entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── data/                 # Game data files
│   ├── players.json      # Player data
│   ├── items.json        # Item database
│   ├── classes.json      # Character classes
│   ├── skills.json       # Skill definitions
│   ├── dungeons.json     # Dungeon data
│   └── monsters.json     # Monster database
│
├── systems/              # Game systems
│   ├── character.py      # Character management
│   ├── combat.py         # Combat system
│   ├── dungeon.py        # Dungeon exploration
│   ├── inventory.py      # Inventory management
│   ├── shop.py           # Shop and economy
│   ├── help.py           # Help system
│   └── ...
│
├── ui/                   # User interface components
│   ├── embeds.py         # Embed templates
│   ├── visual.py         # Visual formatting
│   └── views.py          # Interactive views
│
└── utils/                # Utility functions
    └── helpers.py        # Helper functions
```

## 🎯 Game Mechanics

### Character Classes
Each class has unique starting stats and growth rates:

| Class | HP | MP | Attack | Defense | Magic | Speed | Specialization |
|-------|----|----|--------|---------|-------|-------|----------------|
| Warrior | 120 | 30 | 25 | 20 | 5 | 15 | Physical Combat |
| Mage | 80 | 100 | 10 | 8 | 35 | 12 | Magical Combat |
| Rogue | 90 | 40 | 20 | 12 | 8 | 25 | Stealth Combat |
| Paladin | 110 | 60 | 22 | 18 | 15 | 14 | Holy Combat |
| Archer | 85 | 35 | 28 | 10 | 6 | 20 | Ranged Combat |
| Berserker | 130 | 20 | 30 | 15 | 3 | 18 | Fury Combat |
| Druid | 95 | 80 | 15 | 12 | 25 | 16 | Nature Magic |
| Monk | 100 | 50 | 24 | 14 | 10 | 22 | Martial Arts |

### Item Rarity System
- **Common** (⚪) - Basic items, low cost
- **Uncommon** (🟢) - Better items, moderate cost
- **Rare** (🔵) - Powerful items, high cost
- **Epic** (🟣) - Very powerful items, very high cost
- **Legendary** (🟠) - Ultimate items, extremely high cost

### Dungeon Progression
1. **Forest** (Level 1-5) - Beginner-friendly, basic monsters
2. **Cave** (Level 2-6) - Crystal-themed, moderate difficulty
3. **Castle** (Level 8-12) - Undead enemies, high difficulty
4. **Abyss** (Level 15-20) - Void creatures, ultimate challenge

## 🔧 Configuration

### Bot Setup
1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot and copy the token
3. Add the token to `config.py` or set as environment variable
4. Invite the bot to your server with appropriate permissions

### Permissions Required
- Send Messages
- Embed Links
- Use Slash Commands
- Add Reactions
- Read Message History

## 🛠️ Development

### Adding New Features
The bot is built with a modular architecture. To add new features:

1. **Create new data files** in the `data/` directory
2. **Add new systems** in the `systems/` directory
3. **Update main.py** to load new cogs
4. **Add UI components** in the `ui/` directory

### Extending the Game
- **New Classes**: Add to `classes.json` and update character system
- **New Items**: Add to `items.json` with proper rarity and stats
- **New Dungeons**: Add to `dungeons.json` with floors and monsters
- **New Monsters**: Add to `monsters.json` with stats and loot tables

## 📊 Performance

### Data Storage
- All game data is stored in JSON files for simplicity
- Player data is automatically saved after each action
- No database setup required

### Scalability
- Modular design allows easy addition of new features
- JSON-based data storage can be migrated to databases later
- Cog-based architecture supports multiple servers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the `!help` command in-game
2. Review the `!tutorial` for beginners
3. Check the project documentation
4. Open an issue on GitHub

## 🎉 Acknowledgments

- Built with Discord.py
- Inspired by classic RPG games
- Community feedback and suggestions
- Open source contributors

---

**Happy adventuring! 🐾**

*Plagg the RPG Bot - Bringing epic adventures to Discord servers everywhere!* 