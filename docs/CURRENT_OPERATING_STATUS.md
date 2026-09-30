# Current operating status

Recorded 2026-09-30 while advancing the certified 2024 Circle of the Land Druid progression through level 7.

This file is operating authority for *what to work on next*. Combat rules still live in `docs/IRON_PIT_RULES_CONTRACT.md`. If this file and a chat summary disagree, this file wins until it is updated on `main`.

## Owner split

- **Iron Pit (`cbw29512/D20-ironpit`)** is the only combat-engine lane. One agent at a time.
- **Blackink Bestiary / coloring-book local AI** is a separate product. Do not mix PRs, CI, or GPU loops into this repository.

## What is already certified on `main`

From `backend/app/content/certified_hero_progressions.py`:

| Edition | Class | Registered levels |
|---|---|---|
| 2014 | Fighter (Champion) | 1–20 |
| 2014 | Barbarian (Berserker) | 1–20 |
| 2014 | Bard (Lore) | 1–20 |
| 2014 | Cleric (Life) | 1–20 |
| 2014 | Druid (Land) | 1–20 |
| 2014 | Monk (Open Hand) | 1–20 |
| 2014 | Paladin (Devotion) | 1–20 |
| 2014 | Ranger (Hunter) | 1–20 |
| 2014 | Rogue (Thief) | 1–20 |
| 2014 | Sorcerer (Draconic) | 1–20 |
| 2014 | Warlock (Fiend) | 1–20 |
| 2014 | Wizard (Evoker) | 1–20 |
| 2024 | Barbarian (Berserker) | 1–20 |
| 2024 | Bard (Lore) | 1–20 |
| 2024 | Cleric (Life) | 1–20 |
| 2024 | Fighter (Champion) | 1–20 |
| 2024 | Rogue (Thief) | 1–20 |
| 2024 | Druid (Land) | 1–7 |

2024 public-ready hero slots after the Druid 7 tranche: **107 / 240**.
2024 public-ready monster slots in `data/monster_certification_manifest.json`: **140 / 330**.
2014 browser monster roster asserted in tests: **129** certified.

Holy Nimbus (2014 Paladin 20) is a timed self-buff plus timed emanation primitive. Do not add a Paladin-named combat resolver.

## Active lane

**2014 canonical pregens remain complete at 240 / 240 registered level snapshots.** The 2014 Hero Certification and paired-edition guard workflows were green on the exact PR #436 head before merge.

**2024 canonical pregens are now 107 / 240 public-ready after this tranche.** Fighter, Barbarian, Rogue, Life Cleric, and Lore Bard are complete at levels 1–20. Circle of the Land Druid is certified through level 7.

Active implementation lane after merge: **2024 Circle of the Land Druid level 8 onward**.

Bard 20 Words of Creation is edition-specific: 2024 always prepares Power Word Heal and Power Word Kill, and either spell may affect one additional creature only when that second creature is within 10 feet of the first. Power Word Heal is modeled as one atomic healing resolution that also ends Charmed, Frightened, Paralyzed, Poisoned, and Stunned, with the target optionally spending its Reaction to stand from Prone.

Bard 18 Superior Inspiration is edition-specific: 2024 restores Bardic Inspiration to two on Initiative when below two; do not substitute the 2014 zero-use-to-one rule.
Bard 18's new prepared spell is 2024 Teleport, recorded as arena-out-of-scope rather than approximated.

Bard 19 canonical Epic Boon choice: **Boon of Fate**. The 2024 Bard table recommends Boon of Spell Recall but permits any qualified Epic Boon; Lyra uses Boon of Fate so the build reuses the already-certified universal 2d4 D20 outcome-adjustment mechanic.

For each Druid tranche:
- start from the completed 2014 Circle of the Land Druid progression and reuse universal mechanics where behavior is equivalent;
- verify every 2024 class/subclass feature against 2024 rules before carrying behavior forward;
- keep same-named 2014/2024 spells edition-isolated and require an explicit 2024 spell fingerprint before certification;
- keep Python/browser parity, independent combat fingerprints, generated parity, and the 2014 guard green before merge;
- do not weaken Netlify publishing locks.

## Parked / superseded

Stale stacked PRs whose work already landed on `main` (2014 Paladin 20, 2014 Rogue 20, 2014 Monk 20, 2024 Rogue 20, 2024 Cleric through 12) are to be closed as superseded. Do not rebase them.

Universal-engine PRs that are still current against `main` may stay open only if they are required by the 2014 Cleric lane (healing, conditions, save tags, upcasting).


## Universal combat refactor plan

Architecture target: **checks -> modifiers -> result -> state mutation -> audit**.

This is now the default refactor direction for the engine. Named abilities remain source/audit metadata; combat resolution depends on universal typed facts.

Current migration sequence:

1. **Conditions / buffs / debuffs**
   - remove class/feature-name immunity branches where an existing condition-immunity or debuff-counter primitive can express the rule;
   - preserve source qualifiers such as creature type, magical/nonmagical origin, effect tags, duration, and resource cost;
   - Nature's Ward is the immediate Druid proving case: poison/disease immunity plus Fey/Elemental-scoped Charmed/Frightened immunity.
2. **Attacks / saves / checks**
   - keep legality, roll-mode modifiers, bonuses, DC/AC comparison, and final result separate;
   - source abilities provide data, not alternate attack/save engines.
3. **Damage / healing**
   - route all components through typed defense/reduction/replacement checks before HP mutation.
4. **Movement**
   - route movement through legality, movement-mode, terrain/debuff/counter, path, and final-position checks.
5. **Resources / action economy / recharge**
   - resolve availability first, then spend only after the action is accepted at the appropriate resolution point.
6. **Hooks / reactions / interrupts**
   - keep timing generic; named sources register declarative behavior into canonical windows.

Refactor discipline:

- preserve behavior while migrating;
- Python reference and browser implementation move together;
- add/regenerate permanent parity tests for every migrated path;
- do not create a new primitive when existing checks/modifiers can compose the rule;
- do not stall the active 2024 Druid lane for unrelated cosmetic rewrites;
- when a named special case is discovered during active work, migrate it if the shared replacement is small and safe; otherwise record it here and continue the canonical lane.

Immediate examples:

- **Nature's Ward (Druid 10):** completed as the proving case for typed checks -> universal modifiers/counters -> result; no Druid-named resolver.
- **Mindless Rage:** known named branch in the condition-immunity path. Do not mechanically collapse it yet; preserve the 2014 vs 2024 difference for already-active Charm/Frighten while migrating it to shared condition/debuff semantics in a dedicated tranche.

## CI / spend

September 2026 included Actions usage was exhausted by Iron Pit volume (~$197 gross on this repo).

Heavy workflows are gated:

- `2014-hero-certification.yml` — `main`, PRs into `main`, or `workflow_dispatch`
- `sync-generated.yml` — `main` or `workflow_dispatch` only (never `feat/2014-*`)
- `ci.yml` — `main` + pull_request (unchanged)

Do not restore per-push certification on feature branches. Run generators locally; commit owned outputs; use **Run workflow** when a cert pass is required.

## Agent rules for this repo

1. One coherent tranche per PR. Rebase on current `main` or close.
2. Never hand-edit generated artifacts.
3. Never implement a class-named resolver when a universal primitive exists.
4. Ask one clarification question rather than guessing RAW.
5. Do not start a second 2024 class while the active 2024 class progression is open.


## 2024 Druid lane

Thalen Greenbough remains the persistent canonical Druid and preserves the Land-Druid damage-caster concept while applying 2024 rules.

- Level 1 uses **Primal Order: Magician**.
- 2024 Wood Elf, Acolyte, and background-based ability increases are explicit.
- 2024 Poison Spray is edition-isolated as a 30-foot ranged spell attack for 1d12 Poison at level 1.
- Cure Wounds and Healing Word reuse their certified 2024 healing primitives.
- Longstrider uses an explicit 2024 fingerprint.
- Druidic always prepares Speak with Animals; it is arena-neutral, not approximated.
- Unsupported or only-partially-generalized spell mechanics are not substituted with 2014 behavior.
- Level 2 uses the shared replacement-form engine for 2024 Wild Shape: Bonus Action entry, Wolf form, owner HP retained, Druid-level Temporary HP, retained Humanoid creature type, no spellcasting while shaped, and generic reversion on Incapacitated/death.
- Wild Companion remains source-audited but arena-unavailable under the global no-separate-summon rule.
- 2024 Faerie Fire is edition-fingerprinted and uses the shared area-save/modifier engine; the same tranche re-audited 2014 Faerie Fire to suppress Invisible benefits through a universal modifier.
- Level 3 chooses **Circle of the Land — Arid** and adds Land's Aid plus always-prepared Blur, Burning Hands, and Fire Bolt.
- Land's Aid reuses the universal area-save engine with a generic independent area-healing rider; one Wild Shape use pays for the entire Magic action.
- Blur reuses the modifier stack with source-derived Blindsight/Truesight ranges and distance-aware bypass; no Blur-named attack resolver exists.
- The 2024 monster source audit now reconciles Blindsight/Truesight to the vendored SRD source. Generated capability/browser artifacts carry those ranges.
- Level 4 takes the canonical **+2 Wisdom ASI** (17→19), adds **Starry Wisp** as the fourth Druid cantrip, and fills the seventh prepared-spell slot with arena-neutral **Detect Poison and Disease**; all Wisdom-derived spell/save/skill math is profile-derived.

- Level 5 adds **Wild Resurgence** through the universal resource-conversion engine: spell-slot-to-Wild-Shape restoration is target-empty and shared once-per-turn across slot levels; Wild-Shape-to-1st-level-slot restoration uses the same engine with a once-per-Long-Rest gate and preserves one Wild Shape use under automatic arena policy.
- Level 5 reuses the explicit **2024 Fireball** fingerprint for Arid Land, reuses universal **Dispel Magic** with Wisdom casting, and uses **Water Breathing** as the ninth arena-neutral prepared Druid spell.
- Level 6 adds **Natural Recovery** through the universal alternate-spell-cast resource: one prepared Circle Spell of level 1+ can be cast without a spell slot once per Long Rest; **Aid** is the tenth ordinary prepared Druid spell.
- Level 7 chooses **Elemental Fury: Potent Spellcasting** and adds Wisdom (+4) to each damaging Druid cantrip through the generic spell-action damage bonus; it does not add a Druid-named resolver.
- Arid Land level 7 adds explicit **2024 Blight**. Its Plant-creature automatic failure is a new universal save parameter with Python/browser parity, and **Divination** is the eleventh ordinary prepared Druid spell as an arena-neutral choice.
- Call Lightning remains unbound until its fixed storm-cloud footprint can be represented exactly by a universal persistent-area spell primitive; it is not approximated.
