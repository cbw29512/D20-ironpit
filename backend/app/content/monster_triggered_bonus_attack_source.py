from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_limited_resources import source_limited_resource
from app.domain.models import CombatantTemplate
from app.domain.triggered_bonus_attacks import TriggeredBonusAttack

logger = logging.getLogger(__name__)
_RAMPAGE = re.compile(
    r"Rampage\s*\((?P<limit>\d+\s*/\s*Day)\)\.\s+Immediately after dealing damage "
    r"to a creature that (?:was|is) already Bloodied, the [^.]+(?:can )?move up to half its Speed, "
    r"and it makes one (?P<attack>[A-Z][A-Za-z0-9’' -]+) attack\.",
    re.IGNORECASE,
)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug triggered Bonus Action value %r.", value)
        raise RuntimeError("Triggered Bonus Action id could not be derived.") from exc


def parse_triggered_bonus_attacks(
    monster: str,
    source_bonus_actions: object,
    attack_ids_by_name: dict[str, str],
) -> tuple[list[TriggeredBonusAttack], list]:
    try:
        text = str(source_bonus_actions or "")
        match = _RAMPAGE.search(text)
        if match is None:
            return [], []
        attack_name = match.group("attack").strip()
        attack_id = attack_ids_by_name.get(attack_name.lower())
        if attack_id is None:
            raise ValueError(f"Rampage references unknown attack {attack_name!r} for {monster}.")
        feature_id = f"srd-{_slug(monster)}-rampage"
        resource = source_limited_resource(feature_id, "Rampage", match.group("limit"))
        if resource is None:
            raise ValueError(f"Rampage resource could not be compiled for {monster}.")
        return [TriggeredBonusAttack(
            id=feature_id,
            name="Rampage",
            trigger="damage_target_already_bloodied",
            attack_id=attack_id,
            resource_id=resource.id,
        )], [resource]
    except (TypeError, ValueError):
        logger.exception("Invalid triggered Bonus Action source for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Triggered Bonus Action parsing failed for %s.", monster)
        raise RuntimeError(f"Triggered Bonus Action parsing failed for {monster}.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for triggered Bonus Actions.")
        raise


def complete_monster_triggered_bonus_attacks(
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
            by_name = {attack.weapon.name.lower(): attack.id for attack in attacks}
            features, resources = parse_triggered_bonus_attacks(
                template.name, row.get("bonusActions", ""), by_name,
            )
            known = {item.id for item in template.resources}
            merged_resources = [*template.resources, *(item for item in resources if item.id not in known)]
            completed.append(template.model_copy(update={
                "triggered_bonus_attacks": features,
                "resources": merged_resources,
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete monster triggered Bonus Actions.")
        raise RuntimeError("Monster triggered Bonus Action completion failed.") from exc
