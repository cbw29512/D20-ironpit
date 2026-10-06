from __future__ import annotations

import html
import logging
import re

from app.domain.timed_self_buffs import TimedHostileConditionAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)
# Intake matches mechanical sentences. Printed headings are only source labels.
_AURA_2014 = re.compile(
    r"(?P<name>[^.]+)\. Any creature that starts its turn within (?P<radius>\d+) feet "
    r"of the (?P<creature>[^.]+?) must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>Constitution) saving throw or be (?P<condition>poisoned) "
    r"until the start of its next turn\. On a successful saving throw, the creature "
    r"is immune to the (?P=creature)['’]s (?P<label>[^.]+?) for 24 hours\.",
    re.IGNORECASE,
)
_AURA_2024 = re.compile(
    r"(?P<name>[^.]+)\. (?P<ability>Constitution) Saving Throw: DC (?P<dc>\d+), "
    r"any creature that starts its turn in a (?P<radius>\d+)-foot Emanation "
    r"originating from the (?P<creature>[^.]+?)\. Failure: The target has the "
    r"(?P<condition>Poisoned) condition until the start of its next turn\."
    r"(?: Success: The target is immune to this (?P=creature)['’]s "
    r"(?P<label>[^.]+?) for 24 hours\.)?",
    re.IGNORECASE,
)


def condition_auras_from_source(source_traits: object, ruleset: str) -> list[TimedSelfBuffAction]:
    """Bind printed passive save/condition auras to the existing timed aura payload."""
    try:
        if ruleset not in {"2014", "2024"}:
            raise ValueError("Condition aura intake requires an explicit supported ruleset.")
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(source_traits or "")))).strip()
        # HTML formatting may leave a space between the heading and its period.
        text = re.sub(r"\s+\.", ".", text)
        pattern = _AURA_2014 if ruleset == "2014" else _AURA_2024
        actions = []
        for match in pattern.finditer(text):
            name = match.group("name").strip()
            label = match.group("label")
            if label and label.casefold() != name.casefold():
                raise ValueError("Printed source immunity must identify its own aura.")
            if text[match.end():].lstrip().startswith("Success:"):
                raise ValueError("Condition aura has an unsupported success outcome.")
            actions.append(TimedSelfBuffAction(
                id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
                name=name,
                activation_timing="passive",
                expiry_timing=None,
                hostile_start_turn_condition_aura=TimedHostileConditionAura(
                    radius_ft=int(match.group("radius")),
                    save_ability=match.group("ability").casefold(),
                    save_dc=int(match.group("dc")),
                    condition_id=match.group("condition").casefold(),
                    success_immunity=label is not None,
                    source_is_magical=False,
                    # The next matching target-start window also covers extra
                    # turns in this round; a round-number timer would not.
                    condition_duration_rounds=None,
                    condition_expiry_timing="target_turn_start",
                    effect_tags=["poison"],
                ),
                animation="condition-aura",
            ))
        if len({action.id for action in actions}) != len(actions):
            raise ValueError("Duplicate passive condition aura identities are unsupported.")
        return actions
    except Exception:
        logger.exception("Failed %s passive condition-aura source binding.", ruleset)
        raise
