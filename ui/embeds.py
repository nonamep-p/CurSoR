import discord

def help_embed(category=None):
    """Return a Discord embed for the help menu."""
    embed = discord.Embed(
        title="🧀 Plagg Bot Help Menu",
        description="Use the dropdown or buttons below to explore commands by category.",
        color=discord.Color.blurple()
    )
    if category is None:
        embed.add_field(name="Getting Started", value="$start, $profile, $inventory, $heal", inline=False)
        embed.add_field(name="Combat", value="$battle, $skills, $ultimate, $flee", inline=False)
        embed.add_field(name="Economy", value="$merchant, $buy, $sell, $loot", inline=False)
        embed.add_field(name="Dungeons", value="$dungeon, $adventure", inline=False)
        embed.set_footer(text="Select a category for more details.")
    else:
        # Example: show only commands for the given category
        if category == "Combat":
            embed.add_field(name="Combat Commands", value="$battle, $skills, $ultimate, $flee", inline=False)
        elif category == "Economy":
            embed.add_field(name="Economy Commands", value="$merchant, $buy, $sell, $loot", inline=False)
        # Add more categories as needed
        embed.set_footer(text=f"Category: {category}")
    return embed

# Player profile embed implementation
def player_profile_embed(player):
    """Return a Discord embed for the player profile."""
    embed = discord.Embed(
        title=f"{player.get('username', 'Unknown')}'s Profile",
        color=discord.Color.green()
    )
    embed.add_field(name="Class", value=player.get('class', 'Unassigned'))
    embed.add_field(name="Level", value=player.get('level', 1))
    embed.add_field(name="HP", value=f"{player.get('hp', 0)}/{player.get('max_hp', 0)}")
    embed.add_field(name="Gold", value=player.get('gold', 0))
    return embed 