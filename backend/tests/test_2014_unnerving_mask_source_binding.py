from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_turn_start_reaction_2014 import source_turn_start_reaction_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014


def test_chain_devil_unnerving_mask_source_compiles() -> None:
    source = next(m for m in load_monster_source_2014() if m.id == "chain-devil")
    rule = source_turn_start_reaction_2014(source)
    assert rule is not None
    assert rule.range_ft == 30
    assert rule.save_ability == "wisdom" and rule.save_dc == 14
    assert "source:reaction" not in basic_blockers_2014(source)
    template = compile_combatant(adapt_basic_monster_2014(source))
    assert template.turn_start_save_reaction == rule


def test_modified_source_does_not_silently_certify() -> None:
    source = next(m for m in load_monster_source_2014() if m.id == "chain-devil")
    altered = source.model_copy(update={"source_reactions": ""})
    assert source_turn_start_reaction_2014(altered) is None
    assert "source:reaction" in basic_blockers_2014(altered)
