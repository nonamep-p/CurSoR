import discord

def player_profile_embed(player):
    embed = discord.Embed(title=f"{player['name']}'s Profile", color=0x7289da)
    embed.add_field(name="Class", value=player.get('class', 'Unassigned'))
    embed.add_field(name="Level", value=player.get('level', 1))
    embed.add_field(name="HP", value=f"{player.get('hp', 0)}/{player.get('max_hp', 0)}")
    if player.get('prestige', 0) > 0:
        embed.add_field(name="Prestige", value=player['prestige'])
    return embed 