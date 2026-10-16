"""Assigned research conditions, distinct from later observed skill behavior."""
import hashlib
import json

CONDITIONS = ("baseline", "discover-general", "discover-science", "stamped-explicit")
CONDITION_CHOICES = CONDITIONS + ("skills",)
RESEARCH_SKILLS = (
    "align-with-stamped-principles", "stamped-conventions", "create-stamped-project",
    "create-repronim-stamped-project", "do-full-research-loop", "pixi-with-stamped",
)


def canonical_condition(condition):
    if condition not in CONDITION_CHOICES:
        raise ValueError("Unknown research condition: " + condition)
    return "stamped-explicit" if condition == "skills" else condition


def assignment(content, requested):
    """Resolve from the coordinator's committed config, never its working file."""
    config = json.loads(content)
    if config.get("version") != 1 or set(config.get("conditions", {})) != set(CONDITIONS):
        raise ValueError("Unsupported research condition configuration")
    condition = canonical_condition(requested)
    selected = config["conditions"][condition]
    skills = selected["supplied_skills"]
    expected = list(RESEARCH_SKILLS) if condition == "stamped-explicit" else []
    if skills != expected or not isinstance(selected["additional_prompt"], str):
        raise ValueError("Condition supplied skills/prompt differ from the supported design")
    if condition == "baseline" and selected["additional_prompt"]:
        raise ValueError("Baseline must not receive an additional instruction")
    return {
        "config_version": config["version"],
        "config_sha256": hashlib.sha256(content).hexdigest(),
        "requested_condition": requested,
        "condition": condition,
        "additional_prompt": selected["additional_prompt"],
        "additional_prompt_sha256": hashlib.sha256(selected["additional_prompt"].encode()).hexdigest(),
        "supplied_skills": skills,
    }


def supplied_skills(receipt):
    if "assignment" in receipt:
        return tuple(receipt["assignment"]["supplied_skills"])
    # Old input snapshots supplied these skills without an explicit invocation.
    return RESEARCH_SKILLS if receipt["condition"] == "skills" else ()
