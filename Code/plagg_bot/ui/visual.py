def format_hp_bar(current, max_hp):
    bar_length = 20
    filled = int(bar_length * current / max_hp)
    return f"[{'█' * filled}{'-' * (bar_length - filled)}] {current}/{max_hp} HP" 