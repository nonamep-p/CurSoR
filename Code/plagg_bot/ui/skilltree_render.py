def render_skilltree(skills, unlocked):
    lines = []
    for skill_id, skill in skills.items():
        status = "✅" if skill_id in unlocked else "❌"
        lines.append(f"{status} {skill['name']}: {skill['description']}")
    return "\n".join(lines) 