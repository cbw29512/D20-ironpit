# Included weapon damage audit

2026-10-07. Owner: ChatGPT. Base main: `b63cbfb2e2432b1f8c37fb365500c895f4efb08e`.
Open PR inventory is empty at branch creation; no overlapping combat writer.
Grok retains art/presentation ownership. Netlify remains locked.

## Semantic reuse and schema, before implementation

The printed attack includes the extra dice. Brute changes the printed weapon's
base dice; Heated Weapons and Angelic Weapons are already typed on-hit damage.
Angelic Weapons also marks weapon attacks magical. No extra roll, action, save,
resource, duration, mutable trait state, or lifecycle is introduced.

Immutable source uses `SourceDamage2014`, `on_hit_damage`, and pinned trait/action
text. Preserve `source_actions` in the source model for independent validation.
Shared capability uses `DiceSpec`, `DamageEffectDefinition`, and
`DamageSourceQualifier.MAGICAL`. The existing compiler and both engines apply
critical dice and per-type defenses. Fight HP/audit state stays disposable;
source templates remain unchanged. No new runtime primitive or source-name branch.

| Behavior | Python oracle | Browser production | Data / permanent evidence |
|---|---|---|---|
| Printed base and rider dice | capability attack compiler; attack damage components | browser mixed damage resolver | source binding and compiled attack tests; mixed-damage regressions |
| Magical weapon qualifier | conditional damage defenses | browser conditional damage defenses | Angelic qualifier compiled into the attack; defense parity fixture |
| Critical and typed defenses | attack resolver | production attack resolver | source-derived attack fixture; ordinary/critical/immunity assertions |

## Source families

| 2014 family / classification | Cards | Binding | Other mechanics remain blocked |
|---|---|---|---|
| Brute / ENGINE_EXISTS_CERTIFICATION_MISSING | Bugbear, Gladiator | Printed base dice only | Surprise Attack; multiattack choice |
| Heated Weapons / ENGINE_EXISTS_CERTIFICATION_MISSING | Azer, Salamander | Printed fire rider only | Heated Body; Tail automatic-hit policy |
| Angelic Weapons / ENGINE_EXISTS_BINDING_MISSING | Deva, Planetar, Solar | Printed radiant rider plus magical qualifier | Innate spells, Healing Touch/Change Shape, legendary actions, Slaying Longbow |

Validate against each printed action, including thrown and two-handed variants.
Do not recompute thrown damage from a generic weapon table: preserve the source.
Salamander Tail's separate 2d6 fire remains separate from Heated Weapons' 1d6.
Missing/changed wording or mismatched payloads must leave the trait unbound.
A resolved trait does not imply a complete or certified monster.

## Continuous debt audit

A: Angelic magical qualifier was omitted from the source attack adapter; fix in
this tranche. Existing source dice must not receive the extra dice twice.
B: Source action text was discarded by the typed model; preserve it for validation.
Unrelated unsupported mechanics retain their blockers (M-009/M-010); no promotion
by stripping mechanics. Audit native 2024 source separately after implementation.

## Native 2024 audit

All 330 native trait texts were inspected; none prints Brute, Heated Weapons, or
Angelic Weapons. Azer Sentinel/Bugbear Warrior are native renamed counterparts.
Their own typed attacks already carry their printed damage; no 2014 trait or
magical qualifier is copied. Examples of edition differences: Planetar uses
2d6+7 slashing plus 4d8 radiant; Solar uses 8d8 radiant; Salamander Flame Spear
uses 2d6 fire. Native 2024 bindings and readiness remain unchanged.

## Verification

Permanent evidence: `backend/tests/test_included_weapon_traits_2014.py` covers all
seven cards, mismatched source/riders, thrown/two-handed values, and fail-closed
remaining blockers. `frontend/browser-included-weapon-damage.test.cjs` consumes
`scripts/included_weapon_damage_parity_fixture.py`: ten source-derived attacks
through the real compiler/serializer and both production resolvers, with fixed
independent totals for normal/critical damage, magical bypass, fire immunity,
radiant resistance, immutable parameters, and fight reset. It runs in CI.

Source/certification reports recomputed on this branch: 184/327 2014 monsters,
141/330 2024 monsters, 240/240 heroes per edition. All seven trait blockers are
removed; every affected monster retains independent blockers. No generated
runtime payload, certification manifest, hero, or art data changed. The generated
fix list changes `source:trait` from 97 to 96 affected cards (other cards still
have different unbound traits).

Passed: 62 focused source/compiler tests; ten source-derived production parity
cases; source-size/coverage checks; deterministic capability/blocker exports;
manifest/static regeneration; production wiring/backend-free checks and Netlify
lock verification. Full local Python/browser suites are running. All four new
exact-head workflow gates are pending; no prior-head success is carried forward.
