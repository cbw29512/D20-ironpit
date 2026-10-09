# D20 Iron Pit — SOUL

This file is the first-read architecture rule for every agent and contributor working on Iron Pit.

## Core principle

**The engine models what an effect does, not what the source calls it.**

Printed names exist for cards, player-facing logs, source provenance, audits, and certification. They are not combat-dispatch keys. A source-specific ability is still a real ability and must be preserved exactly on its monster, pregen, item, spell, or homebrew source even when no engine capability shares its name.

A class feature, subclass feature, feat, spell, item, monster trait, legendary action, lair action, or homebrew ability must be decomposed into universal mechanics before implementation.

Examples of universal identity:

- Prone is Prone.
- Grappled is Grappled.
- Restrained is Restrained.
- Blinded is Blinded.
- Charmed is Charmed.
- Frightened is Frightened.
- Poisoned is Poisoned.
- Advantage is Advantage.
- Disadvantage is Disadvantage.
- Resistance is Resistance.
- Immunity is Immunity.
- Vulnerability is Vulnerability.
- Damage is typed damage.
- Healing is healing.
- A saving throw is a saving throw.
- An attack roll is an attack roll.
- A resource is a resource.
- Recharge is recharge.
- Movement is movement.
- A buff/debuff is semantic state plus timing and qualifiers.

The source supplies parameters such as ability name, source id, ruleset, AC, DC, save ability, attack bonus, damage dice/type, range, duration, target count, timing, recharge threshold, resource limits, qualifiers, and logging text.

**The engine supplies behavior. The source supplies the exact numbers and facts.**

**Source-declared precombat buffs are authoritative.** If a printed combatant stat block explicitly says certain spells have been cast before combat, apply **all of those spells** as active pre-initiative buffs through the universal precombat state pipeline; do not erase source facts with the discretionary one-opening-buff selection. The 2014 Archmage specifically starts with Mind Blank, Stoneskin and Mage Armor. Respect the normal spells' Concentration, durations and resource costs; printed source pre-casts do not authorize an additional discretionary opening buff. This is an explicit user-approved product rule (2026-10-08); §7.1 of `docs/IRON_PIT_RULES_CONTRACT.md` owns the exact semantics. Implement by source-declared buff data, not by names in the engine.

Examples: the engine defines what Prone does, but the source decides whether an effect applies Prone and with what save/DC/duration. The engine defines attack-roll-versus-AC behavior, but the combatant source supplies AC and attack bonus. The engine defines typed damage resolution, but the source supplies the damage dice, bonus, type, and qualifiers.

## Mandatory planning queue anti-repeat gate

The generated blocker list is a **code-readiness inventory**, not a list of new user questions. The 2014 planning control file is `data/monster_2014_review_state.json`, and `scripts/monster_2014_review_queue.py` selects the next outstanding *source audit* separately from explicitly recorded open *user questions*. Before asking the user to decide a behavior, check previously confirmed source rulings, the worksheet, universal inventory and pending/merged PRs. **Never ask the user to approve a rule already settled**, even if a related PR has not merged, CI has failed, or the baseline blocker is still present. A printed source clause that already determines the effect should be documented as an implementation recipe and not escalated as a question.

Progress must only increase: when a monster/ability is source-reviewed and the implementation route is known, mark planning decision complete, preserve that decision in the ledger, and advance. Maintain a separate implementation/certification status; **hourly implementation remains disabled until the entire planning pass is closed and the user authorizes it**. Do not reset the cursor from the 124-monster historical list. One monster ability at a time; no redundant image work or unrelated checks.

## Mandatory implementation sequence

Before writing any combat mechanic:

1. Ignore the printed name temporarily.
2. Describe the exact RAW behavior.
3. Break it into trigger/timing, action/resource cost, attack/check/save, damage/healing, condition/state change, range/geometry, duration, movement, recharge/use limit, and lifecycle/reset.
4. Consult `docs/UNIVERSAL_MECHANIC_INVENTORY.md`, then search both hero and monster implementations for equivalent behavior.
5. Reuse an existing universal primitive whenever semantics match.
6. Parameterize differences in source data.
7. Compose multi-effect abilities from existing primitives.
8. If exact behavior cannot be represented, park the affected content and record the missing semantic/RAW question. Do not invent behavior during the content pass.
9. Finish the current family/pass, then return to confirmed engine gaps as deliberate technical debt.
10. Add a new universal primitive only when the reuse/composition search proves the existing engine cannot represent the behavior accurately.
11. Keep the exact printed source name in player logs and source/audit records.
12. Re-audit pregens and monsters after widening a primitive so all equivalent content can bind to it.
13. Regenerate the universal mechanic inventory so resolved demand disappears and newly reusable capability IDs are visible to monster, pregen, and future homebrew work.

## Forbidden architecture

Do not add combat behavior that dispatches on:

- class name or class id;
- subclass name or subclass id;
- monster name or monster id;
- spell name;
- feature/ability name;
- hero identity;
- presentation text.

Those identifiers may select content or source data, but they must not decide how a universal combat mechanic resolves.

Do not create a second resolver because a differently named source produces the same mechanical outcome.

Do not copy same-name 2014 and 2024 behavior across editions without source evidence. Edition source data stays isolated even when both editions bind to the same universal primitive.

Do not invent or backport combat capability for a source creature that explicitly has no effective attack or combat action. Keep the source record in the audit corpus and classify it `ARENA_NEUTRAL`/non-runnable unless product policy explicitly removes it.

## Universal runtime model

Combat behavior follows:

`checks -> modifiers -> result -> state update -> audit event`

Source templates/cards are immutable. Fight mutation belongs only to temporary combat state.

Python is the rules-reference/certification oracle. Browser JavaScript is the production fight engine. A capability is not supported until the required Python/browser behavior is equivalent and permanently tested.

Unsupported outcome-changing mechanics fail closed.

## Homebrew requirement

Future homebrew cards use the same engine. `docs/UNIVERSAL_MECHANIC_INVENTORY.md` is the first lookup surface: preserve the complete source ability, select one or more supported universal mechanic IDs for every behavior they can represent, then supply source-specific parameters and the printed homebrew name. If a source ability such as a unique monster attack has no matching printed name in the engine, that is normal: the source ability remains source-specific. If part of its actual behavior cannot be represented by existing primitives, add the smallest reusable universal primitive for that genuinely new semantic remainder, then bind the source ability to it. Never omit, rename, weaken, or approximate a source ability merely because the engine has no same-named capability.

## Authority

This file defines the product philosophy and semantic-engine rule. Day-to-day implementation starts at `docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md` and exactly one small task guide. Detailed rules remain in:

- `docs/IRON_PIT_RULES_CONTRACT.md`
- `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
- `docs/COMBAT_RESOLUTION_PIPELINE.md`
- `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
- `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
- `docs/TWO_AGENT_COORDINATION.md`

When implementation conflicts with this principle, refactor the implementation rather than creating another source-specific exception.
