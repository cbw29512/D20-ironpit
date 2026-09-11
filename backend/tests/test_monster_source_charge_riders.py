from app.content.monster_source_charge_riders import parse_charge_replacement
from app.domain.size import CreatureSize


def test_movement_gated_prone_charge_is_source_driven() -> None:
    profile = parse_charge_replacement(
        "If the target is a Huge or smaller creature and the beast moved 20+ feet straight toward it "
        "immediately before the hit, the target has the Prone condition."
    )
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.prone_max_target_size == CreatureSize.HUGE
    assert profile.replacement_damage is None
