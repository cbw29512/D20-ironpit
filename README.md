# The Iron Pit

**Pick D&D cards. Watch stick figures close into melee and fight to the death.**

Iron Pit is a rules-first browser combat game built against the D&D 2024 / SRD 5.2.1 rules. The production fight path runs entirely in the browser; Python remains the reference rules implementation used by CI.

## Locked product goal

1. The landing page is the battlefield: six hero card slots on the left and six monster card slots on the right.
2. Click an empty hero slot to choose one of the 12 core classes, a level from 1–20, and an available certified pregen/build.
3. Click an empty monster slot to choose a RAW-ready monster from a catalog sorted numerically by Challenge Rating.
4. Every occupied slot is an individual combatant with its own HP, conditions, initiative identity, death state, and stick-figure silhouette.
5. Press the large **FIGHT** button in the center to roll initiative and run the automated battle.
6. Initiative appears at the top of each occupied card. The active card shakes during its events, critical hits shake/flash the screen red, and a natural-1 attack briefly blacks out the attacker card.
7. Combatants use legal ranged/thrown attacks while closing when available, continue closing instead of kiting, and prefer legal melee attacks once engaged.
8. Player characters at 0 HP remain in the battle under 2024 RAW: they become Unconscious, make Death Saving Throws, and can return above 0 HP through legal healing or a natural 20. Monsters follow their printed zero-HP behavior.
9. The fight ends only when one side is actually defeated under the supported RAW rules, not merely because every character has touched 0 HP once.
10. The detailed event log remains available beneath the battlefield for rules auditing.

See `docs/ARENA_POLICY.md` for the exact arena assumptions.

## Battlefield card picker

The battlefield always presents six fixed slots per side.

- **Hero slot:** click the slot, then choose Class → Level → Pregen / Build. All 12 classes and levels 1–20 are represented in the catalog; uncertified combinations remain unavailable for automated combat rather than being approximated.
- **Monster slot:** click the slot, then choose Challenge Rating → Monster. Only RAW-certified runnable monsters are selectable, sorted by numeric CR.
- Duplicate monsters are separate combatants. Three Goblins occupy three cards, keep three independent HP totals, and are defeated independently.
- Clicking an occupied slot allows that card to be changed or removed before the fight.
- The battlefield contract is **1–6 cards per side**.

## RAW action economy and healing policy

Iron Pit tactics never create extra economy. The rules engine tracks the printed cost of every supported option.

- A combatant normally has one **Action** on its turn.
- A **Bonus Action** can be used only when a feature, spell, or stat block provides one, and only one Bonus Action can be spent on that turn.
- A **Reaction** is trigger-driven. Once spent, it is unavailable until the start of that combatant's next turn.
- **Extra Attack / Multiattack** represents multiple strikes within one Attack/Multiattack action; it is not another Action.
- An Action spent on Dash cannot also pay for Attack or Multiattack that turn unless a separate rule explicitly grants another Action.
- An Action spent on healing also blocks Action-cost attacks, Dodge, Dash, Charge attacks, and other Action options for the rest of that turn; normal movement and an unused legal Bonus Action remain separate.
- Features that actually grant another Action, such as Action Surge, remain blocked until their exact additional-action rules are explicitly modeled and certified.
- Incapacitated creatures cannot spend Actions, Bonus Actions, or Reactions. Movement remains governed separately by the actual condition's Speed rules.

When a supported combatant has a legal healing option, Iron Pit's deterministic tactical priority is:

1. heal a living ally at **0 HP** when legally possible;
2. otherwise heal a **Bloodied** ally (half maximum HP or fewer);
3. only then consider self-healing, with Action-cost self-heals used conservatively because spending an Action can sacrifice offense.

That priority is AI policy only. The heal itself always obeys its printed range, target restrictions, Action/Bonus Action/Reaction cost, resource or spell-slot cost, and other rules. Reaction healing is never fired proactively; it requires its actual trigger to be implemented first.

## Current content model

- 330 unique SRD 5.2.1 monsters are cataloged with source metadata.
- Unsupported outcome-changing mechanics fail closed instead of being approximated.
- 63 monster templates are currently certified runnable in the browser combat engine.
- The hero catalog contains 720 planned cards across the 12 core classes, levels 1–20, and three build slots per level. Only explicitly audited builds are runnable; the current RAW-ready browser heroes are the level-1 Fighter and Barbarian builds.

## Combat foundation already represented

The certified subset includes core d20 attack resolution, AC, HP, initiative, natural 1/20 behavior, critical weapon dice, typed and mixed damage defenses, temporary HP hooks, advantage/disadvantage, range penalties, ordered Multiattack including mixed weapon/save steps, movement, Charge, Pack Tactics, Prone, Grappled, Restrained, Poisoned, timed conditions, condition immunities, Rage, Savage Attacker, Second Wind, Orc Adrenaline Rush/Relentless Endurance, zero-HP handling, Death Saving Throws, and deathmatch targeting of downed player characters.

A mechanic is considered ready only when both the Python reference and browser production path are covered by regression tests where applicable.

## Production architecture

- **GitHub:** source of truth and CI.
- **GitHub Pages / Netlify:** static deployment targets.
- **Browser engine:** authoritative production fight execution; no production `/api/` dependency.
- **Python rules reference:** CI oracle and test bed, not required by the deployed site.

Non-production Netlify builds are intentionally skipped to protect deploy credits.

## Run locally

### Browser app

```bash
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080`.

The checked-in source catalog is copied into `frontend/data/` by the static-site preparation script used for production/CI.

### Python reference tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest -q
```

## Certification gate

GitHub Actions must pass on the exact head before a roster count or UI build is called certified. The gate checks:

- production source-size limits;
- the full Python rules-reference suite;
- static browser packaging and the 330-monster data artifact;
- JavaScript syntax;
- deterministic browser combat regressions;
- RAW Action/Bonus Action/Reaction availability and healing-target priority;
- Dash/Multiattack and post-heal action-cost exclusivity;
- numeric monster-CR sorting and the character catalog model;
- six-slot battlefield wiring and DOM references;
- initiative/card-turn/critical/fumble presentation hooks;
- the strict melee-deathmatch and zero-HP contract;
- backend-free production execution;
- the clean GitHub Pages root entry;
- the production-only Netlify credit guard.

## Next product priorities

Continue expanding the RAW rules engine and monster-specific animation vocabulary. New monsters and heroes become runnable only after every outcome-changing mechanic they depend on is implemented and certified; unsupported rules are never approximated just to increase the card count.
