# 🧀 Plagg Bot - Interactive Discord RPG Experience

> **"Plagg, claws out! Time to cause some chaos!"** 🐾

A comprehensive Discord RPG bot featuring **Plagg**, the Kwami of Destruction from Miraculous Ladybug. Experience next-generation tactical combat, character progression, and economy systems with a fully interactive UI and the most chaotic cheese-loving personality in Discord!

## 🎮 Features Overview

- ⚔️ Revolutionary Combat System
- 🎭 Advanced Character Classes & Miraculous Paths
- 🛡️ Equipment, Items, Artifacts
- 🏰 Dungeons & Monster Hunting
- 🛒 Economy, Shop, Crafting, Trading
- 🏆 PvP Arena, Factions, Gladiator Tokens
- ✨ Achievements, Titles, Techniques
- 📚 Tutorials, Info System, Guides
- 🔧 Admin Controls, Analytics, Owner Powers
- 👑 Owner Panel & Infinite Resources
- 📱 Interactive UI: Dropdowns, Buttons, Embeds

## 🗂️ Modular Structure

```
CurSoR/
│
├── main.py                # Bot entry point
├── config.py              # Config/settings management
├── requirements.txt
├── README.md
│
├── data/                  # Data storage (JSON/db)
│   ├── players.json
│   ├── items.json
│   ├── classes.json
│   ├── dungeons.json
│   └── ...
│
├── systems/               # Core systems (cogs)
│   ├── combat.py
│   ├── character.py
│   ├── inventory.py
│   ├── economy.py
│   ├── dungeon.py
│   ├── shop.py
│   ├── pvp.py
│   ├── admin.py
│   ├── achievement.py
│   ├── guild.py
│   ├── tutorial.py
│   └── ...
│
├── ui/                    # UI elements (embeds, views, buttons, dropdowns)
│   ├── embeds.py
│   ├── views.py
│   ├── buttons.py
│   ├── dropdowns.py
│   └── ...
│
├── utils/                 # Utility functions/helpers
│   └── helpers.py
│
└── database/              # DB integration (if needed)
    └── db.py
```

## 🚀 Extensibility
- Add new cogs in `systems/` for each major feature.
- Use `ui/` for all embeds, buttons, dropdowns, and views.
- Store player/item/dungeon data in `data/` as JSON (or DB for scale).
- Integrate AI/chatbot as a cog or utility module.

## 🛠️ Next Steps
- Refactor codebase to match this structure.
- Implement advanced UI (embeds, buttons, dropdowns).
- Build out each system as a cog for modularity and maintainability.

See full command list and system details below! 