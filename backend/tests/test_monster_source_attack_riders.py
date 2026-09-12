from app.content.monster_source_attack_riders import parse_attack_riders


def test_charge_conditioned_prone_is_not_promoted_to_unconditional_hit_rider() -> None:
    text = (
        "If the target is Medium or smaller and the boar moved 20+ feet straight toward "
        "it immediately before the hit, the target has the Prone condition."
    )

    effects = parse_attack_riders(text)

    assert all(effect.kind != "prone" for effect in effects)


def test_unconditional_prone_still_compiles_as_hit_rider() -> None:
    effects = parse_attack_riders("The target has the Prone condition.")

    assert [effect.kind for effect in effects] == ["prone"]
