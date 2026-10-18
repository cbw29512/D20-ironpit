# Iron Pit — mandatory session continuity contract

This is a **handoff entry point**, not a competing rules ledger. Read this before any coding, automation run, or response to "go", "next", "keep going", or "finish monsters".

## Non-negotiable architecture (already decided; DO NOT ask again)
- **Engine = universal D&D combat semantics. Cards = immutable data, triggers, values, and effect definitions.**
- A monster name is only a label or source identifier. **Never dispatch runtime behavior by monster name.** Do not implement bespoke Basilisk, Medusa, Erinyes, etc. engine branches.
- The card specifies DC, damage, HP, AC, range, ability, targeting, duration, trigger, outcome, resource amounts, and condition/effect parameters. Universal mechanics resolve hit/save/damage/buff/debuff/condition/immunity/timing/reaction/death.
- Preserve the established Iron Pit exceptions in the locked rules; 2014 first, then 2024. Petrified is immediate defeat in the Pit. Do not ask to reconsider settled design unless incompatible source facts require a genuinely new ruling.
- New monsters and homebrew should compose the existing mechanics without engine changes when their effects already exist.

## Required execution order, every session
1. Read [SOUL](../SOUL.md), [implementation playbook](IRON_PIT_IMPLEMENTATION_PLAYBOOK.md), [monster playbook](playbooks/MONSTERS.md), [locked rules](IRON_PIT_LOCKED_RULES.md), [canonical monster queue](MONSTER_ABILITY_WORK_QUEUE.md), [generated blockers](MONSTER_BLOCKERS_2014.md), and [mechanic inventory](UNIVERSAL_MECHANIC_INVENTORY.md).
2. Inspect **live main**, relevant existing PR branches/heads, and exact-head CI. Generated data and current repo state override old chat summaries and historical numbers.
3. **Do implementation work**, not another architecture explanation. Select approved unfinished semantic families that can finish the most monsters. Avoid PR overlap; finish existing branches and tests before opening unrelated work.
4. Bind immutable card facts to universal primitives. Write positive, negative and mutation tests for source proof; Python/browser combat parity; regenerate generated artifacts using their scripts.
5. Do not merge without exact-head required gates. Keep production Netlify publishing locked; beta preview separate.
6. Report **verified** merged monster completions, source-admitted count vs truly battle-certified status, remaining blockers, commit/PR, CI evidence, and exact unresolved blocker. Do not claim progress from discussions, plans, commits, or a draft PR alone.

## Previously settled example — gaze is NOT a new design discussion
- Basilisk and Medusa use a **single universal gaze-trigger + sight/eye-aversion + save + timed Restrained-to-Petrified effect grammar**, parameterized by their source cards. Medusa's initial failure by 5+ causes immediate Petrified. Check source and canonical queue for complete details; do not invent or simplify missing mechanics.
- Poison/Poisoned is distinct from petrification. Never describe gaze as requiring a new monster-specific condition handler.

## Durable ownership
- Architecture: [SOUL](../SOUL.md) and [universal card-to-combat contract](UNIVERSAL_CARD_COMBAT_CONTRACT.md).
- Product exceptions: [locked rules](IRON_PIT_LOCKED_RULES.md).
- Prior decisions, execution cursor and current approved queue: [monster ability work queue](MONSTER_ABILITY_WORK_QUEUE.md).
- Generated measured status: [monster blocker report](MONSTER_BLOCKERS_2014.md), [universal mechanic inventory](UNIVERSAL_MECHANIC_INVENTORY.md). **Never hand-edit generated outputs.**
- Tests + exact-head GitHub Actions = certification evidence, not conversational recollection.

If another chat lacks context, **recover it from this repository before answering or editing**. The user should not have to repeat the architecture again.
