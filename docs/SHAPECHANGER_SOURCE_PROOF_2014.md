# 2014 Shapechanger source proof (draft)

Highest-yield remaining semantic family not covered by open PRs (spellcasting #1074, Fire Aura #1075, Swallow #1066, Magmin #1067).

Affects: Doppelganger, Imp, Quasit, Succubus/Incubus, Werebear, Wereboar, Wererat, Weretiger, Werewolf (and others with form change).

Source-verified: printed Shapechanger is voluntary form change to specific creature types/sizes, with Action cost, equipment/stats rules per monster, reversion on death or action.

Reuse: existing universal tactical form selection (docs/UNIVERSAL_TACTICAL_FORM_SELECTION.md, draft #723) + form overlay primitives. No name dispatch. Parameterize eligible forms, costs, HP semantics from source cards.

Python/browser parity required before any admission. This PR is source analysis only; runtime binding and tests follow in focused follow-ups. Do not claim admission until exact-head CI.

Next blocker after this family: remaining source:trait (e.g. Air Form, Fire Form) or attack:incomplete.
