# 2024 Barbarian follow-up audit

Anchor: `44c0bca5c814f01ea01013a83380046f86cd7e07`, both main and
`feat/2024-barbarian-next`; PR #154 verified merged. Main's CI, 2014 Hero
Certification, Paired Edition Monster Report and artifact sync passed.

Rules authority: [D&D Beyond 2024 Basic Rules, Barbarian](https://www.dndbeyond.com/sources/dnd/br-2024/character-classes#Barbarian).
Reviewed September 18, 2026. This audit does not confer certification.

| Feature | Classification | Existing engine / remaining work |
|---|---|---|
| Retaliation | 4: missing trigger primitive | Reuse encounter attacks, reaction spending, grid distance; add damage-trigger dispatch across damage families. |
| Relentless Rage | 3: extend existing primitive | Zero-HP replacement and shared saving throws; add effect requirement, escalating attempts, replacement HP. |
| Staggering Blow | 4: missing consumption rules | Extend modifiers with next-save Disadvantage and OA suppression. |
| Sundering Blow | 4: missing consumption rules | Existing flat attack modifiers lack other-creature, next-roll consumption. |
| Level-17 Improved Brutal Strike | 3 plus 4 | Damage scaling exists; two distinct effects still missing. |
| Intimidating Presence | 3 | Reuse area geometry, repeat-save conditions, Bonus Action/resources; bind 2024 parameters independently of 2014. |
| Persistent Rage | 3 | Extend existing Rage expiry/termination and initiative-resource lifecycle. |
| Indomitable Might | 4 | Shared save/check resolvers need total replacement. |
| Epic Boon | 4, pending separate feat audit | Canonical row selects Irresistible Offense; do not mark supported. |
| Primal Champion | 1 | Source rows contain score/HP changes; verify complete derived-template propagation before promotion. |
| Primal Knowledge | 2 only where no applicable checks | Existing exclusion needs reinspection against supported grapple/skill-check paths. |

Earlier progression must also be audited: certification artifacts still stop
Barbarian at level 6 despite engine bindings for later features. A successful
builder call is not proof of public certification. The Brutal Strike selection,
Advantage tradeoff and Hamstring nonstacking also need regression review.

## Current tranche: effect-bound zero-HP saving throw

State first: immutable `EffectBoundSurvivalSave` stores source/effect IDs, save
ability, initial DC, DC increment, and replacement HP. Mutable per-fight
`survival_save_uses` stores attempts; pending evidence moves into the triggering
damage event. Fresh state resets both. No source-card mutation occurs.

Python: extend `undead_fortitude.py`, call from `zero_hp.apply_damage` after
massive-damage exclusion and before Relentless Endurance/unconsciousness.
Browser: matching extension in `browser-undead-fortitude.js` and `browser-zero-hp.js`.
Both reuse their existing complete saving-throw resolver. No duplicate dice/save
pipeline; the existing Undead Fortitude behavior is preserved.

Declarative 2024 binding: Rage required, Constitution DC 10, +5 per attempt,
replacement HP twice class level. Failed attempts also count. No action cost.
RAW permits the save; deterministic policy attempts it before spending the
single-use species prevention, which remains available if the save fails.
Between-fight restoration supplies the rest reset under the permanent arena
contract. No in-fight rest system is introduced.

Evidence is included in weapon/Graze, save-action, spell-attack and Divine Spark
events: original dice, modifier, total, DC, outcome, HP and next DC. Existing
save modifiers and rerolls remain in the shared resolver.

Tests: `test_effect_bound_survival.py`, `browser-effect-bound-survival.test.cjs`;
CI explicitly runs the browser regression. Higher levels remain blocked by
unimplemented capabilities. This tranche must not increase readiness counts.
