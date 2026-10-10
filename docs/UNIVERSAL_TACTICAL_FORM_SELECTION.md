# Universal tactical replacement-form choice — 2014 and 2024

**Policy status:** user approved reuse of the Deva counter-form *decision logic*
for Druids and other shapechangers, October 9, 2026.
**Implementation status:** pure Python/browser scorer in draft PR #723; no new
Druid-form selection or Deva live Change Shape implementation/certification.

## One generic question, different legal sources

> Of the **source-legal and certified** forms this combatant could enter now,
> does any form improve its actual matchup enough to repay the printed
> transformation Action/Bonus Action, resource opportunity cost and lost options?

Use a single pure chooser (Python `choose_profitable_replacement_form`,
browser `chooseProfitableReplacementForm`). It receives **evaluated
projections**, not monster names, spell text or fake advantages. Printed ability
names remain in cards, source metadata and battle logs; generic behavior is
driven by source parameters. The shared chooser never authorizes a form; the
source-specific eligibility compiler does.

Candidate filtering **must** occur before scoring:

1. Edition, source actor identity, eligible creature types, levels, subclasses,
   CR ceiling, swim/fly restrictions, and certified source form IDs.
2. RAW Action or Bonus Action cost, remaining transformation charges, current
   form/replacement rules, form-dependent spellcasting and concentration.
3. Ownership of HP, independent form HP, temporary HP, defenses, creature type,
   ability scores, saving throws, attacks, traits, special senses and reversion.
4. Deterministic combat eligibility: legal target/range, movement allowed in
   Pit, no independent summoned entity or source-incompatible actions.
5. Source-specific form metadata and full Python/browser binding. An incomplete
   form is **not a candidate**. Fail closed; do not award projected benefits for
   a source ability absent in the compiled combatant.

## Evaluate what enemies CAN actually do

- Inspect printed opponents' available actions/spells/attacks, damage types,
  likely hit/save rates, source immunity qualifiers and action/slot resources.
- Estimate incoming damage and expected lost actions from conditions including
  Poisoned, Restrained, Paralyzed, Blinded, Charmed, Frightened, etc., checking
  the target's actual immunities, saving throw bonuses and conditional defenses.
- Always evaluate baseline defenses already retained. A Deva's nonmagical
  physical damage resistance, Magic Resistance and condition immunity cannot
  be 'gained again' from a form. Do not confuse poison-damage resistance with
  immunity to the Poisoned condition; magical/silvered physical attacks use
  source qualifiers.
- Evaluate new form's output/control and defenses, one-time entry survivability
  such as 2014 beast HP pool or 2024 Temporary HP, concentration risk, actual
  attack legality, movement and forfeited casting. The existing generic pure
  projection struct handles recurring damage/control/condition costs. Form HP
  and charge opportunity costs still need a certified source adapter before
  live deployment.
- Compare form's overall expected outcome against staying as-is across the
  remaining likely turns, **minus the transformed action's opportunity cost**
  and legal resource cost. No benefit or uncertain provenance => stay original.
- Scoring may use source semantics but never print/source name conditions. Tie
  choices are deterministic. Avoid multiple redundant shapeshifts/loops in a
  fight. Keep cardinality small enough for predictable, testable choices.

## Concrete adopter differences

| Source | Legal forms and capability rules | Cost / HP behavior |
| --- | --- | --- |
| 2014 Deva | Humanoid/Beast, CR <= 10; retains own stats except printed physical replacements, gains extra legal form capabilities (except class/legendary/lair), retains original creature token | Action, retains original HP; current curated four source forms in draft PR #723; remaining ability merge and AI integration open #724 |
| 2014 Circle of the Land Druid | Level 2-3 CR <=1/4 no swim/fly; level 4-7 CR <=1/2 swim allowed; level 8+ CR <=1 swim/fly allowed; no class name-based mechanic | Action; form's separate HP pool, excess damage/revert; concentration retained, no spells in form except higher-level source permissions. **Existing certified canonical 2014 form mapping remains unchanged until an independently tested source-legal multi-form policy replaces it.** |
| 2024 Druid | Source-allowed known Beast forms by level/CR, movement gates and subclass; do not reuse 2014 form list or same-name spell behavior | Bonus Action, owner HP retained and source-level Temporary HP; concentration and class-level permission separate from 2014. Existing single form by level remains until separate tests and rollout. |
| Other voluntary monster Shapechanger, metallic dragon, Polymorph or future homebrew | Exactly its own printed source-legal form types/CR/traits; hostile Polymorph is not voluntary counter-form AI | Its own printed Action, duration, resource, concentration, equipment, HP and revert conditions. Same generic evaluator after source-specific eligibility passes. |

**Important existing constraint:** `docs/2014_DRUID_CANONICAL_WILD_SHAPE_FORMS.md`
currently locks one deterministic form per Land Druid level interval. User's
approval of universal **selection logic** does not by itself certify or deploy
a replacement for those Wild Shape progression fixtures. First build an
edition-accurate source-specific shortlist that honors max CR and movement,
then measure Python/browser regressions; only then change the existing
form-selection policy with explicit source/test evidence.

## Verification and rollout

- Test **the chooser once** for no beneficial legal option, different Action
  costs, source-defined opponent damage/condition threats, projected resource
  and survivability costs, deterministic ties and illegal-form rejection.
- Test **each adapter** with a separate source/edition fixture; no form ID
  pulled from another edition or outside its printed CR/known-form restrictions.
- Test original card immutability, persistent character identity, combat
  resource/reset/reversion, damage and on-hit effects, browser/Python identical
  decisions and full exact-head CI after any runtime integration.
- Exclude shapechange choices from AI while the active form's full source
  capability merge remains unsupported; a physical stat overlay alone must
  never count as a legal source-perfect transformation.
- Netlify deployment remains locked until independently authorized.

Refs: `SOUL.md`, `docs/IRON_PIT_RULES_CONTRACT.md` §20,
`docs/2014_DRUID_CANONICAL_WILD_SHAPE_FORMS.md`,
draft [PR #723](https://github.com/cbw29512/D20-ironpit/pull/723),
remainder [#724](https://github.com/cbw29512/D20-ironpit/issues/724).
