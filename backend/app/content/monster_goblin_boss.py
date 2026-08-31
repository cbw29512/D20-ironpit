from __future__ import annotations

import logging

from app.content.attacks import build_goblin_scimitar_attack, build_goblin_shortbow_attack
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.reactions import RedirectAttackReaction

logger = logging.getLogger(__name__)


def build_goblin_boss() -> CombatantTemplate:
    try:
        scimitar = build_goblin_scimitar_attack().model_copy(update={"id": "goblin-boss-scimitar"})
        shortbow = build_goblin_shortbow_attack().model_copy(update={"id": "goblin-boss-shortbow"})
        choices = [scimitar.id, shortbow.id]
        return CombatantTemplate(
            id="srd-goblin-boss", name="Goblin Boss", archetype="Goblin Boss", challenge_rating="1",
            kind="monster", size="small", armor_class=17, max_hp=21, speed_ft=30, initiative_bonus=2,
            weapon_attack=scimitar, alternate_weapon_attacks=[shortbow],
            attack_action=AttackActionDefinition(
                id="goblin-boss-multiattack", name="Multiattack",
                slots=[AttackActionSlot(attack_ids=choices), AttackActionSlot(attack_ids=choices)],
            ),
            redirect_attack_reaction=RedirectAttackReaction(),
            visual=VisualLoadout(
                armor="chain-shirt", main_hand="scimitar", off_hand="shield", body_style="goblinoid",
            ),
            source="SRD 5.2.1 p. 290",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Goblin Boss.")
        raise RuntimeError("Goblin Boss could not be created.") from exc
