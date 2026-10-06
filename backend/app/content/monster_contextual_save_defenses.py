from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014, load_monster_source_2014
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.timed_self_buffs import TimedFriendlySaveAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
_SELF = re.compile(
    r"(?P<name>[^.\n]+)\. The [^.\n]+? has advantage on saving throws "
    r"against any effect that turns undead\.", re.IGNORECASE,
)
_FRIENDLY = re.compile(
    r"(?P<name>[^.\n]+)\. The [^.\n]+? and any (?P<recipients>[^.\n]+?) within "
    r"(?P<radius>\d+) feet of it have advantage on saving throws "
    r"against effects that turn undead\.", re.IGNORECASE,
)


def contextual_save_defenses_from_source(
    source_traits: object, ruleset: str, recipient_ids: dict[str, str] | None = None,
) -> tuple[list[TimedSelfBuffAction], list[SavingThrowAdvantageGrant]]:
    """Bind mechanical save clauses; headings remain source/log labels only."""
    try:
        if ruleset not in {"2014", "2024"}:
            raise ValueError("Contextual save intake requires an explicit supported ruleset.")
        # Paragraph boundaries prevent an unpunctuated spell list becoming part
        # of the next trait's printed name.
        text = re.sub(r"</p>", "\n", str(source_traits or ""), flags=re.IGNORECASE)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        text = re.sub(r"[^\S\n]+", " ", text).strip()
        text = re.sub(r"\s+\.", ".", text)
        actions, grants = [], []
        for match in _SELF.finditer(text):
            name = match.group("name").strip()
            grants.append(SavingThrowAdvantageGrant(
                source_id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
                source_name=name, abilities=_ABILITIES, required_effect_tags=["turning"],
            ))
        for match in _FRIENDLY.finditer(text):
            name = match.group("name").strip()
            recipient = match.group("recipients").casefold()
            target_id = (recipient_ids or {}).get(recipient)
            if target_id is None:
                raise ValueError(f"No source-derived recipient binding for {recipient!r}.")
            actions.append(TimedSelfBuffAction(
                id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"), name=name,
                activation_timing="passive", expiry_timing=None,
                friendly_save_advantage_aura=TimedFriendlySaveAura(
                    radius_ft=int(match.group("radius")), required_effect_tags=["turning"],
                    target_template_ids=[target_id], includes_source=True, recipient_scope="all",
                    covers_arena=int(match.group("radius")) == 30,
                ),
                animation="buff",
            ))
        ids = [item.id for item in actions] + [item.source_id for item in grants]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate contextual save-defense identities.")
        return actions, grants
    except Exception:
        logger.exception("Failed %s contextual save-defense source intake.", ruleset)
        raise


def contextual_save_defenses_2014(monster: SourceMonster2014):
    try:
        # Printed species eligibility is source data; the runtime only compares
        # declared template IDs, never a monster or feature display name.
        recipients = {f"{row.name.casefold()}s": f"2014-{row.id}" for row in load_monster_source_2014()}
        return contextual_save_defenses_from_source(monster.source_traits, "2014", recipients)
    except Exception:
        logger.exception("Failed contextual save-defense binding for %s.", monster.name)
        raise
