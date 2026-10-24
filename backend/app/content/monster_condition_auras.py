from __future__ import annotations

import html
import logging
import re

from app.domain.timed_self_buffs import TimedHostileConditionAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)

_ABILITY = r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"

_STENCH_AURA_2014 = re.compile(
    rf"(?P<name>[^.]+)\. Any creature that starts its turn within (?P<radius>\d+) feet "
    rf"of the (?P<creature>[^.]+?) must succeed on a DC (?P<dc>\d+) "
    rf"(?P<ability>{_ABILITY}) saving throw or be (?P<condition>[A-Za-z]+) "
    rf"until the start of its next turn\. On a successful saving throw, the creature "
    rf"is immune to the (?P=creature)['’]s (?P<label>[^.]+?) for 24 hours\.",
    re.IGNORECASE,
)

_HOSTILE_AURA_2014 = re.compile(
    rf"(?P<name>[^.]+)\. Any creature hostile to the (?P<creature>[^.]+?) that starts "
    rf"its turn within (?P<radius>\d+) feet of the (?P=creature) must make a DC "
    rf"(?P<dc>\d+) (?P<ability>{_ABILITY}) saving throw, unless the (?P=creature) is "
    rf"incapacitated\. On a failed save, the creature is (?P<condition>[A-Za-z]+) until "
    rf"the start of its next turn\. If a creature['’]s saving throw is successful, the "
    rf"creature is immune to the (?P=creature)['’]s (?P<label>[^.]+?) for the next 24 hours\.",
    re.IGNORECASE,
)

_AURA_2024 = re.compile(
    rf"(?P<name>[^.]+)\. (?P<ability>{_ABILITY}) Saving Throw: DC (?P<dc>\d+), "
    rf"any creature that starts its turn in a (?P<radius>\d+)-foot Emanation "
    rf"originating from the (?P<creature>[^.]+?)\. Failure: The target has the "
    rf"(?P<condition>[A-Za-z]+) condition until the start of its next turn\."
    rf"(?: Success: The target is immune to this (?P=creature)['’]s "
    rf"(?P<label>[^.]+?) for 24 hours\.)?",
    re.IGNORECASE,
)


def _action_from_match(match: re.Match[str], *, source_incapacitation_gate: bool) -> TimedSelfBuffAction:
    try:
        name = match.group("name").strip()
        label = match.groupdict().get("label")
        if label and label.casefold() != name.casefold():
            raise ValueError("Printed source immunity must identify its own aura.")
        condition = match.group("condition").casefold()
        return TimedSelfBuffAction(
            id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
            name=name,
            activation_timing="passive",
            expiry_timing=None,
            hostile_start_turn_condition_aura=TimedHostileConditionAura(
                radius_ft=int(match.group("radius")),
                save_ability=match.group("ability").casefold(),
                save_dc=int(match.group("dc")),
                condition_id=condition,
                success_immunity=label is not None,
                source_is_magical=False,
                inactive_while_source_incapacitated=source_incapacitation_gate,
                condition_duration_rounds=None,
                condition_expiry_timing="target_turn_start",
                effect_tags=[condition],
            ),
            animation="condition-aura",
        )
    except Exception:
        logger.exception("Failed to compile source-declared hostile condition aura.")
        raise


def condition_auras_from_source(source_traits: object, ruleset: str) -> list[TimedSelfBuffAction]:
    """Bind printed passive save/condition auras to the existing timed aura payload."""
    try:
        if ruleset not in {"2014", "2024"}:
            raise ValueError("Condition aura intake requires an explicit supported ruleset.")
        text = re.sub(
            r"\s+", " ",
            html.unescape(re.sub(r"<[^>]+>", " ", str(source_traits or ""))),
        ).strip()
        text = re.sub(r"\s+\.", ".", text)

        specs = (
            [(_STENCH_AURA_2014, False), (_HOSTILE_AURA_2014, True)]
            if ruleset == "2014"
            else [(_AURA_2024, False)]
        )
        matched: list[tuple[int, TimedSelfBuffAction]] = []
        for pattern, source_gate in specs:
            for match in pattern.finditer(text):
                if ruleset == "2024" and text[match.end():].lstrip().startswith("Success:"):
                    raise ValueError("Condition aura has an unsupported success outcome.")
                matched.append((
                    match.start(),
                    _action_from_match(match, source_incapacitation_gate=source_gate),
                ))

        actions = [action for _, action in sorted(matched, key=lambda item: item[0])]
        if len({action.id for action in actions}) != len(actions):
            raise ValueError("Duplicate passive condition aura identities are unsupported.")
        return actions
    except Exception:
        logger.exception("Failed %s passive condition-aura source binding.", ruleset)
        raise
