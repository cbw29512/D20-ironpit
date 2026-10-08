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
    ready_cards = ready_heroes | ready_monsters
    blocked_heroes = [card_id for card_id in selection.hero_ids if card_id not in ready_cards]
    blocked_monsters = [card_id for card_id in selection.monster_ids if card_id not in ready_cards]
    if blocked_heroes:
        raise ValueError(f"Team A cards are not RAW-certified for public fights: {blocked_heroes}")
    if blocked_monsters:
        raise ValueError(f"Team B cards are not RAW-certified for public fights: {blocked_monsters}")
