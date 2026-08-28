from __future__ import annotations

import logging

from app.domain.rules import RuleCoverageEntry, RuleCoverageStatus, RulesCoverageReport

logger = logging.getLogger(__name__)
I = RuleCoverageStatus.IMPLEMENTED
P = RuleCoverageStatus.PARTIAL
U = RuleCoverageStatus.UNSUPPORTED
A = RuleCoverageStatus.ARENA_ASSUMPTION


def build_rules_coverage() -> RulesCoverageReport:
    try:
        entries = [
            RuleCoverageEntry(id="initiative", name="Initiative", status=I, notes="d20 plus Initiative modifier; rolls are recorded."),
            RuleCoverageEntry(id="attack-rolls", name="Weapon attack rolls", status=I, notes="AC checks, natural 1 misses, and natural 20 hits are implemented."),
            RuleCoverageEntry(id="critical-hits", name="Weapon critical hits", status=I, notes="A natural 20 doubles weapon and eligible conditional damage dice."),
            RuleCoverageEntry(id="advantage", name="Advantage and Disadvantage", status=I, notes="Multiple sources collapse using the normal cancellation rule."),
            RuleCoverageEntry(id="range", name="Weapon range", status=I, notes="Melee reach, normal range, long range, and close-ranged Disadvantage are implemented."),
            RuleCoverageEntry(id="movement", name="Movement", status=I, notes="Speed, closing distance, retreat movement, and remaining movement are tracked."),
            RuleCoverageEntry(id="dash", name="Dash", status=I, notes="Dash spends the Action and grants extra movement equal to Speed."),
            RuleCoverageEntry(id="hp-defeat", name="Hit Points and defeat", status=I, notes="Damage, healing, 0 HP defeat, and winner events are implemented for arena duels."),
            RuleCoverageEntry(id="second-wind", name="Fighter Second Wind", status=I, notes="Uses, Bonus Action cost, healing, and max-HP cap are implemented."),
            RuleCoverageEntry(id="sap", name="Longsword Sap", status=I, notes="Next-attack Disadvantage and start-of-source-turn expiry are implemented."),
            RuleCoverageEntry(id="vex", name="Vex mastery", status=I, notes="Target-specific next-attack Advantage through the end of the wielder's next turn is implemented for mastered weapons."),
            RuleCoverageEntry(id="goblin-advantage-damage", name="Goblin Advantage damage", status=I, notes="The Goblin Warrior's conditional d4 damage applies only when its attack has Advantage."),
            RuleCoverageEntry(id="opportunity-attacks", name="Opportunity Attacks", status=I, notes="Leaving melee reach can spend a Reaction for one melee attack before movement resolves."),
            RuleCoverageEntry(id="disengage", name="Disengage", status=I, notes="Disengage suppresses Opportunity Attacks for retreat movement during the current turn."),
            RuleCoverageEntry(id="reactions", name="Reactions", status=P, notes="Reaction availability and Opportunity Attacks are implemented; other Reaction features are not."),
            RuleCoverageEntry(id="nimble-escape", name="Goblin Nimble Escape", status=P, notes="Bonus Action Disengage and retreat are implemented; Hide is not yet implemented."),
            RuleCoverageEntry(id="nick", name="Nick mastery", status=U, notes="Requires a canonical Light-property extra-attack model before implementation."),
            RuleCoverageEntry(id="hide", name="Hide", status=U, notes="Requires concealment, visibility, and Stealth state."),
            RuleCoverageEntry(id="conditions", name="Conditions", status=U, notes="General condition rules are not implemented."),
            RuleCoverageEntry(id="cover", name="Cover", status=U, notes="Battlefield cover and line-of-effect rules are not implemented."),
            RuleCoverageEntry(id="spells", name="Spells", status=U, notes="Spellcasting is outside the current duel slice."),
            RuleCoverageEntry(id="death-saves", name="Death Saving Throws", status=U, notes="The arena currently treats 0 HP as defeat."),
            RuleCoverageEntry(id="initiative-ties", name="Initiative ties", status=A, notes="The arena currently uses Initiative bonus as its deterministic tie-breaker."),
            RuleCoverageEntry(id="arena-geometry", name="Arena geometry", status=A, notes="Current combat uses one-dimensional distance in an open arena and assumes opponents are visible."),
        ]
        return RulesCoverageReport(entries=entries)
    except Exception as exc:
        logger.exception("Failed to build rules coverage report.")
        raise RuntimeError("Rules coverage report could not be created.") from exc
