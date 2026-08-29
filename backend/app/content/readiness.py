from __future__ import annotations

from app.content.catalog import build_full_content_catalog
from app.domain.encounters import EncounterSelection


def assert_public_selection_runnable(selection: EncounterSelection) -> None:
    """Reject direct API attempts to run catalog cards that are not certified."""
    catalog = build_full_content_catalog()
    ready_heroes = {
        card.runnable_template_id
        for card in catalog.heroes
        if card.runnable_template_id is not None
    }
    ready_monsters = {
        card.runnable_template_id
        for card in catalog.monsters
        if card.runnable_template_id is not None
    }
    blocked_heroes = [card_id for card_id in selection.hero_ids if card_id not in ready_heroes]
    blocked_monsters = [card_id for card_id in selection.monster_ids if card_id not in ready_monsters]
    if blocked_heroes:
        raise ValueError(f"Hero cards are not RAW-certified for public fights: {blocked_heroes}")
    if blocked_monsters:
        raise ValueError(f"Monster cards are not RAW-certified for public fights: {blocked_monsters}")
