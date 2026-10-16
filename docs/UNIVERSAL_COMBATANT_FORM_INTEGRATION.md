# Universal combatant form — first integration slice

The existing `CombatantDefinition` schema is the single combatant form for
2014/2024 monsters, pregenerated characters, and future user-entered homebrew.
This is **not** a parallel renderer, simulator, or species-specific system.

**Definition of done for this slice:** a supplied form can be validated
without silently ignoring undeclared *top-level* fields; it then compiles with
the existing `compile_combatant` path; names only affect display metadata;
unsupported capabilities fail closed; a new fight starts from the immutable
template. Permanent tests cover form equivalence and rejection.

**State:** `CombatantDefinition` holds immutable source parameters;
`CombatantTemplate` is the canonical compiled form; `CombatantState`
holds mutable HP, conditions, buffs/debuffs, resource counts and position.
A new fight builds a fresh state. No mutable homebrew state is saved in a card.

**Logic:** form JSON → reject unexpected top-level keys → Pydantic schema
validation and references → unsupported-capability gate → existing compiler
→ existing Python reference / browser serialized combatant runtime.

**Scope limitation:** nested payload objects currently retain their own
existing Pydantic validation policies. A future user-facing editor must add
strict nested-field validation and present human-readable capability choices;
do not imply an unknown nested mechanic is safely supported. This slice adds
no new UI, browser engine, source admission, or monster certification.

**Parity contract:** the output template is the same shape already consumed
by the browser exporter/runtime. Browser serialization and round-trip tests
are required before exposing this to user-submitted homebrew.

**Ownership:** ChatGPT; branch
`refactor/universal-combatant-form-boundary-20261016`;
subsystem: combatant form validation boundary (not attacks, movement or
buff resolution); status: ACTIVE until exact-head CI and review.

**Future slices:** replace source-name checks such as Air Form/Water Form
with declarative movement grants; validate nested effect schemas strictly;
wire a guided homebrew editor to this same compiler; test Python/browser
combat parity on a synthetic renamed form. Keep each slice separate and
reuse existing primitives. Do not merge a universal rewrite in one change.

## Homebrew saving throw default — confirmed 2026-10-16

For a user-defined harmful condition effect, the default save outcome is:
**failed save applies the declared negative condition; successful save negates
that condition**. This is an editor default, not a universal RAW override.
The effect schema must retain explicit success and failure outcomes, because
some printed effects deal half damage or have other effects on success.

**Illustrative only (not an ability to implement):** an arbitrarily named
homebrew effect can target an area and call for a Wisdom save against its
creator-defined character DC. Failure applies the
universal Frightened condition for the source-defined duration; success does
not apply Frightened. The card supplies the name, area, save ability, DC source,
duration, action cost and uses; the engine uses its existing save/condition
mechanics. An ability name exists only for display, source provenance and logs; it is
never a runtime dispatch key. Renaming an ability without changing its mechanics
must not alter its combat outcome.
