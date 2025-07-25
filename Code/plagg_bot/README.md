# Plagg Bot - Miraculous Ladybug Themed Discord RPG

Welcome to **Plagg Bot**, a Discord RPG bot inspired by Miraculous Ladybug, featuring Plagg's mischievous personality! Battle in PvP and PvE, explore dungeons, develop your skill tree, and collect items—all with persistent progression.

## Features
- **Miraculous Ladybug Theme**: Plagg as your sassy guide
- **PvP & PvE Combat**: Fight other players or AI enemies
- **Skill Trees**: Unlock and upgrade unique abilities
- **Inventory System**: Collect, equip, and use items
- **Progression**: Level up, gain new skills, and grow stronger
- **Dungeons**: Team up or go solo in challenging dungeons
- **Persistent Data**: All player and game data is stored in JSON files
- **Discord Embed UI**: Rich, interactive commands and visuals
- **Ready for Railway/Replit**: Easy deployment

## Setup

### Requirements
- Python 3.11+
- `discord.py` 2.3+

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nonamep-p/CurSoR.git
   cd CurSoR/Code/plagg_bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your bot token:
   - Copy your Discord bot token into `config.py` as instructed below.

### Running the Bot
```bash
python main.py
```

## File Structure
```
Code/plagg_bot/
├── main.py
├── config.py
├── data/
│   ├── players.json
│   ├── items.json
│   ├── classes.json
│   ├── skills.json
│   ├── dungeons.json
├── systems/
│   ├── combat.py
│   ├── progression.py
│   ├── inventory.py
│   ├── skilltree.py
│   ├── dungeon.py
│   ├── matchmaking.py
│   ├── plagg_core.py
├── ui/
│   ├── visual.py
│   ├── embeds.py
│   ├── buttons.py
│   ├── skilltree_render.py
│   ├── inventory_render.py
├── README.md
```

## Configuration
Edit `config.py` and set your Discord bot token:
```python
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
```

## Contributing
Pull requests and suggestions are welcome!

## License
MIT 