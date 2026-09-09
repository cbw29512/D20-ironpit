from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.models import DamageType

logger = logging.getLogger(__name__)


def test_xorn_exact_source_multiattack_and_traits() -> None:
    try:
        xorn = next(monster for monster in build_arena_roster().monsters if monster.name == "Xorn")
        attacks = {attack.weapon.name: attack for attack in [xorn.weapon_attack, *xorn.alternate_weapon_attacks]}
        bite = attacks["Bite"]
        claw = attacks["Claw"]

        assert (bite.attack_bonus, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (6, 4, 6, 3)
        assert bite.weapon.damage_type is DamageType.PIERCING
        assert (claw.attack_bonus, claw.weapon.dice_count, claw.weapon.dice_size, claw.damage_bonus) == (6, 1, 10, 3)
        assert claw.weapon.damage_type is DamageType.SLASHING
        assert xorn.attack_action is not None
        assert [slot.attack_ids for slot in xorn.attack_action.slots] == [
            [bite.id], [claw.id], [claw.id], [claw.id],
        ]
        assert "Earth Glide" in xorn.source_trait_names
        assert "Treasure Sense" in xorn.source_trait_names
        assert xorn.source_bonus_action_names == ["Charge"]

        row = next(row for row in load_monster_rows() if row["name"] == "Xorn")
        assert audit_monster_source(xorn, row) == []
    except Exception:
        logger.exception("Xorn exact-source certification regression failed.")
        raise
