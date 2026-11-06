"""Source proof for 2014 optional instead-of-damage grapple (Vampire family)."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_source_monsters_2014
from app.content.monster_source_optional_instead_grapple_2014 import (
    source_proves_optional_instead_grapple_2014,
)
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014

logger = logging.getLogger(__name__)

def test_vampire_family_source_proof_and_mutation_fail_closed() -> None:
    try:
        monsters = {m.id: m for m in load_source_monsters_2014()}
        vampire = monsters["vampire"]
        spawn = monsters["vampire-spawn"]
        vamp_attack = next(a for a in vampire.attacks if "Unarmed" in a.name)
        spawn_attack = next(a for a in spawn.attacks if a.name == "Claws")
        assert source_proves_optional_instead_grapple_2014(vampire, vamp_attack)
        assert source_proves_optional_instead_grapple_2014(spawn, spawn_attack)
        completed = source_completed_mixed_attack_2014(vampire, vamp_attack)
        assert completed.source_complete
        assert completed.control_effect is not None
        assert completed.control_effect["grapple_escape_dc"] == 18
        assert completed.control_effect.get("optional_instead_of_damage") is True
        # Mutation fails closed
        mutated = vamp_attack.model_copy(update={"unsupported_text": "Instead of dealing damage, it can grapple (escape DC 18) and deal extra."})
        assert not source_proves_optional_instead_grapple_2014(vampire, mutated)
        # Rename preserves
        renamed = vampire.model_copy(update={"name": "Blood Lord"})
        assert source_proves_optional_instead_grapple_2014(renamed, vamp_attack)
    except Exception:
        logger.exception("Optional instead-grapple source proof failed.")
        raise
