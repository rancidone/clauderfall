from clauderfall.skills.loader import list_skills, load_skill


def test_list_skills_includes_discovery() -> None:
    skills = list_skills()

    assert any(skill.name == "discovery" for skill in skills)
    assert any(skill.name == "design" for skill in skills)
    assert any(skill.name == "design-completeness-check" for skill in skills)


def test_load_discovery_skill_returns_instructions() -> None:
    skill = load_skill("discovery")

    assert skill.name == "discovery"
    assert "visible, narrative brief" in skill.description
    assert "visible evolving draft" in skill.instructions
    assert "references/product_brief.md" in skill.instructions
    assert "docs/design/" not in skill.instructions


def test_load_design_skill_returns_instructions() -> None:
    skill = load_skill("design")

    assert skill.name == "design"
    assert "concrete, interview-led design artifact" in skill.description
    assert "rigorous design interviewer" in skill.instructions
    assert "references/design_engine_brief.md" in skill.instructions
    assert "docs/design/" not in skill.instructions


def test_load_design_completeness_check_skill_returns_instructions() -> None:
    skill = load_skill("design-completeness-check")

    assert skill.name == "design-completeness-check"
    assert "rigorous audit" in skill.description
    assert "What would implementation still have to invent" in skill.instructions
    assert "references/design-readiness.md" in skill.instructions
    assert "return_to_discovery" in skill.instructions
    assert "docs/design/" not in skill.instructions
