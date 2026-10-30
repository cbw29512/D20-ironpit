from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate
from app.domain.weapons import WeaponAttackKind
from app.domain.reactions import ParryReaction

logger = logging.getLogger(__name__)
_RIPOSTE = re.compile(
    r"Riposte\.\s+Trigger:\s+(?:"
    r"The [^.]+ is hit by a melee attack roll while holding a weapon|"
    r"A creature hits the [^.]+ with a melee attack roll while the [^.]+ is holding a weapon"
    r")\.\s+"
    r"Response:\s+The [^.]+ adds (?P<bonus>\d+) to its AC against that attack, possibly causing it to miss\.\s+"
    r"On a miss, the [^.]+ makes one (?P<attack>[A-Z][A-Za-z0-9’' -]+) attack against the triggering creature "
    r"if (?:(?:the creature is )?within (?P<range>\d+) feet|within range)\.",
    re.IGNORECASE,
)


def _attack_range_ft(attack) -> int:
    try:
        kind = attack.weapon.attack_kind
        if kind is WeaponAttackKind.MELEE:
            return attack.weapon.reach_ft
        if kind is WeaponAttackKind.RANGED:
            if attack.weapon.long_range_ft is None:
                raise ValueError("Ranged Riposte attack lacks a long range.")
            return attack.weapon.long_range_ft
        if kind is WeaponAttackKind.MELEE_OR_RANGED:
            return max(attack.weapon.reach_ft, attack.weapon.long_range_ft or 0)
        raise ValueError(f"Unsupported Riposte attack kind: {kind}.")
    except Exception as exc:
        logger.exception("Failed to derive Riposte attack range.")
        raise RuntimeError("Riposte attack range could not be derived.") from exc



def parse_riposte(
    source_reactions: object,
    attacks_by_name: dict[str, object],
) -> ParryReaction | None:
    try:
        text = str(source_reactions or "")
        if "Riposte." not in text:
            return None
        match = _RIPOSTE.search(text)
        if match is None:
            raise ValueError("Riposte source text is present but unsupported.")
        attack_name = match.group("attack").strip().lower()
        attack = attacks_by_name.get(attack_name)
        if attack is None:
            raise ValueError(f"Riposte references unknown attack {match.group('attack')!r}.")
        explicit_range = match.group("range")
        return ParryReaction(
            ac_bonus=int(match.group("bonus")),
            source_feature="riposte",
            counterattack_attack_id=attack.id,
            counterattack_range_ft=(
                int(explicit_range) if explicit_range is not None else _attack_range_ft(attack)
            ),
        )
    except (TypeError, ValueError):
        logger.exception("Invalid Riposte source data.")
        raise
    except Exception as exc:
        logger.exception("Riposte source parsing failed.")
        raise RuntimeError("Riposte source could not be parsed.") from exc


def riposte_matches(template: CombatantTemplate, source_reactions: object) -> bool:
    try:
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        expected = parse_riposte(
            source_reactions,
            {attack.weapon.name.lower(): attack for attack in attacks},
        )
        return expected is not None and template.parry_reaction == expected
    except Exception as exc:
        logger.exception("Failed to audit Riposte for %s.", template.id)
        raise RuntimeError("Riposte source audit failed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for Riposte.")
        raise


def complete_monster_riposte_reactions(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        rows = _rows_by_name()
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            row = rows.get(template.name)
            if row is None:
                raise ValueError(f"No SRD source row for monster {template.name!r}.")
            attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
            by_name = {attack.weapon.name.lower(): attack for attack in attacks}
            riposte = parse_riposte(row.get("reactions", ""), by_name)
            completed.append(
                template.model_copy(update={"parry_reaction": riposte})
                if riposte is not None else template
            )
        return completed
    except Exception as exc:
        logger.exception("Failed to complete monster Riposte reactions.")
        raise RuntimeError("Monster Riposte completion failed.") from exc
