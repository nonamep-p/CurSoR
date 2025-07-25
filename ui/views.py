import discord

class HelpDropdownView(discord.ui.View):
    """Dropdown view for help categories."""
    def __init__(self, callback):
        super().__init__()
        self.add_item(HelpCategoryDropdown(callback))

class HelpCategoryDropdown(discord.ui.Select):
    def __init__(self, callback):
        options = [
            discord.SelectOption(label="All", value="all", description="Show all commands"),
            discord.SelectOption(label="Getting Started", value="getting_started"),
            discord.SelectOption(label="Combat", value="Combat"),
            discord.SelectOption(label="Economy", value="Economy"),
            discord.SelectOption(label="Dungeons", value="Dungeons"),
        ]
        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)
        self.callback_func = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.values[0]) 