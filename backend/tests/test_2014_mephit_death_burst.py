"""Source-prove 2014 Mephit/Magmin Death Burst family to existing death-trigger primitive."""
from app.content.monster_source_2014 import load_source_monsters_2014
from app.content.monster_death_triggers_2014 import death_trigger_actions_2014, supports_death_triggers_2014


def test_mephit_family_death_burst_source_bound():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    for mid in ("dust-mephit", "ice-mephit", "magma-mephit", "steam-mephit", "magmin"):
        monster = monsters[mid]
        assert supports_death_triggers_2014(monster)
        actions = death_trigger_actions_2014(monster)
        assert len(actions) == 1
        assert actions[0].name == "Death Burst"
        # Fail closed on mutation
        mutated = monster.model_copy(update={"source_traits": monster.source_traits.replace("dies", "lives")})
        assert not supports_death_triggers_2014(mutated)
