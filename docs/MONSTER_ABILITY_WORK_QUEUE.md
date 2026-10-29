# D20 Iron Pit — single operational monster ability queue (2014 first)

## Duergar Resilience — foundation 2026-10-29

- Source-verified 2014 Duergar: advantage on saving throws against poison, spells, and illusions, as well as to resist being charmed or paralyzed. Sunlight Sensitivity is arena-neutral (no sunlight context in Pit).
- Decomposed to universal save Advantage sources for specific damage/condition/spell categories. Reuse existing `save_advantage_sources` in Python/browser saving throw resolution. No name dispatch.
- Does not clear blockers or admit Duergar (still has attack:incomplete, source:extra-action). Exact-head CI required before any admission claim. Production locked.

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
