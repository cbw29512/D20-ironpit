from __future__ import annotations

from app.domain.combat_treasure import CombatTreasureAward
from app.domain.models import CombatantTemplate


def _apply_weapon(template: CombatantTemplate, award: CombatTreasureAward) -> None:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    index = next((i for i, attack in enumerate(attacks) if attack.id == award.target_id), None)
    if index is None:
        raise ValueError(f"Treasure target attack {award.target_id} is not on {template.name}.")
    attack = attacks[index]
    enhanced = attack.model_copy(update={
        "attack_bonus": attack.attack_bonus + award.bonus,
        "damage_bonus": attack.damage_bonus + award.bonus,
        "weapon": attack.weapon.model_copy(update={"name": award.name}),
    })
    if index == 0:
        template.weapon_attack = enhanced
    else:
        template.alternate_weapon_attacks[index - 1] = enhanced


def _apply_spell_focus(template: CombatantTemplate, award: CombatTreasureAward) -> None:
    template.spell_attack_actions = [
        action.model_copy(update={"attack_bonus": action.attack_bonus + award.bonus})
        for action in template.spell_attack_actions
    ]
    template.spell_save_actions = [
        action.model_copy(update={"dc": action.dc + award.bonus})
        for action in template.spell_save_actions
    ]


def _apply_resource(template: CombatantTemplate, award: CombatTreasureAward) -> None:
    found = False
    updated = []
    for resource in template.resources:
        if resource.id == award.target_id:
            found = True
            updated.append(resource.model_copy(update={"max_uses": resource.max_uses + award.bonus}))
        else:
            updated.append(resource)
    if not found:
        raise ValueError(f"Treasure target resource {award.target_id} is not on {template.name}.")
    template.resources = updated


def _apply_one(template: CombatantTemplate, award: CombatTreasureAward) -> None:
    if award.effect == "weapon-enhancement":
        _apply_weapon(template, award)
    elif award.effect == "armor-class":
        template.armor_class += award.bonus
    elif award.effect == "spell-focus":
        _apply_spell_focus(template, award)
    elif award.effect == "saving-throws":
        template.saving_throw_bonuses = {
            ability: value + award.bonus for ability, value in template.saving_throw_bonuses.items()
        }
    elif award.effect == "initiative":
        template.initiative_bonus += award.bonus
    elif award.effect == "speed":
        template.speed_ft += 5 * award.bonus
    elif award.effect == "max-hp":
        template.max_hp += 5 * award.bonus
    elif award.effect == "resource-use":
        _apply_resource(template, award)
    else:
        raise ValueError(f"Unsupported combat treasure effect: {award.effect}.")
    template.combat_treasure_awards.append(award)


def apply_combat_treasure_history(
    base_template: CombatantTemplate,
    awards: list[CombatTreasureAward],
) -> CombatantTemplate:
    """Apply only the strongest award in each equipment slot to avoid bonus stacking."""
    selected: dict[str, CombatTreasureAward] = {}
    for award in awards:
        current = selected.get(award.slot)
        if current is None or (award.bonus, award.level) > (current.bonus, current.level):
            selected[award.slot] = award
    result = base_template.model_copy(deep=True)
    result.combat_treasure_awards = []
    for award in sorted(selected.values(), key=lambda item: (item.level, item.slot)):
        _apply_one(result, award)
    return result
