# Conditional turning-save buff tranche

- Owner: ChatGPT; ACTIVE; branch `fix/passive-contextual-save-buffs`; issue #538.
- Starting main: `f68d76f23a8e427ade0b8d0b7da336a59f58f35a` (#623).
- Scope: passive friendly save buffs, contextual turning saves, source binding,
  Python/browser regressions, generated combat artifacts and CI registration.
- #585 remains stale/conflicted on `3a5bafd15a91cd0e8b52661b7abeee01014ab0ea`.
  Exclude its combatant schema and serializer. The one additive cleric-channel
  caller argument (`setup`) and additive CI test registration were reconciled
  against its exact head; neither changes its proposed channel/resource policy.
  Existing aura serialization covers the new passive friendly payload.
- No art, portraits, figure changes, lair actions or Netlify publishing.

## State-first reuse and source audit

The printed 2014 Ghast grants itself and ghouls within 30 feet Advantage against
effects that turn undead. The printed 2014 Lich grants itself that same save
Advantage. Full scans of the pinned 327/330 source corpora find those two direct
turning-save traits only in 2014; neither 2024 counterpart prints this buff.

Existing primitives: `SavingThrowAdvantageGrant`, `TimedFriendlySaveAura`, the
passive self-buff declaration, source-owned `CombatModifier`, live aura distance,
context effect tags, normal Advantage/Disadvantage cancellation and fresh state.
Classification: ENGINE_EXISTS_COMPOSITION + ENGINE_EXISTS_PARAMETER_DELTA.

Immutable source data declares recipient template IDs and whether the source
always qualifies. Printed "any ghouls" uses recipient scope on both sides, independently of the
existing all-allies default. The aura sync installs ordinary conditional Advantage buffs in
temporary fight state. The 30-foot turning aura covers the whole Pit under Chris's explicit arena rule
(§9); losing the source removes its modifiers. Other radius-based auras still use
live footprint distance.
Self-only defenses use existing passive modifier compilation. No activation,
resource, source-card mutation, special turning condition or alternate save path.

Python: friendly_save_auras -> modifier stack; turn_creature_effects -> shared save.
Browser: browser-friendly-save-auras -> modifiers; browser-turn-creature-effects
-> shared saves. Existing serializers emit the complete aura and passive grants.
The incoming turning save declares semantic `turning` context; ordinary fear saves
must not activate the buff. Source names remain card/log metadata only.

Baseline: monsters 2014 176/327, 2024 141/330; heroes 240/240 each, recomputed on
the starting main. Regenerated branch data is 2014 177/327 and 2024 141/330,
with heroes still 240/240 each. Ghast is unlocked; Lich retains unrelated blockers.

Touched debt: turning saves currently omit all save context and encounter/round
context in both runtimes. Correct this through the shared save call, and refresh
auras before each target so a source destroyed by an earlier save stops protecting
later recipients. Split the Python turning state/resolver to respect module limits.

Repeat-save debt is also fixed in this batch: source-owned `TimedEffect` retains
a typed immutable save context. Both lifecycles reuse that context and the shared
save resolver with live aura refresh, round and encounter context. Turning is
matched semantically on initial and repeat saves; ordinary fear never matches.
The timed-effect model was extracted from runtime state to preserve module limits.

Batch policy: compare printed mechanical clauses across both monster source
corpora and existing hero mechanics before selecting a family. Bind every exact
source match in one tranche; unrelated qualifiers remain their own audited batch.

## Verification snapshot before PR integration

- Full 327/330 source scans assert the two 2014 matches and no 2024 backport.
- 42 focused Python regressions pass, including Pit-wide eligibility, ordinary radius behavior, source destruction,
  original card/fresh-state integrity, source-only Lich compilation, shared save
  cancellation and initial/repeat contextual saves.
- Printed "any ghouls" is explicitly tested on both sides. The recipient-scope
  and Pit-wide range corrections supersede the first broad local Python/browser run; the complete
  final browser gate is rerun, and the full Python suite is required on exact-head
  CI before merge. No prior-head result can certify the final head.
- All generated data comes from canonical exporters; source-size, engine coverage,
  runtime capability and checklist checks are required.
- No open correctness debt remains in this family. The next step is exact-head CI
  integration, then a fresh context packet releasing this subsystem ownership.
