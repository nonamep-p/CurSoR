def render_inventory(inventory, items):
    lines = []
    for item_id, qty in inventory.items():
        item = items.get(item_id, {"name": item_id})
        lines.append(f"{item['name']} x{qty}")
    return "\n".join(lines) 