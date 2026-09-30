# 2014 audit repair — website and shared-engine parity

Base: main `d64f549ea7b3de3ff5776fd0f6070691801b7047`, 2026-09-30.

## Scope and state map

| Finding | Immutable data / schema | Python reference | Website runtime | Lifecycle / evidence |
|---|---|---|---|---|
| Unseen Power Word targets | HP-threshold `requires_target_sight`; 2014 source bindings | threshold legality consumes `can_see` | generated `requiresTargetSight`, threshold legality consumes `canSee` | No action/resource spending on rejected target; permanent visibility/HP/resource tests |
| Sanctuary duration | Defensive spell `duration_minutes` and modifier payload | spell modifiers register an existing timed source group | spell modifiers register the same timed group | source-turn-start expiration removes only that source/effect group; opening and in-combat boundary tests; fresh-state reset |
| High-level action starvation | explicit Arena category policy | early threshold selection and extracted post-move Action module | `signatureThreshold` selector opportunity and post-move category order | after urgent support, before optional Bonus Action spell setup; real-turn Kill rather than Hex/cantrip |
| Standalone test drift | website module order used by fixture loader | existing reference checks retained | nine repaired standalone tests added to CI | Charge mock emits valid event identity; save mock has required dependencies; damage dice cover both greatsword dice and Savage Attacker reroll; cleric self-rider isolated without removing recipient checks |
| Root HTML drift | frontend remains the authoritative website entry | not applicable | identical module list in root and frontend | permanent equality and initialization tests for both entry points |

## Source evidence

- [2014 Power Word Kill](https://www.dndbeyond.com/spells/2210-power-word-kill)
- [2014 Power Word Stun](https://www.dndbeyond.com/spells/2211-power-word-stun)
- [2014 Sanctuary](https://www.dndbeyond.com/spells/2237-sanctuary)

Visibility and modifier expiration reuse existing universal primitives. The Action-family priority change is an explicit Arena policy correction, not a change to printed spell rules. No new class, spell, monster, or source-name resolver was added.

The Druid 10 fixture had an obsolete expectation for a spell-package overlay not exported by the legacy 2014 card. It now verifies actually compiled Cure Wounds and Freedom of Movement, retaining the complete Nature's Ward immunity/counter assertions. This does not certify Scrying or claim a new prepared-spell implementation.

## Verification

- Full Python suite: 1,999 passed after the refactor and six new regressions (188.01 seconds).
- All 201 standalone browser test files pass, including all nine audited failures and the new website-entry/RAW regression.
- Real browser engine in Node: all 240 heroes against four certified monsters, 960 encounters per HTML entry point, zero exceptions for either page.
- Source-size, browser syntax (183 JavaScript files), capability coverage, registry freshness, checklist freshness, and certification/static regeneration passed locally. Backend-free production, GitHub Pages root-entry, and Netlify-lock checks passed. Exact-head GitHub CI is still required.
- Certified roster is still 240/240 heroes and 129/327 monsters for 2014; 116/240 heroes and 140/330 monsters for 2024 at this base.

The encounter probes execute production browser modules in Node. They do not constitute a DOM interaction test or inspection of the deployed site. Netlify's publish directory is frontend, and its autopublish lock is unchanged. No production deployment is included.

## Other active work

PR #472 belongs to the other window's Druid 17 lane. This branch contains no Druid progression, Foresight, or initiative/Death Save changes. Shared exporter and workflow files have independent additions, and generated data must be regenerated when reconciling either merge order. Re-anchor and run exact-head checks after main changes; do not copy verification across heads.
