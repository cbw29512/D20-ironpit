---
name: iron-pit-completion
description: "Drive Iron Pit to completion. Use when advancing D20-ironpit: finishing universal engine capabilities, unlocking remaining 2014 monsters, or certifying pregen levels. Never weaken rules fidelity."
type: workflow
lifecycle: active
---

# Iron Pit Completion

Rules-first D&D 2024 / SRD 5.2.1 combat sim (`cbw29512/D20-ironpit`). Engine owns behavior; cards own immutable parameters. Unsupported mechanics fail closed. Python is the oracle; browser is production. Parity required.

## Locked priority

1. Finish remaining universal engine capabilities.
2. Unlock remaining 2014 monsters in source-approved semantic families (audited batches).
3. Certify remaining pregen levels the same way.
4. Do not raise card counts by weakening rules, inventing behavior, or special-casing names.

## Start of session

1. Run the existing context-transfer skill (`.agents/skills/iron-pit-context-transfer/SKILL.md`).
2. Read: `SOUL.md` → `docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md` → one lane guide (Monsters / Pregens / Universal Engine).
3. Fetch exact `main` SHA, open PRs, `docs/MONSTER_BLOCKERS_2014.md`, `docs/UNIVERSAL_MECHANIC_INVENTORY.md`, and current `docs/MONSTER_ABILITY_WORK_QUEUE.md`.
4. Search open + closed PRs for the chosen family before writing code. Reuse or resume existing work.

## One-family loop

1. Select one source-approved semantic family that clears the most remaining exact obligations (2014 first).
2. Map: trigger → eligibility → action/resource → attack/save → ordered effects → state → reset. Reuse existing Python + browser primitives. Parameterize differences in source data.
3. If a genuine missing semantic exists, park the single blocker and continue the family. Never invent.
4. Implement once, bind every matching card, add permanent parity tests (including synthetic/homebrew).
5. Run focused tests while editing. Regenerate owning artifacts once on the intended final head.
6. Require all applicable CI gates green on that exact head SHA. Intermediate green is not certification.
7. Merge, refresh generated blockers/inventory, record remaining gap in the existing queue only.

## Non-negotiables

- No name/class/monster-id dispatch.
- Source cards immutable; only temporary fight state mutates and fully resets.
- Step / Watch / Replay / Turbo share the same resolver.
- Audit is evidence-only.
- Production is browser-only.
- One subsystem owner; one family per PR.
- Reconcile existing PRs; do not duplicate.

## Authorities

- `SOUL.md` — philosophy
- `AGENTS.md` — coordination and gates
- `docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md` — execution
- `docs/UNIVERSAL_CARD_COMBAT_CONTRACT.md` — card contract
- `docs/MONSTER_ABILITY_WORK_QUEUE.md` — live monster queue
- `.agents/skills/iron-pit-context-transfer/SKILL.md` — handoff

Repository truth beats chat memory. Rebuild status from current SHA and generated reports every session.
