# Antimagic susceptibility completion audit

## Ownership and context transfer

- Agent: ChatGPT; branch: `fix/2014-antimagic-susceptibility`; PR #629.
- Subsystem: terminal-effect lifecycle, shared timed Stunned, and the 2014 susceptibility binding.
- Starting main: `27ab34be9ac96642015ed1af9c62ea683074f3e1`.
- Resumed head: `81ff8ca871b89827ecfff4c160a2a3af601d64ba`.
- Status: COMPLETE; merged PR #629 after all four exact-head gates succeeded. No other open PR was returned at session start.
- Expected changes: terminal resolver, source binding, permanent tests, contracts,
  CI regression wiring, and directly generated artifacts.
- Exact resumed-head gates: 2014 Basic Roster, Paired Edition Monster Report,
  and 2014 Hero Certification succeeded; CI failed.
- Verified failure evidence: runtime capability export gained the new schema
  field; browser UI loaded 182 rows against a 184-row sentinel. Generated data
  was stale. These findings must be corrected, not bypassed.

## Schema and state before implementation

`CombatantDefinition` and `CombatantTemplate.terminal_effect_tags` are immutable
susceptibility data. The compiler preserves them and `template_row` serializes
them. No new mutable pool, action, save, or resource is needed. Dispel uses the existing timed-condition clock.
The existing fight state owns HP, Dead/Unconscious/Stable, active effects,
Concentration, and replacement forms. The next match constructs fresh state.

Logic: legal effect applied -> semantic tag matches susceptibility -> shared
terminal death or existing timed condition -> lifecycle cleanup. No match -> no
state change. Chris subsequently chose a 10-round Stunned response for Dispel
Magic, superseding his earlier Dispel-also-kills choice. No-save mapping is
retained. The source condition response is immutable; `timed_effects` is the
existing mutable clock and is discarded on reset. No new Stunned resolver.

`EffectRemovalAction.effect_tags` supplies semantic incoming tags.
`EffectTagConditionGrant` supplies source id/name, required tag, condition id,
and duration. The source grant binds `spell_dispelling` to Stunned for 10 rounds.
Tagged targets are legal even without an existing spell buff; ordinary spell
removal retains its existing target and resolution paths. An already-Stunned
or immune target is not selected for a redundant cast. Spending, range, logging,
and expiry use the existing Action/spell-slot and condition primitives.

## Semantic reuse and parity map

Classification: `ENGINE_EXISTS_BINDING_MISSING`. Petrified already provides a
terminal arena outcome, and instant death already provides the shared cleanup.
Both are reused; the effect tag is a declarative trigger, not a second death
engine. Ordinary instant death retains its separate prevention window.

| Surface | Resolution / evidence |
|---|---|
| Python | `combat/instant_death.py`; `combat/timed_conditions.py` |
| Browser | `browser-terminal-effects.js`; timed conditions and zero HP delegate |
| Source binding | `content/monster_terminal_effects_2014.py` |
| Serialization | `scripts/browser_template_serializer.py`; normal exporters |
| Permanent tests | `test_2014_antimagic_susceptibility.py`; browser equivalent; terminal lifecycle tests |
| Locked rule | Rules contract §13, Antimagic susceptibility |

2014 source family: Animated Armor, Flying Sword, Rug of Smothering. Only the
first two become unblocked; the rug retains unrelated Damage Transfer and attack
blockers. The source audit recomputed 184/327 compiled candidates on the resumed
branch; this is not an exact-head CI completion claim. Both pregen editions
remain outside the expansion lane. The vendored 2024 armor, sword, and rug have no Antimagic Susceptibility trait; no 2024 binding is added. A same-name construct is not proof of susceptibility.

## Continuous debt and next action

A: resolved. Direct outputs regenerated; full CI passed. Replacement-form and Concentration cleanup have permanent parity regressions.
B: resolved. New regressions are required in CI. Dependency checks fail before state mutation; contextual errors are logged.
C: historical status documents are snapshots, not current counts.

Next exact action: classify the next coherent family from the maintained fix tracker.
Do not carry prior-head CI, old counts, #625 work, or chat-only rules forward.

## Work queue

[Maintained fix tracker](MONSTER_FIX_TRACKER.md); [all 2014 blocked monsters](MONSTER_BLOCKERS_2014.md). Dispel regression evidence lives in `test_dispel_susceptibility.py` and `browser-dispel-susceptibility.test.cjs`.

## Final verification

Source head: `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`. Merged source baseline: `58bb5df4c239273588c702ab901775a2d65f0d9e`.

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811380): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811451): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811366): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811402): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
