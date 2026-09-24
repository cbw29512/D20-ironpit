# 2014 Devotion Paladin Levels 12–20 Capability Audit

## Scope and authority

This audit is anchored to the 2014 lane and the D&D SRD 5.1 Paladin / Oath of Devotion rules. It does not certify any level and must not be used to advance READY state by itself.

Current certified runtime stops at Aurelia level 12. The purpose of this document is to decompose levels 13–20 into universal combat mechanics before any new resolver is written.

## RAW progression inventory

| Level | Combat-relevant progression | Universal-engine disposition |
| --- | --- | --- |
| 13 | 4th-level spell slots; Devotion oath spells *freedom of movement*, *guardian of faith* | Spell/resource data first. Reuse existing slot resources. Both spells require explicit disposition before level 13 can certify. |
| 14 | Cleansing Touch | Effect-removal action: action economy + Charisma-modifier uses per long rest + target spell-effect removal. Compare against existing `effect_removal_actions` / Dispel Magic machinery; do not create a Paladin-specific remover. |
| 15 | Purity of Spirit | Persistent self effect equivalent to always being under *protection from evil and good*. Compose the spell's existing universal defenses if present; otherwise identify the missing generic creature-type defense primitive. |
| 16 | Ability Score Improvement | Existing canonical ability-score/derived-stat progression. No new combat primitive. |
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
2. **Guardian of Faith:** the spell already exists in the canonical 2014 Life Cleric data, but that lane explicitly classifies it `arena-out-of-scope` / non-automated. That existing classification must not be mistaken for engine support. Devotion Paladin level 13 therefore cannot claim this spell as automated by merely reusing the Cleric data row.
3. **Freedom of Movement:** the repository contains the spell name in subclass overlay data, but no runnable 2014 universal implementation was found. Its arena-relevant behavior spans difficult-terrain immunity, prevention of magical speed reduction and paralysis/restraint, automatic escape from nonmagical restraints by spending movement, and underwater movement/attack normalization. No existing capability was found that can honestly represent the complete spell as one reusable action.
4. **Certification consequence:** level 13 remains blocked on a generic/data-driven Freedom of Movement representation and an explicit Iron Pit disposition for Guardian of Faith. Do not extend Aurelia's certified level ranges or READY manifests until those behaviors are resolved and tested.

## Gaps that require focused inventory before code

1. **Freedom of Movement:** add only generic movement/condition-prevention pieces that are genuinely absent. Do not create a spell-name resolver.
2. **Guardian of Faith:** inventory stationary area/summoned hazard support before deciding whether it is runnable in the arena. Do not model it as an ordinary creature summon if the engine's summon contract would change RAW behavior.
3. **Cleansing Touch:** verify whether the existing generic effect-removal action can remove a spell on a touched creature without a spellcasting-ability check. If yes, this is data/resource wiring only.
4. **Purity of Spirit:** reuse the existing typed defenses from *protection from evil and good* and separately inventory the possession/prevention semantics that are not yet represented.
5. **Flame Strike:** verify a save-damage action can carry both fire and radiant components through one Dexterity save and half-on-success semantics.
6. **Holy Nimbus:** verify generic start-of-turn area damage and source-creature-type-gated save advantage. Only missing generic pieces may become new engine primitives.

## Certification sequence

1. Level 12: certified on main.
2. Level 13 only after both 4th-level combat oath spells are dispositioned accurately and the 4/3/3/1 resource vector is covered by Python/browser parity.
3. Level 14 after Cleansing Touch is proven to reuse or minimally extend generic effect removal.
4. Level 15 after *protection from evil and good* composition is certified for the persistent self effect.
5. Level 16 ASI.
6. Level 17 after *flame strike* parity; *commune* remains explicitly noncombat.
7. Level 18 aura-radius parameterization.
8. Level 19 ASI.
9. Level 20 Holy Nimbus as a composition of universal timed/action/resource/aura/start-turn/save-defense mechanics.

No level is READY merely because its row appears in this audit. Certification remains earned through runtime behavior, Python tests, browser parity, generated manifests, and CI.
