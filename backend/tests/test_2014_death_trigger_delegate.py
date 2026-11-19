"""Passive death triggers reuse saving throws without spending an Action."""
from types import SimpleNamespace

from app.combat import death_trigger_save
from app.content.monster_death_trigger_saves_2014 import DeathTriggeredSave
from app.domain.actions import SavingThrowAction


def test_dead_source_uses_shared_save(monkeypatch) -> None:
    source = SimpleNamespace(combatant_id="a", state=SimpleNamespace(is_dead=True, current_hp=0))
    target = SimpleNamespace(combatant_id="b", state=SimpleNamespace(is_dead=False))
    rule = DeathTriggeredSave(
        source_id="pulse", source_name="Synthetic Pulse",
        save_action=SavingThrowAction(
            id="pulse", name="Synthetic Pulse", save_ability="dexterity", dc=10, range_ft=5,
        ),
    )
    seen = []
    def shared(*args, **kwargs):
        seen.append(kwargs)
        return "event"
    monkeypatch.setattr(death_trigger_save, "resolve_save_action", shared)
    assert death_trigger_save.resolve_death_trigger_save(1, 1, source, target, rule, 5, None, None) == "event"
    assert seen == [{"spend_action": False, "check_resource": False, "spend_resource": False, "setup": None}]
