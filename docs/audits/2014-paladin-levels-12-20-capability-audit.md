# 2014 Devotion Paladin Levels 12–20 Capability Audit

## Scope and authority

This audit is anchored to the 2014 lane and the D&D SRD 5.1 Paladin / Oath of Devotion rules. It does not certify any level and must not be used to advance READY state by itself.

Current certified runtime stops at Aurelia level 11. The purpose of this document is to decompose levels 12–20 into universal combat mechanics before any new resolver is written.

## RAW progression inventory

| Level | Combat-relevant progression | Universal-engine disposition |
| --- | --- | --- |
| 12 | Ability Score Improvement | Existing canonical ability-score/derived-stat progression. No new combat primitive. |
| 13 | 4th-level spell slots; Devotion oath spells *freedom of movement*, *guardian of faith* | Spell/resource data first. Reuse existing slot resources. Audit each spell against condition/movement/summoned-area capabilities before implementation. |
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
- Aura of Protection, Aura of Devotion, and Aura of Courage are already represented in progression features through level 11.
- The universal timed-self-effect/source-owned-effect work already merged for the 2014 Monk should be preferred for Holy Nimbus duration/ownership rather than introducing another feature-specific lifecycle.

## Gaps that require focused inventory before code

1. **Cleansing Touch:** verify whether the existing generic effect-removal action can remove a spell on a touched creature without a spellcasting-ability check. If yes, this is data/resource wiring only.
2. **Purity of Spirit:** inventory the existing *protection from evil and good* implementation. The RAW behavior is creature-type gated and includes attack disadvantage plus immunity/prevention rules for charm/frighten/possession; reuse those primitives individually.
3. **Freedom of Movement:** inventory difficult-terrain immunity, magical speed reduction/paralysis/restraint prevention, grapple escape, and underwater movement. Arena-relevant portions must be composed from generic movement/condition capabilities.
4. **Guardian of Faith:** inventory stationary area/summoned hazard support before deciding whether it is runnable in the arena. Do not model it as an ordinary creature summon if the engine's summon contract would change RAW behavior.
5. **Flame Strike:** verify a save-damage action can carry both fire and radiant components through one Dexterity save and half-on-success semantics.
6. **Holy Nimbus:** verify generic start-of-turn area damage and source-creature-type-gated save advantage. Only missing generic pieces may become new engine primitives.

## Certification sequence

1. Level 12 first: canonical ASI + derived stats + Python/browser parity + generated artifact sync.
2. Level 13 only after both 4th-level combat oath spells are dispositioned accurately.
3. Level 14 after Cleansing Touch is proven to reuse or minimally extend generic effect removal.
4. Level 15 after *protection from evil and good* composition is certified.
5. Level 16 ASI.
6. Level 17 after *flame strike* parity; *commune* remains explicitly noncombat.
7. Level 18 aura-radius parameterization.
8. Level 19 ASI.
9. Level 20 Holy Nimbus as a composition of universal timed/action/resource/aura/start-turn/save-defense mechanics.

No level is READY merely because its row appears in this audit. Certification remains earned through runtime behavior, Python tests, browser parity, generated manifests, and CI.
