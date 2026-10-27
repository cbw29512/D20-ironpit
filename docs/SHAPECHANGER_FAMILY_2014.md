# 2014 Shapechanger semantic family foundation

Highest-yield remaining source-trait family not covered by open PRs (11 monsters: Doppelganger, Imp, Mimic, Quasit, Succubus/Incubus, Vampire, Werebear, Wereboar, Wererat, Weretiger, Werewolf).

## Source semantics (common)

Voluntary Action to polymorph into a source-legal form (or back), retaining personality/alignment/stats except physical, gaining form's physical capabilities. Reversion on death or 0 HP in some cases, or voluntary. No name dispatch; parameters from immutable source cards.

Reuse existing universal tactical form-selection evaluator (see docs/UNIVERSAL_TACTICAL_FORM_SELECTION.md) and form-state lifecycle. Do not invent new resolvers.

## Requirements before admission

- Source-verify exact printed form sets, CR limits, costs, HP/reversion rules per monster.
- Bind to shared Python/browser form change primitive with parity tests.
- Preserve fight-local state, reset, and fail-closed on unsupported forms.
- Regenerate owned artifacts; exact-head CI before any admission claim.

This foundation records the family selection. Implementation of specific bindings is follow-on work. Do not weaken fidelity or claim source admission until verified.
