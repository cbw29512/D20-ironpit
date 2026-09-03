import pytest

from app.content.armor_catalog import ARMOR_CATALOG, get_armor


def test_shared_armor_catalog_includes_druid_medium_armor() -> None:
    scale = get_armor("scale-mail")
    assert (scale.name, scale.category, scale.base_ac) == ("Scale Mail", "medium", 14)
    assert set(ARMOR_CATALOG) == {"chain-mail", "scale-mail", "studded-leather"}


def test_unknown_armor_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown audited armor"):
        get_armor("not-armor")
