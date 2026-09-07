from __future__ import annotations

from dataclasses import dataclass

from app.content.monster_spell_source_parser import source_spell_names
from app.domain.models import CombatantTemplate


@dataclass(frozen=True)
class MonsterSpellSelection:
    """Explicit Iron Pit boundary for one named SRD caster."""

    included: tuple[tuple[str, str], ...] = ()
    ignored: tuple[str, ...] = ()
    excluded: tuple[str, ...] = ()

    def source_names(self) -> set[str]:
        return {name for name, _runtime_id in self.included} | set(self.ignored) | set(self.excluded)

    def runtime_ids(self) -> set[str]:
        return {runtime_id for _name, runtime_id in self.included}


# `ignored` means no supported Iron Pit combat-math consequence.
# `excluded` means combat-relevant but deliberately outside the current simple spell surface.
# `included` maps the printed spell name to the shared runtime spell/action id.
MONSTER_CASTER_SPELL_SELECTIONS: dict[str, MonsterSpellSelection] = {
    "Druid": MonsterSpellSelection(
        included=(("Thunderwave", "thunderwave"),),
        ignored=("Druidcraft", "Speak with Animals", "Animal Messenger", "Long-strider"),
        excluded=("Entangle", "Moonbeam"),
    ),
    "Dryad": MonsterSpellSelection(
        ignored=("Druidcraft", "Pass without Trace"),
        excluded=("Animal Friendship", "Charm Monster", "Entangle"),
    ),
    "Imp": MonsterSpellSelection(
        excluded=("Invisibility",),
    ),
}


def _runtime_action_ids(template: CombatantTemplate) -> set[str]:
    families = (
        template.spell_save_actions,
        template.spell_attack_actions,
        template.defensive_spell_actions,
        template.healing_actions,
        template.condition_removal_actions,
    )
    return {action.id for family in families for action in family}


def curated_spellcasting_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> list[str] | None:
    """Return None without a reviewed list; otherwise fail closed on source/list/runtime drift."""
    selection = MONSTER_CASTER_SPELL_SELECTIONS.get(str(row.get("name", "")))
    if selection is None:
        return None
    actual = source_spell_names(row)
    if actual != selection.source_names():
        return ["curated-monster-spell-list-mismatch"]
    missing_runtime = selection.runtime_ids() - _runtime_action_ids(template)
    if missing_runtime:
        return ["curated-monster-spell-not-vendored"]
    return []
