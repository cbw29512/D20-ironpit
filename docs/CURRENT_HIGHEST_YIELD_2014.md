# Current highest-yield remaining 2014 source blocker

Generated 2026-10-31 from current main blockers and open PRs.

## Selected family

**source:trait Shapechanger** (11 remaining unbound after Imp/Quasit open PRs).

Not already in an open implementation PR for the remaining monsters (lycanthropes, Doppelganger, Mimic, Succubus/Incubus, Vampire).

## Rationale

- Largest single category: source:trait at 61 monsters.
- Shapechanger is the most common unbound trait (11).
- Imp and Quasit have open PRs (#1137, #1138, #1143) for arena-neutral classification.
- Other foundation PRs exist (#1103 Doppelganger) but no focused source-verified arena-neutral for the rest.

## Next action

Source-verify each full Shapechanger paragraph against pinned 2014 text. Classify as arena-neutral only when exact text proves movement/appearance-only with identical combat statistics (reuse existing verified_arena_inert_trait_2014 pattern). Fail-closed on any mutation. No name dispatch. Regenerate owned artifacts. Python/browser parity via existing form selection if combat-relevant. Do not claim admission until exact-head CI. Do not weaken fidelity.

Open PR collisions: #1103, #1137, #1138, #1143. Independent of those.

Next blocker after this family: remaining source:trait (Innate Spellcasting / Spellcasting) or source:extra-action.
