# Current operating status

Recorded 2026-10-02 for the 2024 Open Hand Monk level 17 tranche. Main baseline: `99839f044a2b2a53369e18e80ec3c748899ffbec`.

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
| 2024 | Druid (Land) | 1–20 |
| 2024 | Monk (Open Hand) | 1–17 |

2024 public-ready hero slots in this level-16 tranche: **136 / 240**.
2024 public-ready monster slots in `data/monster_certification_manifest.json`: **140 / 330**.
2014 browser monster roster asserted in tests: **129** certified.

Holy Nimbus (2014 Paladin 20) is a timed self-buff plus timed emanation primitive. Do not add a Paladin-named combat resolver.

## Active lane

**2014 canonical pregens remain complete at 240 / 240 registered level snapshots.**

**2024 canonical pregens are 137 / 240 in this tranche.** Fighter, Barbarian, Rogue, Life Cleric, Lore Bard, and Circle of the Land Druid are complete at levels 1–20; Open Hand Monk is advanced through level 17 here.

Active implementation lane: **2024 Open Hand Monk level 17.** Quivering Palm extends the universal hit-armed deferred-save effect with typed failed-save damage, half damage on success, harmless mark replacement, and optional Attack-action slot activation. No Monk-named resolver is added.

Owner-requested completion order: finish every canonical pregen; audit and test the universal engine; finish monster readiness with 2014 catch-up and paired-edition certification; then finish the website's visual design. Engine fixes required to certify a pregen belong in its tranche. Preserve the publishing lock throughout.

### 2024 Monk lane

- Kael Stillwater remains the persistent canonical Monk and remains Human.
- Level 1 uses the legal 2024 Criminal background, Alert origin feat, Human Skillful, and Human Versatile selecting Skilled.
- Martial Arts uses a 1d6 die and the source-agnostic Bonus Attack grant; unlike 2014, the 2024 Bonus Unarmed Strike does not require a prior Attack action.
- Human Resourceful initializes fresh-rest combat state with Heroic Inspiration through generic combatant state.
- The separate 2014 Monk bonus-strike prerequisite resolver remains unchanged and edition-isolated.
- Level 2 adds Monk's Focus, Unarmored Movement, and Uncanny Metabolism through shared resource, action-economy, movement, initiative-resource, healing, Dodge, Disengage, and Dash mechanics.
- Level 3 adds Deflect Attacks through the universal attack-damage-reduction Reaction model; 2014 Deflect Missiles now binds the same primitive with its own ranged-only parameters.
- Level 3 selects Warrior of the Open Hand. Canonical arena automation selects Open Hand Technique's Topple option on Flurry hits and composes the shared Dexterity-save-to-Prone attack rider; no Open-Hand-named resolver is added for 2024.
- Level 4 uses the repeatable **Ability Score Improvement** feat for **+2 Dexterity (17→19)**. Shared derived-stat logic updates AC, Initiative, Unarmed Strike attack/damage, Dexterity save/skills, and Deflect Attacks reduction; Focus Points advance to 4.
- **Slow Fall** is source-audited but arena-neutral because the standard Iron Pit battlefield has no falling hazard. No Monk-named resolver or ordinary attack-damage reduction is created for it.
- Level 5 is merged. Extra Attack and Stunning Strike use shared attack-action, resource-backed hit-save, timed-condition and modifier primitives.
- Level 6 adds Empowered Strikes through a universal attack damage-type choice and Wholeness of Body through shared limited-use Bonus Action healing. Unarmored Movement increases to +15 feet (45-foot Speed for Kael).
- Level 7 adds Evasion through the shared Dexterity-save half-damage transform. The 2024 binding disables Evasion while Incapacitated; 2014 behavior remains isolated.
- Level 8 uses the repeatable **Ability Score Improvement** feat for **+1 Dexterity (19→20) and +1 Constitution (15→16)**. Shared derived-stat logic updates AC, HP, Initiative, attack/damage, Dexterity save, and Dexterity skills.
- Level 9 adds **Acrobatic Movement**. RAW permits movement along vertical surfaces and across liquids while unarmored and not wielding a Shield; the current Iron Pit battlefield has no vertical-surface or liquid-terrain state, so the feature is source-audited as arena-neutral rather than approximated. Proficiency Bonus advances to +4 and Focus Points to 9.
- Level 10 increases Unarmored Movement to +20 feet and Focus Points to 10. **Heightened Focus** upgrades Flurry of Blows to three Unarmed Strikes and Focus-backed Patient Defense to grant 2d8 Temporary HP through universal mechanics. The optional Step of the Wind ally-transport choice remains deliberately unselected by arena automation. **Self-Restoration** binds to the generic end-turn condition-removal primitive with deterministic priority **Charmed → Frightened → Poisoned**.
- Level 11 advances Martial Arts to **d10**, Focus Points to **11**, and HP to **91**. The tranche also corrects prior 2024 Monk healing-die drift by deriving Uncanny Metabolism and Wholeness of Body from the same Martial Arts die rule. **Fleet Step** uses the universal Bonus Action follow-up tactical grant. After another eligible Bonus Action, arena automation immediately takes the resource-free Dash form of Step of the Wind; it does not invent retreat or kiting behavior.
- Level 12 uses the repeatable **Ability Score Improvement** feat for **+2 Wisdom (10→12)**, following the Open Hand unarmed-offense specialization priority of Dexterity → Wisdom → Constitution. This raises AC to 16, Stunning Strike DC to 13, Wisdom skills by 1, and Wholeness of Body healing to 1d10+1 while Focus Points advance to 12.
- Level 13 adds **Deflect Energy**, widening Deflect Attacks from Bludgeoning/Piercing/Slashing to attacks dealing any damage type. Proficiency Bonus advances to +5, Focus Points to 13, HP to 107, Initiative/Unarmed Strike attack bonus to +10, and Stunning Strike DC to 14. The same tranche closes the existing RAW redirect gap: when Deflect Attacks reduces an attack to 0 damage, the Monk can spend 1 Focus Point to force the printed Dexterity save and deal two Martial Arts dice plus Dexterity modifier on a failure through a universal zero-damage redirect primitive with Python/browser parity.
- Level 14 adds **Disciplined Survivor** by reusing universal saving-throw proficiency grants and the shared failed-save reroll. Constitution, Intelligence, Wisdom, and Charisma join Kael's existing Strength/Dexterity save proficiencies; a failed save may spend 1 Focus Point to reroll and must use the replacement result. Unarmored Movement rises to +25 feet (55-foot Speed), Focus Points to 14, and HP to 115.
- Level 15 adds **Perfect Focus** through the universal initiative resource-refill primitive. Uncanny Metabolism resolves first; if it is unavailable/not used and Focus Points are 3 or fewer, Perfect Focus restores the total to 4. Focus Points advance to 15 and HP to 123.
- Level 16 uses the repeatable **Ability Score Improvement** feat for **+2 Wisdom (12→14)**. Shared derived-stat logic raises AC to 17, Wisdom save/skills, Stunning Strike and Deflect Attacks redirect DCs to 15, and Wholeness of Body healing to 1d10+2; Focus Points advance to 16 and HP to 131.
- Level 17 adds **Quivering Palm** through the universal deferred-save effect engine. An Unarmed Strike hit may spend 4 Focus Points to arm one target; an existing mark can end harmlessly before a different target is armed. Detonation uses the Monk Constitution-save DC and deals 10d12 Force damage on failure or half on success. Arena selection prefers replacing one legal Attack-action attack over spending the entire Action, while retaining the full-Action fallback when no Attack slot is legal. The Martial Arts die advances to d12, Proficiency Bonus to +6, Focus Points to 17, HP to 139, Initiative/attack bonus to +11, and Monk save DC to 16.
- The same tranche closes the pre-existing 2014 Quivering Palm harmless-end gap through the same universal mark-replacement parameter; 2014 remains Action-only for detonation.
- Next exact level after level 17 certification is **Monk 18**; audit Superior Defense against existing timed self-buff and typed damage-resistance primitives before adding engine behavior.

### Druid spell-selection policy

For Iron Pit caster pregens, ordinary prepared-spell choices prioritize **damage and healing** when legal choices are available and mechanically useful in arena combat. Utility/control options do not displace a stronger damage/healing choice merely because they are newly available. Always-prepared subclass spells are still source-audited and implemented when combat-relevant, but they do not redefine the canonical optimization lane.

Druid 9 follows that policy:
- **Cone of Cold** is the new damaging prepared choice: 60-foot self-origin cone, Constitution save, 8d8 Cold, half on success, +1d8 per slot above 5.
- **Mass Cure Wounds** is the new healing prepared choice: point within 60 feet, up to six creatures in a 30-foot-radius sphere, 5d8 + Wisdom modifier, +1d8 per slot above 5.
- **Wall of Stone** is an Arid Circle spell granted independently of ordinary prepared choices. It is represented through a universal persistent-barrier primitive and does not replace the damage/healing-first choices.

Bard 20 Words of Creation is edition-specific: 2024 always prepares Power Word Heal and Power Word Kill, and either spell may affect one additional creature only when that second creature is within 10 feet of the first. Power Word Heal is modeled as one atomic healing resolution that also ends Charmed, Frightened, Paralyzed, Poisoned, and Stunned, with the target optionally spending its Reaction to stand from Prone.

Bard 18 Superior Inspiration is edition-specific: 2024 restores Bardic Inspiration to two on Initiative when below two; do not substitute the 2014 zero-use-to-one rule.
Bard 18's new prepared spell is 2024 Teleport, recorded as arena-out-of-scope rather than approximated.

Bard 19 canonical Epic Boon choice: **Boon of Fate**. The 2024 Bard table recommends Boon of Spell Recall but permits any qualified Epic Boon; Lyra uses Boon of Fate so the build reuses the already-certified universal 2d4 D20 outcome-adjustment mechanic.

For each Druid tranche:
- start from the completed 2014 Circle of the Land Druid progression and reuse universal mechanics where behavior is equivalent;
- verify every 2024 class/subclass feature against 2024 rules before carrying behavior forward;
- keep same-named 2014/2024 spells edition-isolated and require an explicit 2024 spell fingerprint before certification;
- prioritize damaging/healing prepared spells for the Iron Pit combat build;
- keep Python/browser parity, independent combat fingerprints, generated parity, and the 2014 guard green before merge;
- do not weaken Netlify publishing locks.

## Parked / superseded

Stale stacked PRs whose work already landed on `main` are to be closed as superseded. Do not rebase them.

Universal-engine PRs that are still current against `main` may stay open only if they serve a current combat requirement.

## Universal combat refactor plan

Architecture target: **checks -> modifiers -> result -> state mutation -> audit**.

This is the default refactor direction for the engine. Named abilities remain source/audit metadata; combat resolution depends on universal typed facts.

Current migration sequence:

1. **Conditions / buffs / debuffs**
   - remove class/feature-name immunity branches where an existing condition-immunity or debuff-counter primitive can express the rule;
   - preserve source qualifiers such as creature type, magical/nonmagical origin, effect tags, duration, and resource cost;
   - Nature's Ward (Druid 10) is 2024-edition-specific: immunity to the Poisoned condition plus damage resistance from the current land choice; canonical Arid grants Fire resistance. Reuse generic condition-immunity and damage-resistance data, not a Druid-named resolver.
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

- **Nature's Ward (Druid 10):** 2024 Arid grants Poisoned immunity and Fire resistance. Bind those to generic condition-immunity and damage-resistance data; do not carry forward the 2014 feature by name.
- **Mindless Rage:** preserve the 2014 vs 2024 difference for already-active Charm/Frighten while migrating it to shared condition/debuff semantics in a dedicated tranche.

## CI / spend

September 2026 included Actions usage was exhausted by Iron Pit volume (~$197 gross on this repo).

Heavy workflows are gated:

- `2014-hero-certification.yml` — `main`, PRs into `main`, or `workflow_dispatch`
- `sync-generated.yml` — `main` or `workflow_dispatch` only
- `ci.yml` — `main` + pull_request

Do not restore per-push certification on feature branches. Generated artifacts must be produced by the repository generator, never hand-edited.

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
- Level 4 takes the canonical **+2 Wisdom ASI** (17→19), adds **Starry Wisp** as the fourth Druid cantrip, and fills the seventh prepared-spell slot with arena-neutral **Detect Poison and Disease**.
- Level 5 adds **Wild Resurgence** through the universal resource-conversion engine and reuses the explicit **2024 Fireball** fingerprint for Arid Land; **Dispel Magic** and **Water Breathing** fill the remaining progression needs.
- Level 6 adds **Natural Recovery** through the universal alternate-spell-cast resource; **Aid** is the tenth ordinary prepared Druid spell.
- Level 7 chooses **Elemental Fury: Potent Spellcasting** and adds Wisdom (+4) to each damaging Druid cantrip through generic spell-action damage bonus; Arid adds explicit **2024 Blight** and **Divination** is the eleventh ordinary prepared spell.
- Level 8 takes **+1 Wisdom / +1 Charisma** (Wisdom 19→20, Charisma 15→16), upgrades deterministic Wild Shape to certified **Brown Bear (CR 1)**, and adds **Freedom of Movement** as the twelfth ordinary prepared spell.
- Level 9 advances to PB +4, 48 HP, slots 4/3/3/3/1, and fourteen ordinary prepared Druid spells. The new prepared choices are **Cone of Cold** and **Mass Cure Wounds** under the damage/healing-first policy.
- Arid level 9 additionally grants **Wall of Stone**. Its source data binds to a reusable persistent-barrier engine for blocked edges, forced-movement interaction, destructible sections, support legality, concentration lifecycle, and Python/browser parity; it is not a Druid-named resolver.
- Level 10 adds **Nature's Ward** through universal defenses: Poisoned immunity plus Arid Fire resistance. It also adds **Thunderclap** and prepares **Thunderwave** under the damage-first policy.
- Level 11 advances to 58 HP, 16 prepared spells, and a level-6 slot. The new prepared spell is **Heal**: 70 fixed HP plus removal of Blinded, Deafened, and Poisoned through the universal healing action.
- Level 12 advances to 63 HP and uses the repeatable **Ability Score Improvement** feat for +2 Charisma (16→18); Wisdom remains capped at 20 and the damage/healing spell package is preserved.
- Level 13 advances to PB +5, 68 HP, 17 prepared spells, and a level-7 slot. **Fire Storm** is the damage-first preparation but remains explicitly arena-out-of-scope because its ten freely arranged contiguous cubes require unsupported multi-cube battlefield geometry.
- Level 14 advances to 73 HP, improves **Land's Aid** to 4d6 damage/healing, and adds **Nature's Sanctuary** through the universal persistent-beneficial-zone engine: a movable 15-foot cube that grants Half Cover and the Arid Fire resistance according to its source rules.
- Level 15 advances to 78 HP, adds a level-8 slot and the 18th prepared spell **Sunburst**, reusing the certified 2024 area save-damage and timed-Blinded primitives. **Improved Elemental Fury: Potent Spellcasting** increases qualifying Druid cantrip ranges by 300 feet as compiled action data; Poison Spray, Fire Bolt, and Starry Wisp become 330/420/360 feet while Self-range Thunderclap remains unchanged.\n- Level 16 advances to 83 HP and uses the repeatable **Ability Score Improvement** feat for +2 Charisma (18→20). Wisdom, spell slots, prepared spells, and the damage/healing package remain unchanged.
- Level 17 advances to PB +6, 88 HP, 19 ordinary prepared spells, 4 Wild Shape uses, and one level-9 slot. **Foresight** is the one arena-entry opening buff and uses universal D20 Advantage/incoming-attack Disadvantage; the explicit Iron Pit exception leaves the level-9 slot unspent.
- Level 18 advances to 93 HP, a third level-5 slot, and 20 prepared spells. **Beast Spells** reuses the replacement-form spell allowlist; the new prepared spell is explicit 2024 **Barkskin** (Bonus Action, Touch, AC minimum 17, no Concentration).
- Level 19 advances to 98 HP, two level-6 slots, and 21 prepared spells. Thalen legally selects **Boon of Fate** rather than the recommended Boon of Dimensional Travel, raising Intelligence 13→14 and reusing the universal 2d4 D20 outcome-adjustment plus Initiative refill. **Regenerate** is the healing-priority prepared choice; its 1-minute casting time means Arena AI does not select it in a standard match.
- Level 20 advances to 103 HP, two level-7 slots, and 22 prepared spells. **Archdruid** reuses initiative resource refill for Evergreen Wild Shape and universal resource conversion for Nature Magician's 1–4 Wild Shape → level 2/4/6/8 spell-slot exchanges; Longevity is arena-neutral. **Ice Storm** is the damage-priority prepared choice but remains arena-out-of-scope until temporary area Difficult Terrain can be represented exactly.
- Call Lightning remains unbound until its fixed storm-cloud footprint can be represented exactly by a universal persistent-area spell primitive; it is not approximated.
