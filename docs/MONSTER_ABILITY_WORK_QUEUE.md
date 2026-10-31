# D20 Iron Pit — single operational monster ability queue (2014 first)

## Shapechanger semantic family — source contract foundation 2026-10-30

- Highest-yield remaining source:trait family not covered by a general open PR (11 monsters: Doppelganger, Imp, Mimic, Quasit, Succubus/Incubus, Vampire, Werebear, Wereboar, Wererat, Weretiger, Werewolf). Specific foundations exist for Doppelganger only.
- Source-proven common contract: Action to polymorph into a listed form or true form; statistics other than size identical; equipment not transformed; reverts on death.
- Reuses existing ReplacementFormAction / enter_replacement_form primitives (hp_mode=retain_owner, action cost). No name dispatch.
- Permanent source regressions added. Form-specific attacks, size-sensitive rules, lycanthrope Multiattack, and full Python/browser combat wiring remain independently blocked. No monster admission claimed. Production remains locked. Regenerate owned artifacts only after exact-head CI on a complete wiring head.

## Surprise-opening attack modifiers — implementation 2026-10-29

- The mandatory source-semantic scan covers all 327 immutable cards and finds two applicable cards: Bugbear and Doppelganger. It does not route on monster or trait name.
- Both cards' printed Surprise Attack dice and damage type are bound to the existing first-round initiative-lead hit rider. Doppelganger's separate printed Ambusher clause now grants attack Advantage through the same fight-local opening window in Python and browser.
- Generator-owned `docs/generated/SURPRISE_OPENING_BINDINGS_2014.json`: 327 scanned; 2 applicable; 2 Python wired; 2 browser wired; zero remaining; zero exceptions.
- Bugbear remains source-admitted. Doppelganger's Ambusher and Surprise Attack obligations are cleared, while its independent Shapechanger Action/trait remains explicitly blocked; no admission is claimed. Production remains locked.

## Recharge save-for-half typed damage — implementation 2026-10-29

- The mandatory semantic scan covers all 327 immutable cards and finds 30 direct Recharge Actions whose complete printed outcome is typed damage on a failed save and half on success.
- All 30 are wired in Python and browser with source-declared save ability/DC, range/area, damage dice/type, half-damage outcome, Recharge threshold and one-use resource. Behir's previously missing Lightning Breath binding adds its exact 20-by-5-foot line, DC 16 Dexterity save, 12d10 Lightning damage and Recharge 5–6 without monster-name runtime dispatch.
- Generator-owned `docs/generated/RECHARGE_SAVE_HALF_DAMAGE_BINDINGS_2014.json`: 327 scanned; 30 applicable; 30 Python wired; 30 browser wired; zero remaining; zero exceptions.
- Behir's `mechanic:recharge` blocker is removed. The simple grapple-then-Swallow profile is now wired for Giant Frog and Giant Toad in Python and browser, raising source admission to 250/327. The 327-card semantic scan finds 8 applicable Swallow/Engulf cards: 2 wired and 6 explicitly blocked by missing structured parameters or distinct failed-save, regurgitation, or Engulf profiles. Behir's printed Swallow remains fail-closed under `source:extra-action`. Production remains locked.

## End-turn recurring typed damage — source-data blocker recorded 2026-10-29

- The mandatory semantic scan covers all 327 immutable cards and finds one applicable card: Magmin Touch.
- The card supplies hit application, 1d6 Fire, target-turn-end timing, and an Action exit. It does not supply the grid range for a different creature taking that douse Action; Iron Pit does not copy the 5-foot Wake Sleeper range or invent another value.
- Generator-owned `docs/generated/END_TURN_RECURRING_DAMAGE_BINDINGS_2014.json`: 327 scanned; one applicable; zero Python wired; zero browser wired; one remaining; one explicit missing-data exception.
- PR #1096's Python-only synthetic lifecycle is not integration evidence and must not merge without resolving this source gap, binding Python/browser together, and regenerating this report. Production remains locked.

## Sleep spell semantic family — source-data blocker recorded 2026-10-28

- The mandatory semantic scan covers all 327 immutable 2014 monster cards and finds four applicable cards: Dust Mephit, Night Hag, Oni, and Spirit Naga.
- The cards declare Sleep access and their per-day or prepared-spell access, but omit the spell's effect payload: range, area, hit-point-pool dice, duration, damage/wake exits, and creature/condition exclusions. Those values are not inferred from monster or spell names.
- The existing shared Python/browser Unconscious lifecycle, damage exit, and explicit `wake-sleeper` Action are reusable evidence from the certified Brass Dragon Sleep Breath family, but they are not a substitute for the missing spell payload or a complete Sleep cast action.
- Generator-owned `docs/generated/SLEEP_BINDINGS_2014.json`: 327 scanned; 4 applicable; 0 Python wired; 0 browser wired; 4 remaining; 4 explicit missing-data exceptions. Ingest a pinned 2014 spell source before binding all four cards together.
- No monster admission, runtime mechanic, or finished fight is claimed. Production remains locked.
