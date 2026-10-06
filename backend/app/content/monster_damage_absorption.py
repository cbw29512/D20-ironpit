from __future__ import annotations

import html
import logging
import re

from app.domain.damage_absorption import DamageAbsorptionRule
from app.domain.weapons import DamageType
from app.content.monster_defense_source_audit import parse_defense_profile

logger = logging.getLogger(__name__)
# Source labels are retained for evidence; the typed damage clause supplies semantics.
_REPLACEMENT = re.compile(
    r"(?P<name>[^.]+)\.\s+Whenever the [^.]+? is subjected to "
    r"(?P<type>[A-Za-z]+) damage, it "
    r"(?P<zero>takes no damage and (?:instead )?)?"
    r"regains a number of hit points equal to the (?P=type) damage dealt\.",
    re.IGNORECASE,
)


def damage_absorptions_from_source(
    source_traits: object,
    damage_immunities: set[str],
) -> list[DamageAbsorptionRule]:
    """Bind equal typed healing plus damage prevention to the existing replacement rule."""
    try:
        # Pinned 2014 source is HTML; 2024 source is plain text. Normalize only markup.
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(source_traits or "")))).strip()
        rules: list[DamageAbsorptionRule] = []
        for match in _REPLACEMENT.finditer(text):
            damage_type = DamageType(match.group("type").lower())
            # Some 2024 traits print healing alone: the separately printed Immunity
            # supplies prevention. Never infer prevention from the ability name.
            if not match.group("zero") and damage_type.value not in damage_immunities:
                raise ValueError("Equal typed healing needs printed damage prevention or Immunity.")
            name = match.group("name").strip()
            rules.append(DamageAbsorptionRule(
                source_id=re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
                source_name=name,
                damage_type=damage_type,
            ))
        printed = re.findall(r"(?:^|\.\s+)([^.]*\bAbsorption)\.", text)
        if any(name.strip() not in {rule.source_name for rule in rules} for name in printed):
            raise ValueError("Printed Absorption has an unsupported source payload.")
        if len({rule.damage_type for rule in rules}) != len(rules):
            raise ValueError("Multiple replacements for one damage type are unsupported.")
        return rules
    except Exception:
        logger.exception("Failed to bind damage-to-healing source replacement.")
        raise


def damage_absorptions_2024(row: dict[str, object]) -> list[DamageAbsorptionRule]:
    """Supply the independently printed 2024 Immunities only when needed."""
    try:
        traits = str(row.get("traits", ""))
        # Unrelated, unsupported defense clauses must not obstruct trait intake.
        immunities = parse_defense_profile(row)["damage_immunities"] if _REPLACEMENT.search(traits) else set()
        return damage_absorptions_from_source(traits, immunities)
    except Exception:
        logger.exception("Failed to bind 2024 absorption for %s.", row.get("name"))
        raise
