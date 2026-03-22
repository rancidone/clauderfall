from clauderfall.skills.loader import list_skills, load_skill


def test_list_skills_includes_discovery() -> None:
    skills = list_skills()

    assert any(skill.name == "discovery" for skill in skills)


def test_load_discovery_skill_returns_instructions() -> None:
    skill = load_skill("discovery")

    assert skill.name == "discovery"
    assert "visible, narrative brief" in skill.description
    assert "visible evolving draft" in skill.instructions
    assert "references/product_brief.md" in skill.instructions
    assert "docs/design/" not in skill.instructions
