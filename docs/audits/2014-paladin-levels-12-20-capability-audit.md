# 2014 Devotion Paladin Levels 12–20 Capability Audit

## Scope and authority

This audit is anchored to the 2014 lane and the D&D SRD 5.1 Paladin / Oath of Devotion rules. It does not certify any level and must not be used to advance READY state by itself.

Current certified runtime stops at Aurelia level 15. The purpose of this document is to decompose the remaining levels through 20 into universal combat mechanics before any new resolver is written.

## RAW progression inventory

| Level | Combat-relevant progression | Universal-engine disposition |
| --- | --- | --- |
| 13 | 4th-level spell slots; Devotion oath spells *freedom of movement*, *guardian of faith* | 4/3/3/1 slots. *Freedom of movement* uses universal buff/debuff counters. *Guardian of Faith* remains in RAW/Oath metadata but is arena-unavailable under the current no-summons/created-entity rule. Aurelia prepares *death ward* as the legal non-summoning 4th-level combat replacement. |
| 14 | Cleansing Touch | Effect-removal action: action economy + Charisma-modifier uses per long rest + target spell-effect removal. Compare against existing `effect_removal_actions` / Dispel Magic machinery; do not create a Paladin-specific remover. |
| 15 | Purity of Spirit | Persistent self effect equivalent to always being under *protection from evil and good*. Compose the spell's existing universal defenses if present; otherwise identify the missing generic creature-type defense primitive. |
| 16 | Ability Score Improvement | Canonical +2 Charisma ASI through existing ability-score progression. Derived Charisma modifier updates Aura of Protection, Sacred Weapon, Cleansing Touch uses, Persuasion, and spell preparation. No new combat primitive. |
| 17 | 5th-level spell slots; Devotion oath spells *commune*, *flame strike* | Slot resource is existing. *Commune* is noncombat for Iron Pit. *Flame strike* should reuse save-damage/AoE primitives with its two damage components if the current multi-component save-damage path supports them. |
| 18 | Aura improvements | Parameter change only: Aura of Protection / Courage / Devotion radius 10 ft → 30 ft. Reuse the same aura capabilities with data-driven radius. |
| 19 | Ability Score Improvement | Existing canonical ability-score/derived-stat progression. No new combat primitive. |
| 20 | Holy Nimbus | Composite timed self effect: Action activation, 1/long-rest resource, 1-minute duration, 30-ft bright-light enemy start-of-turn radiant damage, plus advantage on saves against spells cast by fiends/undead. Reuse timed-self-effect lifecycle and start-of-turn damage hooks; audit whether source-creature-type-gated save advantage is already generic before adding anything. |

## Existing engine capabilities already confirmed in the current Paladin lane

- Standard Action economy and finite `ResourceDefinition` resources.
- Spell-slot resources by spell level.
- `effect_removal_actions` are already present on Aurelia through *dispel magic*.
- Generic `OnHitDamage` already represents Improved Divine Smite without a Paladin-specific damage resolver.
- Aura of Protection, Aura of Devotion, and Aura of Courage are already represented in progression features through level 12.
- *Protection from evil and good* already composes typed attack disadvantage plus typed charm/fright immunity through `DefensiveSpellAction` / `SpellModifierEffect` rather than a Paladin-specific resolver.
- The universal timed-self-effect/source-owned-effect work already merged for the 2014 Monk should be preferred for Holy Nimbus duration/ownership rather than introducing another feature-specific lifecycle.

## Level 13 inventory result

Repository inventory after level 12 certification found:

1. **4th-level slots:** existing generic spell-slot `ResourceDefinition` is sufficient. Level 13 needs the RAW 4/3/3/1 slot vector in Paladin runtime/profile data; no new resource primitive is needed.
2. **Guardian of Faith:** preserved as an always-prepared Oath of Devotion spell in source metadata, but explicitly arena-unavailable while Iron Pit disables summoned/conjured/created combat entities. It is not automated, selected by Arena AI, or treated as a certification blocker.
3. **Freedom of Movement:** represented through universal buff-vs-debuff counter semantics. Arena-relevant behavior is difficult-terrain countering, prevention of magical Speed reduction and magical paralysis/restraint, plus automatic escape from nonmagical Grappled/Restrained by spending 5 feet of movement. The underwater clause is `ARENA_NEUTRAL` because Iron Pit environmental hospitality already lets combatants move as though in a valid native environment for their printed movement modes.
4. **Death Ward:** selected as Aurelia's legal prepared 4th-level non-summoning combat spell. It uses the universal source-owned zero-HP replacement primitive: the first qualifying drop to 0 becomes 1 HP and the ward ends. Its non-damage instant-death clause is represented by the same ward capability for future direct-death effects.
5. **Certification consequence:** level 13 requires the 4/3/3/1 slot vector plus Python/browser parity for Freedom of Movement and Death Ward. Guardian of Faith no longer blocks under the current arena contract.

## Gaps that require focused inventory before code

1. **Freedom of Movement / Death Ward:** keep both as generic source-owned buffs; no Paladin-specific resolver.
2. **Guardian of Faith:** no engine work while summons/created combat entities are disabled. Revisit only if the global summon policy changes.
3. **Cleansing Touch:** resolved as `ENGINE_EXISTS_PARAMETER_DELTA`. The generic effect-removal action now supports level-0 feature actions; Cleansing Touch uses an Action, 5-foot self/willing-ally targeting, automatic removal through spell level 9, no ability check, no spell slot, and Charisma-modifier uses. Arena AI orders it before Dispel Magic so a class-feature use is not replaced by an unnecessary spell-slot expenditure.
4. **Purity of Spirit:** resolved as a permanent source-owned buff compiled into the existing typed defenses from *protection from evil and good*: qualifying creature types have Disadvantage attacking Aurelia and cannot Charm or Frighten her. Possession remains `ARENA_NEUTRAL` until a certified possession mechanic enters active content.
5. **Flame Strike:** verify a save-damage action can carry both fire and radiant components through one Dexterity save and half-on-success semantics.
6. **Holy Nimbus:** verify generic start-of-turn area damage and source-creature-type-gated save advantage. Only missing generic pieces may become new engine primitives.

## Certification sequence

1. Level 12: certified on main.
2. Level 13 after the 4/3/3/1 resource vector, Freedom of Movement, and Death Ward pass Python/browser parity; Guardian of Faith remains source-visible but arena-unavailable by contract.
3. Level 14: Cleansing Touch reuses generic effect removal; certification requires exact-head Python/browser/resource parity before READY.
4. Level 15 after Purity of Spirit compiles the existing *protection from evil and good* typed defenses as permanent passive modifiers with Python/browser parity and exact-head certification.
5. Level 16: canonical +2 Charisma ASI, 4/3/3/2 slots retained, prepared capacity rises to 12; legal Find Steed remains summon-unavailable and Create Food and Water remains noncombat under existing arena contracts.
6. Level 17 after *flame strike* parity; *commune* remains explicitly noncombat.
7. Level 18 aura-radius parameterization.
8. Level 19 ASI.
9. Level 20 Holy Nimbus as a composition of universal timed/action/resource/aura/start-turn/save-defense mechanics.

No level is READY merely because its row appears in this audit. Certification remains earned through runtime behavior, Python tests, browser parity, generated manifests, and CI.
