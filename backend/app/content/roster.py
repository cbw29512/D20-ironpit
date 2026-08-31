from __future__ import annotations

import logging

from app.content.certified_heroes import build_certified_hero_templates
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.monster_bonus_action_source_audit import complete_monster_bonus_action_fingerprints
from app.content.monster_hippogriff import build_hippogriff
from app.content.monster_legendary_source_audit import complete_monster_legendary_fingerprints
from app.content.monster_limited_use_source_audit import complete_monster_limited_use_fingerprints
from app.content.monster_reaction_source_audit import complete_monster_reaction_fingerprints
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_spellcasting_source_audit import complete_monster_spellcasting_fingerprints
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.content.monster_tyrannosaurus import build_tyrannosaurus_rex
from app.content.monsters import build_axe_beak, build_bandit, build_commoner, build_giant_lizard
from app.content.monsters_bears import build_black_bear, build_brown_bear
from app.content.monsters_batch_three import build_monster_batch_three
from app.content.monsters_beast_batch_two import build_beast_batch_two
from app.content.monsters_charge import build_boar, build_elk, build_giant_boar
from app.content.monsters_control import build_control_monsters
from app.content.monsters_fixed_damage import build_fixed_damage_monsters
from app.content.monsters_humanoid_expansion import build_goblin_minion, build_hobgoblin_warrior, build_kobold_warrior
from app.content.monsters_low_cr import build_giant_rat, build_giant_weasel, build_guard
from app.content.monsters_mixed_multiattack import build_giant_constrictor_snake
from app.content.monsters_poison import build_poison_monsters
from app.content.monsters_simple_beasts import build_baboon, build_camel, build_deer, build_draft_horse, build_giant_badger
from app.content.monsters_venom import build_venom_monsters
from app.content.monsters_wolves import build_dire_wolf, build_wolf
from app.content.movement_modes import complete_monster_movement_modes
from app.content.pregens import build_brom_ironmark, build_mara_quickstep, build_selene_asharrow
from app.domain.models import ArenaRoster

logger = logging.getLogger(__name__)


def build_arena_roster() -> ArenaRoster:
    try:
        monsters = [
            build_goblin_warrior(), build_goblin_minion(), build_hobgoblin_warrior(), build_kobold_warrior(),
            build_bandit(), build_commoner(), build_guard(), build_giant_rat(), build_giant_weasel(),
            build_axe_beak(), build_giant_lizard(), build_wolf(), build_dire_wolf(),
            build_black_bear(), build_brown_bear(), build_baboon(), build_camel(), build_deer(),
            build_draft_horse(), build_giant_badger(), build_boar(), build_elk(), build_giant_boar(),
            build_hippogriff(), *build_fixed_damage_monsters(), *build_beast_batch_two(),
            *build_monster_batch_three(), *build_control_monsters(), *build_poison_monsters(),
            *build_venom_monsters(), build_giant_constrictor_snake(), build_tyrannosaurus_rex(),
        ]
        monsters = complete_monster_movement_modes(monsters)
        monsters = complete_monster_trait_fingerprints(monsters)
        monsters = complete_monster_reaction_fingerprints(monsters)
        monsters = complete_monster_bonus_action_fingerprints(monsters)
        monsters = complete_monster_limited_use_fingerprints(monsters)
        monsters = complete_monster_legendary_fingerprints(monsters)
        monsters = complete_monster_spellcasting_fingerprints(monsters)
        return ArenaRoster(
            characters=[
                *build_certified_hero_templates(),
                build_demo_fighter(),
                build_brom_ironmark(),
                build_selene_asharrow(),
                build_mara_quickstep(),
            ],
            monsters=complete_monster_saving_throws(monsters),
        )
    except Exception as exc:
        logger.exception("Failed to build Iron Pit arena roster.")
        raise RuntimeError("Arena roster could not be created.") from exc
