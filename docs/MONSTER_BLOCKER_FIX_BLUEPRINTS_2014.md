# 2014 monster blocker fix blueprints — 124 of 124

> **This is a planning queue, not a declaration of implementation, verification or RAW certification.** 2014 is first. No automation or production publishing is enabled by these documents.

Pinned baseline: `main` **642a6154e99448b31e0427599889724000ad95ec**. Catalog: `backend/app/content/data/srd_5_1_monsters_catalog.json` (**327 source records**). Generator's 2014 blockers at this commit: **203 admitted, 124 blocked**. Blocker categories overlap. In-flight PRs may change the count on merge; the generated list always takes precedence.

## Execution contract

1. The printed source record and SOUL/rules contracts decide semantics; abilities with different names but equivalent behavior share the same effect ID. 2014/2024 parameter fingerprints remain isolated.
2. Every entry below records **exact source names and snippets** and a proposed **fix route** for each blocker; it is triaged and QUEUED but **not yet certified**. `supported` universal components are reuse candidates; `partial`/`unsupported` represent known gaps.
3. Work by shared family: source review of one small packet → existing Python+browser primitive → source binding → real action/event and fight-reset tests → generator refresh → exact-head CI → merge → remove resolved blockers. No monster-name logic.
4. While code CI runs, prepare the **next independent monster packet**. Keep one owner per shared runtime/serializer/generated output; do not duplicate old PR branches. A failed/unknown source clause stays blocked, not silently approximated.
5. A monster is complete only after all its independent blocker categories clear and actual Python/browser combat certification agrees. Explicit user-approved arena exclusions retain printed source and must not masquerade as implementation.
6. After each merge regenerate `docs/MONSTER_BLOCKERS_2014.md` and `docs/UNIVERSAL_MECHANIC_INVENTORY.md`, then reconcile this pinned snapshot and [parent execution list](https://github.com/cbw29512/D20-ironpit/issues/675). Do not rescan all printed JSON for every individual PR.

## Prioritized prepared fixes and dependencies

| Stage | Mechanic / monsters | Work item |
|---|---|---|
| Code submitted / pending certification | Heated Body — Azer, Salamander, Remorhaz | [#673](https://github.com/cbw29512/D20-ironpit/pull/673): shared passive retaliation; only Azer is candidate for full admission |
| Old submitted PRs / review | Assassinate, Evasion, Sneak Attack — Assassin | #664, #665, #666 (Surprise semantics and generated outputs still gate) |
| Old submitted PR / review | Change Shape, metallic dragons | #663, verify exact approved noncombat classification for every variant |
| Foundation overlap | Steadfast — Bearded Devil | #662 conditional active-ally foundation, old overlapping #654; Beard/Glaive separate |
| Prepared source-to-engine packet | Petrifying Gaze — Basilisk + Medusa | [#676](https://github.com/cbw29512/D20-ironpit/issues/676) |
| Prepared source-to-engine packet | Deadly Leap — Bulette | [#677](https://github.com/cbw29512/D20-ironpit/issues/677) |
| Prepared source-to-engine packet | Fetid Cloud — Dretch | [#678](https://github.com/cbw29512/D20-ironpit/issues/678) |
| Prepared source-to-engine packet | Luring Song — Harpy | [#679](https://github.com/cbw29512/D20-ironpit/issues/679) |
| Next independent source audit | Blind Senses; Leadership; Tail Spike Regrowth; Rock Catching | Grimlock, Knight, Manticore, Stone Giant; see packets below |

## Existing shared mechanics to reuse (actual inventory status)

| Capability | Status |
|---|---|
| `action-economy` | **supported** |
| `saving-throws` | **supported** |
| `typed-damage-resistance-immunity-vulnerability` | **supported** |
| `timed-condition-lifecycle-repeat-save` | **supported** |
| `condition-immunity` | **supported** |
| `recharge` | **supported** |
| `legendary-actions` | **supported** |
| `multiattack-extra-attack` | **supported** |
| `grappled-restrained-escape` | **supported** |
| `ongoing-periodic-damage` | **supported** |
| `area-target-placement` | **supported** |
| `generic-limited-use-resources` | **partial** |
| `generic-death-triggers` | **partial** |
| `generic-reaction-trigger-grammar` | **partial** |
| `multiple-persistent-riders-on-one-attack` | **unsupported** |
| `summons-transformations-splitting` | **unsupported** |
| `forced-movement-push-pull-teleport` | **partial** |
| `cover-line-of-sight-obscurement` | **partial** |

## Family batches (each monster assigned one primary review lane)

### RECHARGE / RESOURCES (12)

- Aboleth
- Air Elemental
- Chain Devil
- Clay Golem
- Darkmantle
- Ettercap
- Giant Spider
- Ice Devil
- Knight
- Manticore
- Shield Guardian
- Storm Giant

### SPELLCASTING (18)

- Acolyte
- Archmage
- Cloud Giant
- Cult Fanatic
- Deep Gnome (Svirfneblin)
- Drider
- Drow
- Druid
- Flameskull
- Glabrezu
- Green Hag
- Gynosphinx
- Lamia
- Mage
- Planetar
- Priest
- Rakshasa
- Spirit Naga

### FEAR / CHARM / STATUS (20)

- Adult Bronze Dragon
- Adult Gold Dragon
- Adult Silver Dragon
- Ancient Brass Dragon
- Ancient Bronze Dragon
- Ancient Copper Dragon
- Ancient Gold Dragon
- Ancient Silver Dragon
- Androsphinx
- Banshee
- Dretch
- Dryad
- Gibbering Mouther
- Guardian Naga
- Harpy
- Pit Fiend
- Succubus/Incubus
- Tarrasque
- Vampire
- Vrock

### ATTACK RIDERS / MULTICOMPONENT DAMAGE (4)

- Assassin
- Bugbear
- Erinyes
- Shadow

### PASSIVE RETALIATION / DAMAGE AURA (8)

- Azer
- Balor
- Barbed Devil
- Black Pudding
- Fire Elemental
- Gray Ooze
- Remorhaz
- Salamander

### GAZE / SIGHT / INVISIBILITY (14)

- Basilisk
- Cloaker
- Duergar
- Gelatinous Cube
- Ghost
- Grimlock
- Imp
- Invisible Stalker
- Lich
- Medusa
- Quasit
- Solar
- Sprite
- Will-o'-Wisp

### ALLY / AURA (1)

- Bearded Devil

### RESTRAINT / SWALLOW (10)

- Behir
- Chuul
- Giant Frog
- Giant Toad
- Kraken
- Otyugh
- Roper
- Rug of Smothering
- Shambling Mound
- Water Elemental

### AREA / SAVE ACTIONS (3)

- Bulette
- Mummy Lord
- Spectator

### SHAPECHANGE / TRANSFORMATION (11)

- Couatl
- Deva
- Doppelganger
- Mimic
- Night Hag
- Oni
- Werebear
- Wereboar
- Wererat
- Weretiger
- Werewolf

### DEATH / HP-LIFECYCLE (8)

- Djinni
- Dust Mephit
- Efreeti
- Ice Mephit
- Magma Mephit
- Magmin
- Steam Mephit
- Vampire Spawn

### SOURCE-ONLY / ARENA POLICY (3)

- Frog
- Sea Horse
- Stirge

### INFORMATION / NONCOMBAT (2)

- Homunculus
- Pseudodragon

### OTHER / SOURCE BINDING (6)

- Horned Devil
- Mummy
- Purple Worm
- Rust Monster
- Sea Hag
- Shrieker

### REACTIONS / TRIGGERS (3)

- Hydra
- Marilith
- Stone Giant

### POSITION / MOVEMENT (1)

- Nightmare

## Per-monster source review and exact blocker-fix packets

Every entry below contains: blocker categories, printed abilities, a fix plan for **each** blocker category, shared reuse candidates, and source excerpts when present. Excerpts ending in `[…]` must be reopened from the pinned source to check every qualifier. All status: **QUEUED FOR IMPLEMENTATION**, not done.

### 001. Aboleth — RECHARGE / RESOURCES

**Blocking categories:** `attack:incomplete`, `mechanic:legendary`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Mucous Cloud`, `Probing Telepathy`.

**Printed actions:** `Multiattack`, `Tentacle`, `Tail`, `Enslave (3/Day)`.

**Printed legendary choices:** `Detect`, `Tail Swipe`, `Psychic Drain`.

**Incomplete source attacks:** `Tentacle`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `legendary-actions` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Mucous Cloud:** Mucous Cloud. While underwater, the aboleth is surrounded by transformative mucus. A creature that touches the aboleth or that hits it with a melee attack while within 5 feet of it must make a DC 14 Constitution saving throw. On a failure, the creature is diseased for 1d4 hours. The diseased creature can breathe only underwater.
- **Trait — Probing Telepathy:** Probing Telepathy. If a creature communicates telepathically with the aboleth, the aboleth learns the creature's greatest desires if the aboleth can see the creature.
- **Action — Enslave (3/Day):** Enslave (3/Day). The aboleth targets one creature it can see within 30 feet of it. The target must succeed on a DC 14 Wisdom saving throw or be magically charmed by the aboleth until the aboleth dies or until it is on a different plane of existence from the target. The charmed target is under the aboleth's control and can't take reactions, and the aboleth and the target can communicate telepathically with each other over any distance.
- **Legendary action — Detect:** Detect. The aboleth makes a Wisdom (Perception) check.
- **Legendary action — Tail Swipe:** Tail Swipe. The aboleth makes one tail attack.
- **Legendary action — Psychic Drain:** Psychic Drain (Costs 2 Actions). One creature charmed by the aboleth takes 10 (3d6) psychic damage, and the aboleth regains hit points equal to the damage the creature takes.
- **Incomplete attack — Tentacle:** Tentacle. Melee Weapon Attack: +9 to hit, reach 10 ft., one target. Hit: 12 (2d6 + 5) bludgeoning damage. If the target is a creature, it must succeed on a DC 14 Constitution saving throw or become diseased. The disease has no effect for 1 minute and can be removed by any magic that cures disease. After 1 minute, the diseased creature's skin becomes translucent and slimy, the creature can't regain hit points unless it is underwater, and the disease can be removed only by heal or another disease-curing spell of 6th level or higher. When the creature is outside a body of water, it takes 6 (1d12) acid damage every 10 minutes unless moi […]

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 002. Acolyte — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Club`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **User decision / queued:** **LOCKED: Light is combat-relevant and remains available**, to illuminate nonmagical darkness, reveal darkness-dependent stealth, or trigger bright-light sensitivity as appropriate. It cannot counter 2014 magical Darkness (overlapping Darkness dispels Light cantrip). Thaumaturgy stays on the original stat block, but AI never casts it because it has no relevant arena combat purpose. Preserve all remaining spells and use existing spell primitives. Not yet implemented/certified.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The acolyte is a 1st-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 12, +4 to hit with spell attacks). The acolyte has following cleric spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 003. Adult Bronze Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Lightning Breath`, `Repulsion Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **Linked implementation/decision:** #663 Change Shape source policy candidate.
- **Previously recorded specific ruling / dependency:** - **Identified remaining action:** Change Shape; the Bronze Repulsion audit explicitly names this as the independent extra-action blocker.
- **Previously recorded specific ruling / dependency:** - **Fix plan:** Read the exact 2014 Change Shape source and compare against existing transformation/replacement-form and arena restrictions. If transformation is allowed and representable, bind it declaratively using the shared form/state primitive and preserve the original dragon's legal capabilities. If Pit policy excludes the action, document the existing rule and classifier consequence rather than invent a replacement. Verify attack choices, stats/HP/form return and browser/Python parity as applicable.
- **Previously recorded specific ruling / dependency:** - **Avoid rework:** Do not touch Repulsion Breath or add a dragon-specific transformation resolver. Next classification decision is the permitted scope of Change Shape under the locked Pit rules.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 17 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Lightning Breath:** Lightning Breath. The dragon exhales lightning in a 90- foot line that is 5 feet wide. Each creature in that line must make a DC 19 Dexterity saving throw, taking 66 (12d10) lightning damage on a failed save, or half as much damage on a successful one.
- **Action — Repulsion Breath:** Repulsion Breath. The dragon exhales repulsion energy in a 30-foot cone. Each creature in that area must succeed on a DC 19 Strength saving throw. On a failed save, the creature is pushed 60 feet away from the dragon.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 004. Adult Gold Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Fire Breath`, `Weakening Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 21 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Fire Breath:** Fire Breath. The dragon exhales fire in a 60-foot cone. Each creature in that area must make a DC 21 Dexterity saving throw, taking 66 (12d10) fire damage on a failed save, or half as much damage on a successful one.
- **Action — Weakening Breath:** Weakening Breath. The dragon exhales gas in a 60-foot cone. Each creature in that area must succeed on a DC 21 Strength saving throw or have disadvantage on Strength-based attack rolls, Strength checks, and Strength saving throws for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 005. Adult Silver Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Cold Breath`, `Paralyzing Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 18 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Cold Breath:** Cold Breath. The dragon exhales an icy blast in a 60-foot cone. Each creature in that area must make a DC 20 Constitution saving throw, taking 58 (13d8) cold damage on a failed save, or half as much damage on a successful one.
- **Action — Paralyzing Breath:** Paralyzing Breath. The dragon exhales paralyzing gas in a 60-foot cone. Each creature in that area must succeed on a DC 20 Constitution saving throw or be paralyzed for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 006. Air Elemental — RECHARGE / RESOURCES

**Blocking categories:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Air Form`.

**Printed actions:** `Multiattack`, `Slam`, `Whirlwind (Recharge 4–6)`.

**Printed action recharge mapping:** `{"whirlwind":4}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Air Form: reuse movement, spaces and creature occupancy constraints; do not reduce to presentation.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Air Form:** Air Form. The elemental can enter a hostile creature's space and stop there. It can move through a space as narrow as 1 inch wide without squeezing.
- **Action — Whirlwind (Recharge 4–6):** Whirlwind (Recharge 4–6). Each creature in the elemental's space must make a DC 13 Strength saving throw. On a failure, a target takes 15 (3d8 + 2) bludgeoning damage and is flung up 20 feet away from the elemental in a random direction and knocked prone. If a thrown target strikes an object, such as a wall or floor, the target takes 3 (1d6) bludgeoning damage for every 10 feet it was thrown. If the target is thrown at another creature, that creature must succeed on a DC 13 Dexterity saving throw or take the same damage and be knocked prone.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 007. Ancient Brass Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Fire Breath`, `Sleep Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 18 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons:
- **Action — Fire Breath:** Fire Breath. The dragon exhales fire in an 90-foot line that is 10 feet wide. Each creature in that line must make a DC 21 Dexterity saving throw, taking 56 (16d6) fire damage on a failed save, or half as much damage on a successful one.
- **Action — Sleep Breath:** Sleep Breath. The dragon exhales sleep gas in a 90-foot cone. Each creature in that area must succeed on a DC 21 Constitution saving throw or fall unconscious for 10 minutes. This effect ends for a creature if the creature takes damage or someone uses an action to wake it.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 008. Ancient Bronze Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Lightning Breath`, `Repulsion Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 20 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Lightning Breath:** Lightning Breath. The dragon exhales lightning in a 120-foot line that is 10 feet wide. Each creature in that line must make a DC 23 Dexterity saving throw, taking 88 (16d10) lightning damage on a failed save, or half as much damage on a successful one.
- **Action — Repulsion Breath:** Repulsion Breath. The dragon exhales repulsion energy in a 30-foot cone. Each creature in that area must succeed on a DC 23 Strength saving throw. On a failed save, the creature is pushed 60 feet away from the dragon.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 009. Ancient Copper Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Acid Breath`, `Slowing Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 19 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Acid Breath:** Acid Breath. The dragon exhales acid in an 90-foot line that is 10 feet wide. Each creature in that line must make a DC 22 Dexterity saving throw, taking 63 (14d8) acid damage on a failed save, or half as much damage on a successful one.
- **Action — Slowing Breath:** Slowing Breath. The dragon exhales gas in a 90-foot cone. Each creature in that area must succeed on a DC 22 Constitution saving throw. On a failed save, the creature can't use reactions, its speed is halved, and it can't make more than one attack on its turn. In addition, the creature can use either an action or a bonus action on its turn, but not both. These effects last for 1 minute. The creature can repeat the saving throw at the end of each of its turns, ending the effect on itself with a successful save.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 010. Ancient Gold Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Fire Breath`, `Weakening Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 24 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Fire Breath:** Fire Breath. The dragon exhales fire in a 90-foot cone. Each creature in that area must make a DC 24 Dexterity saving throw, taking 71 (13d10) fire damage on a failed save, or half as much damage on a successful one.
- **Action — Weakening Breath:** Weakening Breath. The dragon exhales gas in a 90-foot cone. Each creature in that area must succeed on a DC 24 Strength saving throw or have disadvantage on Strength-based attack rolls, Strength checks, and Strength saving throws for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 011. Ancient Silver Dragon — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail`, `Frightful Presence`, `Breath Weapons (Recharge 5–6)`, `Cold Breath`, `Paralyzing Breath`, `Change Shape`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Frightful Presence:** Frightful Presence. Each creature of the dragon's choice that is within 120 feet of the dragon and aware of it must succeed on a DC 21 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the dragon's Frightful Presence for the next 24 hours.
- **Action — Breath Weapons (Recharge 5–6):** Breath Weapons (Recharge 5–6). The dragon uses one of the following breath weapons.
- **Action — Cold Breath:** Cold Breath. The dragon exhales an icy blast in a 90-foot cone. Each creature in that area must make a DC 24 Constitution saving throw, taking 67 (15d8) cold damage on a failed save, or half as much damage on a successful one.
- **Action — Paralyzing Breath:** Paralyzing Breath. The dragon exhales paralyzing gas in a 90-foot cone. Each creature in that area must succeed on a DC 24 Constitution saving throw or be paralyzed for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Change Shape:** Change Shape. The dragon magically polymorphs into a humanoid or beast that has a challenge rating no higher than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the dragon's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 012. Androsphinx — FEAR / CHARM / STATUS

**Blocking categories:** `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Inscrutable`, `Spellcasting`.

**Printed actions:** `Multiattack`, `Claw`, `Roar (3/Day)`, `First Roar`, `Second Roar`, `Third Roar`.

**Printed legendary choices:** `Claw Attack`, `Teleport (Costs 2 Actions)`, `Cast a Spell (Costs 3 Actions)`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `legendary-actions` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Inscrutable:** Inscrutable. The sphinx is immune to any effect that would sense its emotions or read its thoughts, as well as any divination spell that it refuses. Wisdom (Insight) checks made to ascertain the sphinx's intentions or sincerity have disadvantage.
- **Trait — Spellcasting:** Spellcasting. The sphinx is a 12th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 18, +10 to hit with spell attacks). It requires no material components to cast its spells. The sphinx has the following cleric spells prepared:
- **Action — Roar (3/Day):** Roar (3/Day). The sphinx emits a magical roar. Each time it roars before finishing a long rest, the roar is louder and the effect is different, as detailed below. Each creature within 500 feet of the sphinx and able to hear the roar must make a saving throw.
- **Action — First Roar:** First Roar. Each creature that fails a DC 18 Wisdom saving throw is frightened for 1 minute. A frightened creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Second Roar:** Second Roar. Each creature that fails a DC 18 Wisdom saving throw is deafened and frightened for 1 minute. A frightened creature is paralyzed and can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Action — Third Roar:** Third Roar. Each creature makes a DC 18 Constitution saving throw. On a failed save, a creature takes 44 (8d10) thunder damage and is knocked prone. On a successful save, the creature takes half as much damage and isn't knocked prone.
- **Legendary action — Claw Attack:** Claw Attack. The sphinx makes one claw attack.
- **Legendary action — Teleport (Costs 2 Actions):** Teleport (Costs 2 Actions). The sphinx magically teleports, along with any equipment it is wearing or carrying, up to 120 feet to an unoccupied space it can see.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 013. Archmage — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Dagger`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Disguise Self — user decision / queued:** Retain printed spell on source/card; Archmage AI never casts it in Iron Pit (appearance-only, no combat impact). Route via shared arena-inert spell selection, not a bespoke Archmage resolver. Not implemented/certified.
- **Previously recorded specific ruling / dependency:** - **Detect Magic — user decision / queued:** Preserve printed spell but never select it as an Iron Pit combat action; source remains intact. Not implemented/certified.
- **Previously recorded specific ruling / dependency:** - **Identify — user decision / queued:** Keep the printed spell but never cast it in Iron Pit. Implement by shared noncombat-spell choice exclusion; not certified.
- **Previously recorded specific ruling / dependency:** - **Detect Thoughts — user decision / queued:** Printed spell retained; AI never casts it in arena. Shared noncombat-spell selection exclusion; not implemented/certified.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The archmage is an 18th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 17, +9 to hit with spell attacks). The archmage can cast disguise self and invisibility at will and has the following wizard spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 014. Assassin — ATTACK RIDERS / MULTICOMPONENT DAMAGE

**Blocking categories:** `source:trait`. **Unbound named traits:** `Assassinate`, `Evasion`, `Sneak Attack`.

**Printed actions:** `Multiattack`, `Shortsword`, `Light Crossbow`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** PRs #664, #665, #666 (unmerged).
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Assassinate/Sneak Attack/Evasion: reuse rogue pregen combat primitives where semantics match.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Assassinate:** Assassinate. During its first turn, the assassin has advantage on attack rolls against any creature that hasn't taken a turn. Any hit the assassin scores against a surprised creature is a critical hit.
- **Trait — Evasion:** Evasion. If the assassin is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, the assassin instead takes no damage if it succeeds on the saving throw, and only half damage if it fails.
- **Trait — Sneak Attack:** Sneak Attack. Once per turn, the assassin deals an extra 14 (4d6) damage when it hits a target with a weapon attack and has advantage on the attack roll, or when the target is within 5 feet of an ally of the assassin that isn't incapacitated and the assassin doesn't have disadvantage on the attack roll.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 015. Azer — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `source:trait`. **Unbound named traits:** `Heated Body`.

**Printed actions:** `Warhammer`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** PR #673 Heated Body (not merged at planning snapshot).
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Heated Body: use existing typed retaliatory fire damage and add/reuse generic contact trigger after checking hit-versus-touch distinction.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Heated Body:** Heated Body. A creature that touches the azer or hits it with a melee attack while within 5 feet of it takes 5 (1d10) fire damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 016. Balor — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Death Throes`, `Fire Aura`.

**Printed actions:** `Multiattack`, `Longsword`, `Whip`, `Teleport`.

**Incomplete source attacks:** `Longsword`, `Whip`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Throes:** Death Throes. When the balor dies, it explodes, and each creature within 30 feet of it must make a DC 20 Dexterity saving throw, taking 70 (20d6) fire damage on a failed save, or half as much damage on a successful one. The explosion ignites flammable objects in that area that aren't being worn or carried, and it destroys the balor's weapons.
- **Trait — Fire Aura:** Fire Aura. At the start of each of the balor's turns, each creature within 5 feet of it takes 10 (3d6) fire damage, and flammable objects in the aura that aren't being worn or carried ignite. A creature that touches the balor or hits it with a melee attack while within 5 feet of it takes 10 (3d6) fire damage.
- **Incomplete attack — Longsword:** Longsword. Melee Weapon Attack: +14 to hit, reach 10 ft., one target. Hit: 21 (3d8 + 8) slashing damage plus 13 (3d8) lightning damage. If the balor scores a critical hit, it rolls damage dice three times, instead of twice.
- **Incomplete attack — Whip:** Whip. Melee Weapon Attack: +14 to hit, reach 30 ft., one target. Hit: 15 (2d6 + 8) slashing damage plus 10 (3d6) fire damage, and the target must succeed on a DC 20 Strength saving throw or be pulled up to 25 feet toward the balor.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 017. Banshee — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Detect Life`.

**Printed actions:** `Corrupting Touch`, `Horrifying Visage`, `Wail (1/Day)`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Detect Life:** Detect Life. The banshee can magically sense the presence of creatures up to 5 miles away that aren’t undead or constructs. She knows the general direction they’re in but not their exact locations.
- **Action — Horrifying Visage:** Horrifying Visage. Each non-undead creature within 60 feet of the banshee that can see her must succeed on a DC 13 Wisdom saving throw or be frightened for 1 minute. A frightened target can repeat the saving throw at the end of each of its turns, with disadvantage if the banshee is within line of sight, ending the effect on itself on a success. If a target’s saving throw is successful or the effect ends for it, the target is immune to the banshee’s Horrifying Visage for the next 24 hours.
- **Action — Wail (1/Day):** Wail (1/Day). The banshee releases a mournful wail, provided that she isn’t in sunlight. This wail has no effect on constructs and undead. All other creatures within 30 feet of her that can hear her must make a DC 13 Constitution saving throw. On a failure, a creature drops to 0 hit points. On a success, a creature takes 10 (3d6) psychic damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 018. Barbed Devil — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:range`, `source:trait`. **Unbound named traits:** `Barbed Hide`.

**Printed actions:** `Multiattack`, `Claw`, `Tail`, `Hurl Flame`.

**Fix queue for this monster:**
- **`attack:range`:** Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Barbed Hide: reuse contact retaliation; verify printed trigger and damage.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported); `melee-ranged-range-bands` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Barbed Hide:** Barbed Hide. At the start of each of its turns, the barbed devil deals 5 (1d10) piercing damage to any creature grappling it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 019. Basilisk — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:trait`. **Unbound named traits:** `Petrifying Gaze`.

**Printed actions:** `Bite`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** Ticket #676, paired Medusa.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Petrifying Gaze: source-triggered sight/save and staged Restrained/Petrified timing; check generic gaze predicate.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Petrifying Gaze:** Petrifying Gaze. If a creature starts its turn within 30 feet of the basilisk and the two of them can see each other, the basilisk can force the creature to make a DC 12 Constitution saving throw if the basilisk isn't incapacitated. On a failed save, the creature magically begins to turn to stone and is restrained. It must repeat the saving throw at the end of its next turn. On a success, the effect ends. On a failure, the creature is petrified until freed by the greater restoration spell or other magic.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 020. Bearded Devil — ALLY / AURA

**Blocking categories:** `attack:complex`, `attack:incomplete`, `source:trait`. **Unbound named traits:** `Steadfast`.

**Printed actions:** `Multiattack`, `Beard`, `Glaive`.

**Incomplete source attacks:** `Beard`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** #662 live-ally predicate pending; #654 old overlap.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** M-025 Steadfast: conditional Frightened immunity requires live active ally; PR #654 partially implemented, not certified. Then Beard: save -> Poisoned plus healing restriction; Glaive: stacking 1d10 ongoing wound, cleared on magical healing (Pit globally disallows Medicine checks).

**Reusable universal capabilities to inspect:** `auras` (supported); `condition-immunity` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Steadfast:** Steadfast. The devil can't be frightened while it can see an allied creature within 30 feet of it.
- **Incomplete attack — Beard:** Beard. Melee Weapon Attack: +5 to hit, reach 5 ft., one creature. Hit: 6 (1d8 + 2) piercing damage, and the target must succeed on a DC 12 Constitution saving throw or be poisoned for 1 minute. While poisoned in this way, the target can't regain hit points. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 021. Behir — RESTRAINT / SWALLOW

**Blocking categories:** `mechanic:recharge`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Constrict`, `Lightning Breath (Recharge 5–6)`, `Swallow`.

**Printed action recharge mapping:** `{"lightning-breath":5}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported); `recharge` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Lightning Breath (Recharge 5–6):** Lightning Breath (Recharge 5–6). The behir exhales a line of lightning that is 20 feet long and 5 feet wide. Each creature in that line must make a DC 16 Dexterity saving throw, taking 66 (12d10) lightning damage on a failed save, or half as much damage on a successful one.
- **Action — Swallow:** Swallow. The behir makes one bite attack against a Medium or smaller target it is grappling. If the attack hits, the target is also swallowed, and the grapple ends. While swallowed, the target is blinded and restrained, it has total cover against attacks and other effects outside the behir, and it takes 21 (6d6) acid damage at the start of each of the behir's turns. A behir can have only one creature swallowed at a time.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 022. Black Pudding — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Corrosive Form`.

**Printed actions:** `Pseudopod`.

**Printed reactions:** `Split`.

**Incomplete source attacks:** `Pseudopod`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Corrosive Form:** Corrosive Form. A creature that touches the pudding or hits it with a melee attack while within 5 feet of it takes 4 (1d8) acid damage. Any nonmagical weapon made of metal or wood that hits the pudding corrodes. After dealing damage, the weapon takes a permanent and cumulative −1 penalty to damage rolls. If its penalty drops to −5, the weapon is destroyed.
- **Incomplete attack — Pseudopod:** Pseudopod. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 6 (1d6 + 3) bludgeoning damage plus 18 (4d8) acid damage. In addition, nonmagical armor worn by the target is partly dissolved and takes a permanent and cumulative −1 penalty to the AC it offers. The armor is destroyed if the penalty reduces its AC to 10.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 023. Bugbear — ATTACK RIDERS / MULTICOMPONENT DAMAGE

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Surprise Attack`.

**Printed actions:** `Morningstar`, `Javelin`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Surprise Attack:** Surprise Attack. If the bugbear surprises a creature and hits it with an attack during the first round of combat, the target takes an extra 7 (2d6) damage from the attack.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 024. Bulette — AREA / SAVE ACTIONS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Bite`, `Deadly Leap`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **Linked implementation/decision:** Ticket #677.
- **Previously recorded specific ruling / dependency:** - **Deadly Leap queued / approved arena semantics:** Landing occupies a 10×10-foot (2×2 square) AoE; every enemy overlapping a landing square resolves its own DC 16 Strength-or-Dexterity (better available) save. On failure, roll 3d6+4 bludgeoning plus 3d6+4 slashing, apply typed resistance/immunity/vulnerability independently, and inflict shared Prone. On success, half damage per component after the save, apply defenses, no Prone; 5-ft push deliberately omitted in Iron Pit. A legal 15-ft jump remains required. AI prioritizes leap on opening turn when eligible; ability remains available subsequently. **Queued, not implemented/certified.**

**Reusable universal capabilities to inspect:** `area-target-placement` (supported); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Deadly Leap:** Deadly Leap. If the bulette jumps at least 15 feet as part of its movement, it can then use this action to land on its feet in a space that contains one or more other creatures. Each of those creatures must succeed on a DC 16 Strength or Dexterity saving throw (target's choice) or be knocked prone and take 14 (3d6 + 4) bludgeoning damage plus 14 (3d6 + 4) slashing damage. On a successful save, the creature takes only half the damage, isn't knocked prone, and is pushed 5 feet out of the bulette's space into an unoccupied space of the creature's choice. If no unoccupied space is within range, the creature instead falls prone in the bu […]

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 025. Chain Devil — RECHARGE / RESOURCES

**Blocking categories:** `attack:complex`, `source:extra-action`, `source:reaction`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Chain`, `Animate Chains (Recharges after a Short or Long Rest)`.

**Printed reactions:** `Unnerving Mask`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:reaction`:** Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `generic-reaction-trigger-grammar` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Animate Chains (Recharges after a Short or Long Rest):** Animate Chains (Recharges after a Short or Long Rest). Up to four chains the devil can see within 60 feet of it magically sprout razor-edged barbs and animate under the devil's control, provided that the chains aren't being worn or carried.
- **Reaction — Unnerving Mask:** Unnerving Mask. When a creature the devil can see starts its turn within 30 feet of the devil, the devil can create the illusion that it looks like one of the creature's departed loved ones or bitter enemies. If the creature can see the devil, it must succeed on a DC 14 Wisdom saving throw or be frightened until the end of its turn.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 026. Chuul — RESTRAINT / SWALLOW

**Blocking categories:** `attack:incomplete`, `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Sense Magic`.

**Printed actions:** `Multiattack`, `Pincer`, `Tentacles`.

**Incomplete source attacks:** `Pincer`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Sense Magic:** Sense Magic. The chuul senses magic within 120 feet of it at will. This trait otherwise works like the detect magic spell but isn't itself magical.
- **Action — Tentacles:** Tentacles. One creature grappled by the chuul must succeed on a DC 13 Constitution saving throw or be poisoned for 1 minute. Until this poison ends, the target is paralyzed. The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.
- **Incomplete attack — Pincer:** Pincer. Melee Weapon Attack: +6 to hit, reach 10 ft., one target. Hit: 11 (2d6 + 4) bludgeoning damage. The target is grappled (escape DC 14) if it is a Large or smaller creature and the chuul doesn't have two other creatures grappled.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 027. Clay Golem — RECHARGE / RESOURCES

**Blocking categories:** `mechanic:recharge`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Slam`, `Haste (Recharge 5–6)`.

**Printed action recharge mapping:** `{"haste":5}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Haste (Recharge 5–6):** Haste (Recharge 5–6). Until the end of its next turn, the golem magically gains a +2 bonus to its AC, has advantage on Dexterity saving throws, and can use its slam attack as a bonus action.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 028. Cloaker — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Damage Transfer`, `Light Sensitivity`.

**Printed actions:** `Multiattack`, `Bite`, `Tail`, `Moan`, `Phantasms (Recharges after a Short or Long Rest)`.

**Incomplete source attacks:** `Bite`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Damage Transfer:** Damage Transfer. While attached to a creature, the cloaker takes only half the damage dealt to it (rounded down), and that creature takes the other half.
- **Trait — Light Sensitivity:** Light Sensitivity. While in bright light, the cloaker has disadvantage on attack rolls and Wisdom (Perception) checks that rely on sight.
- **Action — Moan:** Moan. Each creature within 60 feet of the cloaker that can hear its moan and that isn't an aberration must succeed on a DC 13 Wisdom saving throw or become frightened until the end of the cloaker's next turn. If a creature's saving throw is successful, the creature is immune to the cloaker's moan for the next 24 hours.
- **Action — Phantasms (Recharges after a Short or Long Rest):** Phantasms (Recharges after a Short or Long Rest). The cloaker magically creates three illusory duplicates of itself if it isn't in bright light. The duplicates move with it and mimic its actions, shifting position so as to make it impossible to track which cloaker is the real one. If the cloaker is ever in an area of bright light, the duplicates disappear.
- **Incomplete attack — Bite:** Bite. Melee Weapon Attack: +6 to hit, reach 5 ft., one creature. Hit: 10 (2d6 + 3) piercing damage, and if the target is Large or smaller, the cloaker attaches to it. If the cloaker has advantage against the target, the cloaker attaches to the target's head, and the target is blinded and unable to breathe while the cloaker is attached. While attached, the cloaker can make this attack only against the target and has advantage on the attack roll. The cloaker can detach itself by spending 5 feet of its movement. A creature, including the target, can take its action to detach the cloaker by succeeding on a DC 16 Strength check.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 029. Cloud Giant — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Morningstar`, `Rock`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The giant's innate spellcasting ability is Charisma. It can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 030. Couatl — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`, `Shielded Mind`.

**Printed actions:** `Bite`, `Constrict`, `Change Shape`.

**Incomplete source attacks:** `Bite`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The couatl's spellcasting ability is Charisma (spell save DC 14). It can innately cast the following spells, requiring only verbal components:
- **Trait — Shielded Mind:** Shielded Mind. The couatl is immune to scrying and to any effect that would sense its emotions, read its thoughts, or detect its location.
- **Action — Change Shape:** Change Shape. The couatl magically polymorphs into a humanoid or beast that has a challenge rating equal to or less than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the couatl's choice).
- **Incomplete attack — Bite:** Bite. Melee Weapon Attack: +8 to hit, reach 5 ft., one creature. Hit: 8 (1d6 + 5) piercing damage, and the target must succeed on a DC 13 Constitution saving throw or be poisoned for 24 hours. Until this poison ends, the target is unconscious. Another creature can use an action to shake the target awake.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 031. Cult Fanatic — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Multiattack`, `Dagger`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The fanatic is a 4th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 11, +3 to hit with spell attacks). The fanatic has the following cleric spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 032. Darkmantle — RECHARGE / RESOURCES

**Blocking categories:** `attack:incomplete`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Crush`, `Darkness Aura (1/Day)`.

**Incomplete source attacks:** `Crush`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Darkness Aura (1/Day):** Darkness Aura (1/Day). A 15--foot radius of magical darkness extends out from the darkmantle, moves with it, and spreads around corners. The darkness lasts as long as the darkmantle maintains concentration, up to 10 minutes (as if concentrating on a spell). Darkvision can't penetrate this darkness, and no natural light can illuminate it. If any of the darkness overlaps with an area of light created by a spell of 2nd level or lower, the spell creating the light is dispelled.
- **Incomplete attack — Crush:** Crush. Melee Weapon Attack: +5 to hit, reach 5 ft., one creature. Hit: 6 (1d6 + 3) bludgeoning damage, and the darkmantle attaches to the target. If the target is Medium or smaller and the darkmantle has advantage on the attack roll, it attaches by engulfing the target's head, and the target is also blinded and unable to breathe while the darkmantle is attached in this way.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 033. Deep Gnome (Svirfneblin) — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `War Pick`, `Poisoned Dart`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The gnome’s innate spellcasting ability is Intelligence (spell save DC 11). It can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 034. Deva — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Mace`, `Healing Touch (3/Day)`, `Change Shape`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The deva's spellcasting ability is Charisma (spell save DC 17). The deva can innately cast the following spells, requiring only verbal components:
- **Action — Healing Touch (3/Day):** Healing Touch (3/Day). The deva touches another creature. The target magically regains 20 (4d8 + 2) hit points and is freed from any curse, disease, poison, blindness, or deafness.
- **Action — Change Shape:** Change Shape. The deva magically polymorphs into a humanoid or beast that has a challenge rating equal to or less than its own, or back into its true form. It reverts to its true form if it dies. Any equipment it is wearing or carrying is absorbed or borne by the new form (the deva's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 035. Djinni — DEATH / HP-LIFECYCLE

**Blocking categories:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Elemental Demise`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Scimitar`, `Create Whirlwind`.

**Incomplete source attacks:** `Scimitar`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Elemental Demise:** Elemental Demise. If the djinni dies, its body disintegrates into a warm breeze, leaving behind only equipment the djinni was wearing or carrying.
- **Trait — Innate Spellcasting:** Innate Spellcasting. The djinni's innate spellcasting ability is Charisma (spell save DC 17, +9 to hit with spell attacks). It can innately cast the following spells, requiring no material components:
- **Action — Create Whirlwind:** Create Whirlwind. A 5-foot-radius, 30-foot-tall cylinder of swirling air magically forms on a point the djinni can see within 120 feet of it. The whirlwind lasts as long as the djinni maintains concentration (as if concentrating on a spell). Any creature but the djinni that enters the whirlwind must succeed on a DC 18 Strength saving throw or be restrained by it. The djinni can move the whirlwind up to 60 feet as an action, and creatures restrained by the whirlwind move with it. The whirlwind ends if the djinni loses sight of it.
- **Incomplete attack — Scimitar:** Scimitar. Melee Weapon Attack: +9 to hit, reach 5 ft., one target. Hit: 12 (2d6 + 5) slashing damage plus 3 (1d6) lightning or thunder damage (djinni's choice).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 036. Doppelganger — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `attack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`, `Ambusher`, `Surprise Attack`.

**Printed actions:** `Multiattack`, `Slam`, `Read Thoughts`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The doppelganger can use its action to polymorph into a Small or Medium humanoid it has seen, or back into its true form. Its statistics, other than its size, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Trait — Ambusher:** Ambusher. The doppelganger has advantage on attack rolls against any creature it has surprised.
- **Trait — Surprise Attack:** Surprise Attack. If the doppelganger surprises a creature and hits it with an attack during the first round of combat, the target takes an extra 10 (3d6) damage from the attack.
- **Action — Read Thoughts:** Read Thoughts. The doppelganger magically reads the surface thoughts of one creature within 60 feet of it. The effect can penetrate barriers, but 3 feet of wood or dirt, 2 feet of stone, 2 inches of metal, or a thin sheet of lead blocks it. While the target is in range, the doppelganger can continue reading its thoughts, as long as the doppelganger's concentration isn't broken (as if concentrating on a spell). While reading the target's mind, the doppelganger has advantage on Wisdom (Insight) and Charisma (Deception, Intimidation, and Persuasion) checks against the target.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 037. Dretch — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claws`, `Fetid Cloud (1/Day)`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **Linked implementation/decision:** Ticket #678.
- **Previously recorded specific ruling / dependency:** - **Fetid Cloud user-approved fix queued:** Treat as a source-owned 1/day area poison: shared Poisoned + separate action/bonus exclusivity and reaction suppression, delivered by existing saving throw and timed-effect primitives. Do not change the global Poisoned effect; retain exact printed DC/radius/duration/immunity terms for implementation. Source/card retains the printed name. **Not coded or certified.**

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Fetid Cloud (1/Day):** Fetid Cloud (1/Day). A 10-foot radius of disgusting green gas extends out from the dretch. The gas spreads around corners, and its area is lightly obscured. It lasts for 1 minute or until a strong wind disperses it. Any creature that starts its turn in that area must succeed on a DC 11 Constitution saving throw or be poisoned until the start of its next turn. While poisoned in this way, the target can take either an action or a bonus action on its turn, not both, and can't take reactions.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 038. Drider — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Bite`, `Longsword`, `Longbow`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The drider's innate spellcasting ability is Wisdom (spell save DC 13). The drider can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 039. Drow — SPELLCASTING

**Blocking categories:** `attack:complex`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Shortsword`, `Hand Crossbow`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The drow’s spellcasting ability is Charisma (spell save DC 11). It can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 040. Druid — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Quarterstaff`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The druid is a 4th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 12, +4 to hit with spell attacks). It has the following druid spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 041. Dryad — FEAR / CHARM / STATUS

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`, `Speak with Beasts and Plants`, `Tree Stride`.

**Printed actions:** `Club`, `Fey Charm`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The dryad's innate spellcasting ability is Charisma (spell save DC 14). The dryad can innately cast the following spells, requiring no material components:
- **Trait — Speak with Beasts and Plants:** Speak with Beasts and Plants. The dryad can communicate with beasts and plants as if they shared a language.
- **Trait — Tree Stride:** Tree Stride. Once on her turn, the dryad can use 10 feet of her movement to step magically into one living tree within her reach and emerge from a second living tree within 60 feet of the first tree, appearing in an unoccupied space within 5 feet of the second tree. Both trees must be Large or bigger.
- **Action — Fey Charm:** Fey Charm. The dryad targets one humanoid or beast that she can see within 30 feet of her. If the target can see the dryad, it must succeed on a DC 14 Wisdom saving throw or be magically charmed. The charmed creature regards the dryad as a trusted friend to be heeded and protected. Although the target isn't under the dryad's control, it takes the dryad's requests or actions in the most favorable way it can.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 042. Duergar — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Duergar Resilience`.

**Printed actions:** `Enlarge (Recharges after a Short or Long Rest)`, `War Pick`, `Javelin`, `Invisibility (Recharges after a Short or Long Rest)`.

**Incomplete source attacks:** `War Pick`, `Javelin`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Duergar Resilience:** Duergar Resilience. The duergar has advantage on saving throws against poison, spells, and illusions, as well as to resist being charmed or paralyzed.
- **Action — Enlarge (Recharges after a Short or Long Rest):** Enlarge (Recharges after a Short or Long Rest). For 1 minute, the duergar magically increases in size, along with anything it is wearing or carrying. While enlarged, the duergar is Large, doubles its damage dice on Strength-based weapon attacks (included in the attacks), and makes Strength checks and Strength saving throws with advantage. If the duergar lacks the room to become Large, it attains the maximum size possible in the space available.
- **Action — Invisibility (Recharges after a Short or Long Rest):** Invisibility (Recharges after a Short or Long Rest). The duergar magically turns invisible until it attacks, casts a spell, or uses its Enlarge, or until its concentration is broken, up to 1 hour (as if concentrating on a spell). Any equipment the duergar wears or carries is invisible with it.
- **Incomplete attack — War Pick:** War Pick. Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 6 (1d8 + 2) piercing damage, or 11 (2d8 + 2) piercing damage while enlarged.
- **Incomplete attack — Javelin:** Javelin. Melee or Ranged Weapon Attack: +4 to hit, reach 5 ft. or range 30/120 ft., one target. Hit: 5 (1d6 + 2) piercing damage, or 9 (2d6 + 2) piercing damage while enlarged.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 043. Dust Mephit — DEATH / HP-LIFECYCLE

**Blocking categories:** `mechanic:recharge`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Death Burst`, `Innate Spellcasting`.

**Printed actions:** `Claws`, `Blinding Breath (Recharge 6)`.

**Printed action recharge mapping:** `{"blinding-breath":6}`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `recharge` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Burst:** Death Burst. When the mephit dies, it explodes in a burst of dust. Each creature within 5 feet of it must then succeed on a DC 10 Constitution saving throw or be blinded for 1 minute. A blinded creature can repeat the saving throw on each of its turns, ending the effect on itself on a success.
- **Trait — Innate Spellcasting:** Innate Spellcasting.(1/Day). The mephit can innately cast sleep, requiring no material components. Its innate spellcasting ability is Charisma.
- **Action — Blinding Breath (Recharge 6):** Blinding Breath (Recharge 6). The mephit exhales a 15- foot cone of blinding dust. Each creature in that area must succeed on a DC 10 Dexterity saving throw or be blinded for 1 minute. A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 044. Efreeti — DEATH / HP-LIFECYCLE

**Blocking categories:** `attack:range`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Elemental Demise`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Scimitar`, `Hurl Flame`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:range`:** Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `melee-ranged-range-bands` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Elemental Demise:** Elemental Demise. If the efreeti dies, its body disintegrates in a flash of fire and puff of smoke, leaving behind only equipment the efreeti was wearing or carrying.
- **Trait — Innate Spellcasting:** Innate Spellcasting. The efreeti's innate spellcasting ability is Charisma (spell save DC 15, +7 to hit with spell attacks). It can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 045. Erinyes — ATTACK RIDERS / MULTICOMPONENT DAMAGE

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Hellish Weapons`.

**Printed actions:** `Multiattack`, `Longsword`, `Longbow`.

**Printed reactions:** `Parry`.

**Incomplete source attacks:** `Longbow`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Hellish Weapons:** Hellish Weapons. The erinyes's weapon attacks are magical and deal an extra 13 (3d8) poison damage on a hit (included in the attacks).
- **Incomplete attack — Longbow:** Longbow. Ranged Weapon Attack: +7 to hit, range 150/600 ft., one target. Hit: 7 (1d8 + 3) piercing damage plus 13 (3d8) poison damage, and the target must succeed on a DC 14 Constitution saving throw or be poisoned. The poison lasts until it is removed by the lesser restoration spell or similar magic.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 046. Ettercap — RECHARGE / RESOURCES

**Blocking categories:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claws`, `Web (Recharge 5–6)`.

**Printed action recharge mapping:** `{"web":5}`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`attack:damage-type`:** Preserve each typed damage component and apply defenses separately and save-halving in both engines.
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 047. Fire Elemental — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Fire Form`, `Water Susceptibility`.

**Printed actions:** `Multiattack`, `Touch`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Fire Form/Water Susceptibility: reuse contact/fire application and damage-from-environment primitives; retain Pit environment policy.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Fire Form:** Fire Form. The elemental can move through a space as narrow as 1 inch wide without squeezing. A creature that touches the elemental or hits it with a melee attack while within 5 feet of it takes 5 (1d10) fire damage. In addition, the elemental can enter a hostile creature's space and stop there. The first time it enters a creature's space on a turn, that creature takes 5 (1d10) fire damage and catches fire; until someone takes an action to douse the fire, the creature takes 5 (1d10) fire damage at the start of each of its turns.
- **Trait — Water Susceptibility:** Water Susceptibility. For every 5 feet the elemental moves in water, or for every gallon of water splashed on it, it takes 1 cold damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 048. Flameskull — SPELLCASTING

**Blocking categories:** `attack:range`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Multiattack`, `Fire Ray`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:range`:** Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported); `melee-ranged-range-bands` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The flameskull is a 5th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 13, +5 to hit with spell attacks). It requires no somatic or material components to cast its spells. The flameskull has the following wizard spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 049. Frog — SOURCE-ONLY / ARENA POLICY

**Blocking categories:** `arena:neutral`. **Unbound named traits:** none separately listed.

**Fix queue for this monster:**
- **`arena:neutral`:** Verify existing no-combat-action arena policy and source text; never certify invented offense.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** No printed meaningful arena attack: preserve arena-neutral status.

**Reusable universal capabilities to inspect:** `action-economy` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 050. Gelatinous Cube — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Ooze Cube`, `Transparent`.

**Printed actions:** `Pseudopod`, `Engulf`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Ooze Cube:** Ooze Cube. The cube takes up its entire space. Other creatures can enter the space, but a creature that does so is subjected to the cube's Engulf and has disadvantage on the saving throw.
- **Trait — Transparent:** Transparent. Even when the cube is in plain sight, it takes a successful DC 15 Wisdom (Perception) check to spot a cube that has neither moved nor attacked. A creature that tries to enter the cube's space while unaware of the cube is surprised by the cube.
- **Action — Engulf:** Engulf. The cube moves up to its speed. While doing so, it can enter Large or smaller creatures' spaces. Whenever the cube enters a creature's space, the creature must make a DC 12 Dexterity saving throw.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 051. Ghost — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Ethereal Sight`.

**Printed actions:** `Withering Touch`, `Etherealness`, `Horrifying Visage`, `Possession (Recharge 6)`.

**Printed action recharge mapping:** `{"possession":6}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported); `recharge` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Ethereal Sight:** Ethereal Sight. The ghost can see 60 feet into the Ethereal Plane when it is on the Material Plane, and vice versa.
- **Action — Etherealness:** Etherealness. The ghost enters the Ethereal Plane from the Material Plane, or vice versa. It is visible on the Material Plane while it is in the Border Ethereal, and vice versa, yet it can't affect or be affected by anything on the other plane.
- **Action — Horrifying Visage:** Horrifying Visage. Each non-undead creature within 60 feet of the ghost that can see it must succeed on a DC 13 Wisdom saving throw or be frightened for 1 minute. If the save fails by 5 or more, the target also ages 1d4 × 10 years. A frightened target can repeat the saving throw at the end of each of its turns, ending the frightened condition on itself on a success. If a target's saving throw is successful or the effect ends for it, the target is immune to this ghost's Horrifying Visage for the next 24 hours. The aging effect can be reversed with a greater restoration spell, but only within 24 hours of it occurring.
- **Action — Possession (Recharge 6):** Possession (Recharge 6). One humanoid that the ghost can see within 5 feet of it must succeed on a DC 13 Charisma saving throw or be possessed by the ghost; the ghost then disappears, and the target is incapacitated and loses control of its body. The ghost now controls the body but doesn't deprive the target of awareness. The ghost can't be targeted by any attack, spell, or other effect, except ones that turn undead, and it retains its alignment, Intelligence, Wisdom, Charisma, and immunity to being charmed and frightened. It otherwise uses the possessed target's statistics, but doesn't gain access to the target's knowledge, class f […]

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 052. Giant Frog — RESTRAINT / SWALLOW

**Blocking categories:** `mechanic:swallow`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Bite`, `Swallow`.

**Fix queue for this monster:**
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Swallow:** Swallow. The frog makes one bite attack against a Small or smaller target it is grappling. If the attack hits, the target is swallowed, and the grapple ends. The swallowed target is blinded and restrained, it has total cover against attacks and other effects outside the frog, and it takes 5 (2d4) acid damage at the start of each of the frog's turns. The frog can have only one target swallowed at a time. If the frog dies, a swallowed creature is no longer restrained by it and can escape from the corpse using 5 feet of movement, exiting prone.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 053. Giant Spider — RECHARGE / RESOURCES

**Blocking categories:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`. **Unbound named traits:** none separately listed.

**Printed actions:** `Bite`, `Web (Recharge 5–6)`.

**Printed action recharge mapping:** `{"web":5}`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`attack:damage-type`:** Preserve each typed damage component and apply defenses separately and save-halving in both engines.
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 054. Giant Toad — RESTRAINT / SWALLOW

**Blocking categories:** `mechanic:swallow`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Bite`, `Swallow`.

**Fix queue for this monster:**
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Swallow:** Swallow. The toad makes one bite attack against a Medium or smaller target it is grappling. If the attack hits, the target is swallowed, and the grapple ends. The swallowed target is blinded and restrained, it has total cover against attacks and other effects outside the toad, and it takes 10 (3d6) acid damage at the start of each of the toad's turns. The toad can have only one target swallowed at a time. If the toad dies, a swallowed creature is no longer restrained by it and can escape from the corpse using 5 feet of movement, exiting prone.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 055. Gibbering Mouther — FEAR / CHARM / STATUS

**Blocking categories:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Aberrant Ground`, `Gibbering`.

**Printed actions:** `Multiattack`, `Bite`, `Blinding Spittle (Recharge 5–6)`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Aberrant Ground:** Aberrant Ground. The ground in a 10-foot radius around the mouther is doughlike difficult terrain. Each creature that starts its turn in that area must succeed on a DC 10 Strength saving throw or have its speed reduced to 0 until the start of its next turn.
- **Trait — Gibbering:** Gibbering. The mouther babbles incoherently while it can see any creature and isn't incapacitated. Each creature that starts its turn within 20 feet of the mouther and can hear the gibbering must succeed on a DC 10 Wisdom saving throw. On a failure, the creature can't take reactions until the start of its next turn and rolls a d8 to determine what it does during its turn. On a 1 to 4, the creature does nothing. On a 5 or 6, the creature takes no action or bonus action and uses all its movement to move in a randomly determined direction. On a 7 or 8, the creature makes a melee attack against a randomly determined creature within its  […]
- **Action — Blinding Spittle (Recharge 5–6):** Blinding Spittle (Recharge 5–6). The mouther spits a chemical glob at a point it can see within 15 feet of it. The glob explodes in a blinding flash of light on impact. Each creature within 5 feet of the flash must succeed on a DC 13 Dexterity saving throw or be blinded until the end of the mouther's next turn.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 056. Glabrezu — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Pincer`, `Fist`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The glabrezu's spellcasting ability is Intelligence (spell save DC 16). The glabrezu can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 057. Gray Ooze — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Corrode Metal`.

**Printed actions:** `Pseudopod`.

**Incomplete source attacks:** `Pseudopod`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Corrode Metal:** Corrode Metal. Any nonmagical weapon made of metal that hits the ooze corrodes. After dealing damage, the weapon takes a permanent and cumulative −1 penalty to damage rolls. If its penalty drops to −5, the weapon is destroyed. Nonmagical ammunition made of metal that hits the ooze is destroyed after dealing damage.
- **Incomplete attack — Pseudopod:** Pseudopod. Melee Weapon Attack: +3 to hit, reach 5 ft., one target. Hit: 4 (1d6 + 1) bludgeoning damage plus 7 (2d6) acid damage, and if the target is wearing nonmagical metal armor, its armor is partly corroded and takes a permanent and cumulative −1 penalty to the AC it offers. The armor is destroyed if the penalty reduces its AC to 10.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 058. Green Hag — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Claws`, `Illusory Appearance`, `Invisible Passage`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The hag's innate spellcasting ability is Charisma (spell save DC 12). She can innately cast the following spells, requiring no material components:
- **Action — Illusory Appearance:** Illusory Appearance. The hag covers herself and anything she is wearing or carrying with a magical illusion that makes her look like another creature of her general size and humanoid shape. The illusion ends if the hag takes a bonus action to end it or if she dies.
- **Action — Invisible Passage:** Invisible Passage. The hag magically turns invisible until she attacks or casts a spell, or until her concentration ends (as if concentrating on a spell). While invisible, she leaves no physical evidence of her passage, so she can be tracked only by magic. Any equipment she wears or carries is invisible with her.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 059. Grimlock — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:trait`. **Unbound named traits:** `Blind Senses`.

**Printed actions:** `Spiked Bone Club`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **RAW range locked / queued:** Blindsight **30 feet**, not arena-wide (24×16 five-foot squares). Reuse shared Blindsight/sight and source Blinded immunity; no global Blinded disadvantage within perceivable range, no valid gaze eye contact with Basilisk/Medusa, normal limitations beyond 30 ft. Preserve printed Deafened/smell qualifier for future mechanics. **Specification only: not implemented or certified.**

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Blind Senses:** Blind Senses. The grimlock can't use its blindsight while deafened and unable to smell.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 060. Guardian Naga — FEAR / CHARM / STATUS

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Bite`, `Spit Poison`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The naga is an 11th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 16, +8 to hit with spell attacks), and it needs only verbal components to cast its spells. It has the following cleric spells prepared:
- **Action — Spit Poison:** Spit Poison. Ranged Weapon Attack: +8 to hit, range 15/30 ft., one creature. Hit: The target must make a DC 15 Constitution saving throw, taking 45 (10d8) poison damage on a failed save, or half as much damage on a successful one.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 061. Gynosphinx — SPELLCASTING

**Blocking categories:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`. **Unbound named traits:** `Inscrutable`, `Spellcasting`.

**Printed actions:** `Multiattack`, `Claw`.

**Printed legendary choices:** `Claw Attack`, `Teleport (Costs 2 Actions)`, `Cast a Spell (Costs 3 Actions)`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported); `legendary-actions` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Inscrutable:** Inscrutable. The sphinx is immune to any effect that would sense its emotions or read its thoughts, as well as any divination spell that it refuses. Wisdom (Insight) checks made to ascertain the sphinx's intentions or sincerity have disadvantage.
- **Trait — Spellcasting:** Spellcasting. The sphinx is a 9th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 16, +8 to hit with spell attacks). It requires no material components to cast its spells. The sphinx has the following wizard spells prepared:
- **Legendary action — Claw Attack:** Claw Attack. The sphinx makes one claw attack.
- **Legendary action — Teleport (Costs 2 Actions):** Teleport (Costs 2 Actions). The sphinx magically teleports, along with any equipment it is wearing or carrying, up to 120 feet to an unoccupied space it can see.
- **Legendary action — Cast a Spell (Costs 3 Actions):** Cast a Spell (Costs 3 Actions). The sphinx casts a spell from its list of prepared spells, using a spell slot as normal.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 062. Harpy — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Claws`, `Club`, `Luring Song`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **Linked implementation/decision:** Ticket #679.
- **Previously recorded specific ruling / dependency:** - **Luring Song user decision / queued:** 300-ft range spans the entire current arena but retain hearing and creature-type eligibility. Failure of DC 11 Wisdom save composes existing Charmed and Incapacitated and moves the victim via existing pathfinding toward Harpy's 5-ft melee reach on its own turns, limited by normal movement (not teleport); retain printed follow-up saves, song continuation and 24-hour success immunity. **No implementation or certification yet.**

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Luring Song:** Luring Song. The harpy sings a magical melody. Every humanoid and giant within 300 feet of the harpy that can hear the song must succeed on a DC 11 Wisdom saving throw or be charmed until the song ends. The harpy must take a bonus action on its subsequent turns to continue singing. It can stop singing at any time. The song ends if the harpy is incapacitated.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 063. Homunculus — INFORMATION / NONCOMBAT

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Telepathic Bond`.

**Printed actions:** `Bite`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-buff-debuff-modifier-stack` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Telepathic Bond:** Telepathic Bond. While the homunculus is on the same plane of existence as its master, it can magically convey what it senses to its master, and the two can communicate telepathically.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 064. Horned Devil — OTHER / SOURCE BINDING

**Blocking categories:** `attack:complex`, `attack:range`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Fork`, `Tail`, `Hurl Flame`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`attack:range`:** Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported); `melee-ranged-range-bands` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 065. Hydra — REACTIONS / TRIGGERS

**Blocking categories:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Multiple Heads`, `Reactive Heads`.

**Printed actions:** `Multiattack`, `Bite`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Multiple/Reactive Heads: shared head count, sever/regrow triggers, attack count and reactions driven by combat state.

**Reusable universal capabilities to inspect:** `generic-reaction-trigger-grammar` (partial); `parry-redirect-reactions` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Multiple Heads:** Multiple Heads. The hydra has five heads. While it has more than one head, the hydra has advantage on saving throws against being blinded, charmed, deafened, frightened, stunned, and knocked unconscious.
- **Trait — Reactive Heads:** Reactive Heads. For each head the hydra has beyond one, it gets an extra reaction that can be used only for opportunity attacks.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 066. Ice Devil — RECHARGE / RESOURCES

**Blocking categories:** `mechanic:recharge`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Claws`, `Tail`, `Wall of Ice (Recharge 6)`.

**Printed action recharge mapping:** `{"wall-of-ice":6}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Wall of Ice (Recharge 6):** Wall of Ice (Recharge 6). The devil magically forms an opaque wall of ice on a solid surface it can see within 60 feet of it. The wall is 1 foot thick and up to 30 feet long and 10 feet high, or it's a hemispherical dome up to 20 feet in diameter.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 067. Ice Mephit — DEATH / HP-LIFECYCLE

**Blocking categories:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Death Burst`, `Innate Spellcasting`.

**Printed actions:** `Claws`, `Frost Breath (Recharge 6)`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:death-trigger`:** Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Burst:** Death Burst. When the mephit dies, it explodes in a burst of jagged ice. Each creature within 5 feet of it must make a DC 10 Dexterity saving throw, taking 4 (1d8) slashing damage on a failed save, or half as much damage on a successful one.
- **Trait — Innate Spellcasting:** Innate Spellcasting.(1/Day). The mephit can innately cast fog cloud, requiring no material components. Its innate spellcasting ability is Charisma.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 068. Imp — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Sting (Bite in Beast Form)`, `Invisibility`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The imp can use its action to polymorph into a beast form that resembles a rat (speed 20 ft.), a raven (20 ft., fly 60 ft.), or a spider (20 ft., climb 20 ft.), or back into its true form. Its statistics are the same in each form, except for the speed changes noted. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Action — Invisibility:** Invisibility. The imp magically turns invisible until it attacks or until its concentration ends (as if concentrating on a spell). Any equipment the imp wears or carries is invisible with it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 069. Invisible Stalker — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:trait`. **Unbound named traits:** `Invisibility`.

**Printed actions:** `Multiattack`, `Slam`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** #674 Faultless Tracker merged; actual Invisibility unresolved.
- **Previously recorded specific ruling / dependency:** - **User-approved arena policy (queued):** Faultless Tracker remains printed on source/card but has no effect in Iron Pit, no combat vision/targeting bonus. Invisibility uses existing universal system; Slam attacks are unaffected. Apply shared arena-inert trait classification and regenerate blockers; not yet implemented/certified.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Invisibility:** Invisibility. The stalker is invisible.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 070. Knight — RECHARGE / RESOURCES

**Blocking categories:** `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Greatsword`, `Heavy Crossbow`, `Leadership (Recharges after a Short or Long Rest)`.

**Printed reactions:** `Parry`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **Previously recorded specific ruling / dependency:** - **Leadership user decision / queued:** Activate via Action as a nonspell, short/long-rest recharge, 10-round Bless-style +1d4 to qualifying friendly attack rolls and saves within 30 ft and able to hear. No Concentration. **Iron Pit house simplification:** once activated, buff continues until duration expires or the Knight reaches 0 HP; printed Incapacitated-ending restriction is replaced by HP > 0. Reuse shared roll-bonus mechanics. **Not implemented/certified.**

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Leadership (Recharges after a Short or Long Rest):** Leadership (Recharges after a Short or Long Rest). For 1 minute, the knight can utter a special command or warning whenever a nonhostile creature that it can see within 30 feet of it makes an attack roll or a saving throw. The creature can add a d4 to its roll provided it can hear and understand the knight. A creature can benefit from only one Leadership die at a time. This effect ends if the knight is incapacitated.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 071. Kraken — RESTRAINT / SWALLOW

**Blocking categories:** `attack:incomplete`, `mechanic:legendary`, `mechanic:swallow`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Freedom of Movement`.

**Printed actions:** `Multiattack`, `Bite`, `Tentacle`, `Fling`, `Lightning Storm`.

**Printed legendary choices:** `Tentacle Attack or Fling`, `Lightning Storm (Costs 2 Actions)`, `Ink Cloud (Costs 3 Actions)`.

**Incomplete source attacks:** `Tentacle`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported); `legendary-actions` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Freedom of Movement:** Freedom of Movement. The kraken ignores difficult terrain, and magical effects can't reduce its speed or cause it to be restrained. It can spend 5 feet of movement to escape from nonmagical restraints or being grappled.
- **Action — Fling:** Fling. One Large or smaller object held or creature grappled by the kraken is thrown up to 60 feet in a random direction and knocked prone. If a thrown target strikes a solid surface, the target takes 3 (1d6) bludgeoning damage for every 10 feet it was thrown. If the target is thrown at another creature, that creature must succeed on a DC 18 Dexterity saving throw or take the same damage and be knocked prone.
- **Action — Lightning Storm:** Lightning Storm. The kraken magically creates three bolts of lightning, each of which can strike a target the kraken can see within 120 feet of it. A target must make a DC 23 Dexterity saving throw, taking 22 (4d10) lightning damage on a failed save, or half as much damage on a successful one.
- **Legendary action — Tentacle Attack or Fling:** Tentacle Attack or Fling. The kraken makes one tentacle attack or uses its Fling.
- **Legendary action — Lightning Storm (Costs 2 Actions):** Lightning Storm (Costs 2 Actions). The kraken uses Lightning Storm.
- **Legendary action — Ink Cloud (Costs 3 Actions):** Ink Cloud (Costs 3 Actions). While underwater, the kraken expels an ink cloud in a 60-foot radius. The cloud spreads around corners, and that area is heavily obscured to creatures other than the kraken. Each creature other than the kraken that ends its turn there must succeed on a DC 23 Constitution saving throw, taking 16 (3d10) poison damage on a failed save, or half as much damage on a successful one. A strong current disperses the cloud, which otherwise disappears at the end of the kraken's next turn.
- **Incomplete attack — Tentacle:** Tentacle. Melee Weapon Attack: +17 to hit, reach 30 ft., one target. Hit: 20 (3d6 + 10) bludgeoning damage, and the target is grappled (escape DC 18). Until this grapple ends, the target is restrained. The kraken has ten tentacles, each of which can grapple one target.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 072. Lamia — SPELLCASTING

**Blocking categories:** `attack:incomplete`, `mechanic:spellcasting`, `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Claws`, `Intoxicating Touch`.

**Incomplete source attacks:** `Claws`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The lamia's innate spellcasting ability is Charisma (spell save DC 13). It can innately cast the following spells, requiring no material components.
- **Action — Intoxicating Touch:** Intoxicating Touch. Melee Spell Attack: +5 to hit, reach 5 ft., one creature. Hit: The target is magically cursed for 1 hour. Until the curse ends, the target has disadvantage on Wisdom saving throws and all ability checks.
- **Incomplete attack — Claws:** Claws. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 14 (2d10 + 3) slashing damage. Dagger. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 5 (1d4 + 3) piercing damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 073. Lich — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Paralyzing Touch`.

**Printed legendary choices:** `Cantrip`, `Paralyzing Touch (Costs 2 Actions)`, `Frightening Gaze (Costs 2 Actions)`, `Disrupt Life (Costs 3 Actions)`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported); `legendary-actions` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The lich is an 18th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 20, +12 to hit with spell attacks). The lich has the following wizard spells prepared:
- **Legendary action — Cantrip:** Cantrip. The lich casts a cantrip.
- **Legendary action — Paralyzing Touch (Costs 2 Actions):** Paralyzing Touch (Costs 2 Actions). The lich uses its Paralyzing Touch.
- **Legendary action — Frightening Gaze (Costs 2 Actions):** Frightening Gaze (Costs 2 Actions). The lich fixes its gaze on one creature it can see within 10 feet of it. The target must succeed on a DC 18 Wisdom saving throw against this magic or become frightened for 1 minute. The frightened target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. If a target's saving throw is successful or the effect ends for it, the target is immune to the lich's gaze for the next 24 hours.
- **Legendary action — Disrupt Life (Costs 3 Actions):** Disrupt Life (Costs 3 Actions). Each living creature within 20 feet of the lich must make a DC 18 Constitution saving throw against this magic, taking 21 (6d6) necrotic damage on a failed save, or half as much damage on a successful one.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 074. Mage — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Dagger`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The mage is a 9th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 14, +6 to hit with spell attacks). The mage has the following wizard spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 075. Magma Mephit — DEATH / HP-LIFECYCLE

**Blocking categories:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Death Burst`, `Innate Spellcasting`.

**Printed actions:** `Claws`, `Fire Breath (Recharge 6)`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:death-trigger`:** Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Burst:** Death Burst. When the mephit dies, it explodes in a burst of lava. Each creature within 5 feet of it must make a DC 11 Dexterity saving throw, taking 7 (2d6) fire damage on a failed save, or half as much damage on a successful one.
- **Trait — Innate Spellcasting:** Innate Spellcasting.(1/Day). The mephit can innately cast heat metal (spell save DC 10), requiring no material components. Its innate spellcasting ability is Charisma.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 076. Magmin — DEATH / HP-LIFECYCLE

**Blocking categories:** `attack:incomplete`, `mechanic:death-trigger`, `source:trait`. **Unbound named traits:** `Death Burst`, `Ignited Illumination`.

**Printed actions:** `Touch`.

**Incomplete source attacks:** `Touch`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:death-trigger`:** Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Burst:** Death Burst. When the magmin dies, it explodes in a burst of fire and magma. Each creature within 10 feet of it must make a DC 11 Dexterity saving throw, taking 7 (2d6) fire damage on a failed save, or half as much damage on a successful one. Flammable objects that aren't being worn or carried in that area are ignited.
- **Trait — Ignited Illumination:** Ignited Illumination. As a bonus action, the magmin can set itself ablaze or extinguish its flames. While ablaze, the magmin sheds bright light in a 10-foot radius and dim light for an additional 10 feet.
- **Incomplete attack — Touch:** Touch. Melee Weapon Attack: +4 to hit, reach 5 ft., one target. Hit: 7 (2d6) fire damage. If the target is a creature or a flammable object, it ignites. Until a creature takes an action to douse the fire, the target takes 3 (1d6) fire damage at the end of each of its turns.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 077. Manticore — RECHARGE / RESOURCES

**Blocking categories:** `mechanic:limited-use`, `source:trait`. **Unbound named traits:** `Tail Spike Regrowth`.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Tail Spike`.

**Fix queue for this monster:**
- **`mechanic:limited-use`:** Bind uses, expenditure, recovery/regrowth roll/interval and reset to generic encounter resources.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Tail Spike Regrowth:** Tail Spike Regrowth. The manticore has twenty-four tail spikes. Used spikes regrow when the manticore finishes a long rest.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 078. Marilith — REACTIONS / TRIGGERS

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Reactive`.

**Printed actions:** `Multiattack`, `Longsword`, `Tail`, `Teleport`.

**Printed reactions:** `Parry`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-reaction-trigger-grammar` (partial); `parry-redirect-reactions` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Reactive:** Reactive. The marilith can take one reaction on every turn in a combat.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 079. Medusa — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:trait`. **Unbound named traits:** `Petrifying Gaze`.

**Printed actions:** `Multiattack`, `Snake Hair`, `Shortsword`, `Longbow`.

**Fix queue for this monster:**
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** Ticket #676, paired Basilisk.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Petrifying Gaze: reuse timed save escalation to Petrified, but verify sight/gaze avoidance and source timing.
- **Previously recorded specific ruling / dependency:** - **User decision, queued:** Same shared gaze mechanic and sight/avert policy as Basilisk. Medusa supplies **DC 14 Constitution, 30-ft range** and the special **fail by 5 or more => immediate Petrified** escalation (terminal Iron Pit outcome). Other failed saves follow existing Restrained → repeat-save → Petrified progression; source qualifiers preserved. Not implemented/certified.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Petrifying Gaze:** Petrifying Gaze. When a creature that can see the medusa's eyes starts its turn within 30 feet of the medusa, the medusa can force it to make a DC 14 Constitution saving throw if the medusa isn't incapacitated and can see the creature. If the saving throw fails by 5 or more, the creature is instantly petrified. Otherwise, a creature that fails the save begins to turn to stone and is restrained. The restrained creature must repeat the saving throw at the end of its next turn, becoming petrified on a failure or ending the effect on a success. The petrification lasts until the creature is freed by the greater restoration spell or other […]

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 080. Mimic — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Shapechanger`, `Adhesive (Object Form Only)`, `False Appearance (Object Form Only)`, `Grappler`.

**Printed actions:** `Pseudopod`, `Bite`.

**Incomplete source attacks:** `Pseudopod`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The mimic can use its action to polymorph into an object or back into its true, amorphous form. Its statistics are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Trait — Adhesive (Object Form Only):** Adhesive (Object Form Only). The mimic adheres to anything that touches it. A Huge or smaller creature adhered to the mimic is also grappled by it (escape DC 13). Ability checks made to escape this grapple have disadvantage.
- **Trait — False Appearance (Object Form Only):** False Appearance (Object Form Only). While the mimic remains motionless, it is indistinguishable from an ordinary object.
- **Trait — Grappler:** Grappler. The mimic has advantage on attack rolls against any creature grappled by it.
- **Incomplete attack — Pseudopod:** Pseudopod. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 7 (1d8 + 3) bludgeoning damage. If the mimic is in object form, the target is subjected to its Adhesive trait.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 081. Mummy — OTHER / SOURCE BINDING

**Blocking categories:** `attack:incomplete`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Rotting Fist`, `Dreadful Glare`.

**Incomplete source attacks:** `Rotting Fist`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Dreadful Glare:** Dreadful Glare. The mummy targets one creature it can see within 60 feet of it. If the target can see the mummy, it must succeed on a DC 11 Wisdom saving throw against this magic or become frightened until the end of the mummy's next turn. If the target fails the saving throw by 5 or more, it is also paralyzed for the same duration. A target that succeeds on the saving throw is immune to the Dreadful Glare of all mummies (but not mummy lords) for the next 24 hours.
- **Incomplete attack — Rotting Fist:** Rotting Fist. Melee Weapon Attack: +5 to hit, reach 5 ft., one target. Hit: 10 (2d6 + 3) bludgeoning damage plus 10 (3d6) necrotic damage. If the target is a creature, it must succeed on a DC 12 Constitution saving throw or be cursed with mummy rot. The cursed target can't regain hit points, and its hit point maximum decreases by 10 (3d6) for every 24 hours that elapse. If the curse reduces the target's hit point maximum to 0, the target dies, and its body turns to dust. The curse lasts until removed by the remove curse spell or other magic.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 082. Mummy Lord — AREA / SAVE ACTIONS

**Blocking categories:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Multiattack`, `Rotting Fist`, `Dreadful Glare`.

**Printed legendary choices:** `Attack`, `Blinding Dust`, `Blasphemous Word (Costs 2 Actions)`, `Channel Negative Energy (Costs 2 Actions)`, `Whirlwind of Sand (Costs 2 Actions)`.

**Incomplete source attacks:** `Rotting Fist`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `area-target-placement` (supported); `saving-throws` (supported); `legendary-actions` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The mummy lord is a 10th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 17, +9 to hit with spell attacks). The mummy lord has the following cleric spells prepared:
- **Action — Dreadful Glare:** Dreadful Glare. The mummy lord targets one creature it can see within 60 feet of it. If the target can see the mummy lord, it must succeed on a DC 16 Wisdom saving throw against this magic or become frightened until the end of the mummy's next turn. If the target fails the saving throw by 5 or more, it is also paralyzed for the same duration. A target that succeeds on the saving throw is immune to the Dreadful Glare of all mummies and mummy lords for the next 24 hours.
- **Legendary action — Attack:** Attack. The mummy lord makes one attack with its rotting fist or uses its Dreadful Glare.
- **Legendary action — Blinding Dust:** Blinding Dust. Blinding dust and sand swirls magically around the mummy lord. Each creature within 5 feet of the mummy lord must succeed on a DC 16 Constitution saving throw or be blinded until the end of the creature's next turn.
- **Legendary action — Blasphemous Word (Costs 2 Actions):** Blasphemous Word (Costs 2 Actions). The mummy lord utters a blasphemous word. Each non-undead creature within 10 feet of the mummy lord that can hear the magical utterance must succeed on a DC 16 Constitution saving throw or be stunned until the end of the mummy lord's next turn.
- **Legendary action — Channel Negative Energy (Costs 2 Actions):** Channel Negative Energy (Costs 2 Actions). The mummy lord magically unleashes negative energy. Creatures within 60 feet of the mummy lord, including ones behind barriers and around corners, can't regain hit points until the end of the mummy lord's next turn.
- **Legendary action — Whirlwind of Sand (Costs 2 Actions):** Whirlwind of Sand (Costs 2 Actions). The mummy lord magically transforms into a whirlwind of sand, moves up to 60 feet, and reverts to its normal form. While in whirlwind form, the mummy lord is immune to all damage, and it can't be grappled, petrified, knocked prone, restrained, or stunned. Equipment worn or carried by the mummy lord remain in its possession.
- **Incomplete attack — Rotting Fist:** Rotting Fist. Melee Weapon Attack: +9 to hit, reach 5 ft., one target. Hit: 14 (3d6 + 4) bludgeoning damage plus 21 (6d6) necrotic damage. If the target is a creature, it must succeed on a DC 16 Constitution saving throw or be cursed with mummy rot. The cursed target can't regain hit points, and its hit point maximum decreases by 10 (3d6) for every 24 hours that elapse. If the curse reduces the target's hit point maximum to 0, the target dies, and its body turns to dust. The curse lasts until removed by the remove curse spell or other magic.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 083. Night Hag — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Claws`, `Change Shape`, `Etherealness`, `Nightmare Haunting (1/Day)`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The hag's innate spellcasting ability is Charisma (spell save DC 14, +6 to hit with spell attacks). She can innately cast the following spells, requiring no material components:
- **Action — Change Shape:** Change Shape. The hag magically polymorphs into a Small or Medium female humanoid, or back into her true form. Her statistics are the same in each form. Any equipment she is wearing or carrying isn't transformed. She reverts to her true form if she dies.
- **Action — Etherealness:** Etherealness. The hag magically enters the Ethereal Plane from the Material Plane, or vice versa. To do so, the hag must have a heartstone in her possession.
- **Action — Nightmare Haunting (1/Day):** Nightmare Haunting (1/Day). While on the Ethereal Plane, the hag magically touches a sleeping humanoid on the Material Plane. A protection from evil and good spell cast on the target prevents this contact, as does a magic circle. As long as the contact persists, the target has dreadful visions. If these visions last for at least 1 hour, the target gains no benefit from its rest, and its hit point maximum is reduced by 5 (1d10). If this effect reduces the target's hit point maximum to 0, the target dies, and if the target was evil, its soul is trapped in the hag's soul bag. The reduction to the target's hit point maximum lasts until  […]

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 084. Nightmare — POSITION / MOVEMENT

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Confer Fire Resistance`.

**Printed actions:** `Hooves`, `Ethereal Stride`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `movement-modes-closing` (supported); `forced-movement-push-pull-teleport` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Confer Fire Resistance:** Confer Fire Resistance. The nightmare can grant resistance to fire damage to anyone riding it.
- **Action — Ethereal Stride:** Ethereal Stride. The nightmare and up to three willing creatures within 5 feet of it magically enter the Ethereal Plane from the Material Plane, or vice versa.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 085. Oni — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Claw (Oni Form Only)`, `Glaive`, `Change Shape`.

**Incomplete source attacks:** `Glaive`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The oni's innate spellcasting ability is Charisma (spell save DC 13). The oni can innately cast the following spells, requiring no material components:
- **Action — Change Shape:** Change Shape. The oni magically polymorphs into a Small or Medium humanoid, into a Large giant, or back into its true form. Other than its size, its statistics are the same in each form. The only equipment that is transformed is its glaive, which shrinks so that it can be wielded in humanoid form. If the oni dies, it reverts to its true form, and its glaive reverts to its normal size.
- **Incomplete attack — Glaive:** Glaive. Melee Weapon Attack: +7 to hit, reach 10 ft., one target. Hit: 15 (2d10 + 4) slashing damage, or 9 (1d10 + 4) slashing damage in Small or Medium form.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 086. Otyugh — RESTRAINT / SWALLOW

**Blocking categories:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Limited Telepathy`.

**Printed actions:** `Multiattack`, `Bite`, `Tentacle`, `Tentacle Slam`.

**Incomplete source attacks:** `Tentacle`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Limited Telepathy:** Limited Telepathy. The otyugh can magically transmit simple messages and images to any creature within 120 feet of it that can understand a language. This form of telepathy doesn't allow the receiving creature to telepathically respond.
- **Action — Tentacle Slam:** Tentacle Slam. The otyugh slams creatures grappled by it into each other or a solid surface. Each creature must succeed on a DC 14 Constitution saving throw or take 10 (2d6 + 3) bludgeoning damage and be stunned until the end of the otyugh's next turn. On a successful save, the target takes half the bludgeoning damage and isn't stunned.
- **Incomplete attack — Tentacle:** Tentacle. Melee Weapon Attack: +6 to hit, reach 10 ft., one target. Hit: 7 (1d8 + 3) bludgeoning damage plus 4 (1d8) piercing damage. If the target is Medium or smaller, it is grappled (escape DC 13) and restrained until the grapple ends. The otyugh has two tentacles, each of which can grapple one target.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 087. Pit Fiend — FEAR / CHARM / STATUS

**Blocking categories:** `attack:incomplete`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Fear Aura`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Mace`, `Tail`.

**Incomplete source attacks:** `Bite`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Incomplete attack — Bite:** Bite. Melee Weapon Attack: +14 to hit, reach 5 ft., one target. Hit: 22 (4d6 + 8) piercing damage. The target must succeed on a DC 21 Constitution saving throw or become poisoned. While poisoned in this way, the target can't regain hit points, and it takes 21 (6d6) poison damage at the start of each of its turns. The poisoned target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 088. Planetar — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Divine Awareness`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Greatsword`, `Healing Touch`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Divine Awareness:** Divine Awareness. The planetar knows if it hears a lie.
- **Trait — Innate Spellcasting:** Innate Spellcasting. The planetar's spellcasting ability is Charisma (spell save DC 20). The planetar can innately cast the following spells, requiring no material components:
- **Action — Healing Touch:** Healing Touch (4/Day). The planetar touches another creature. The target magically regains 30 (6d8 + 3) hit points and is freed from any curse, disease, poison, blindness, or deafness.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 089. Priest — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Divine Eminence`, `Spellcasting`.

**Printed actions:** `Mace`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Divine Eminence:** Divine Eminence. As a bonus action, the priest can expend a spell slot to cause its melee weapon attacks to magically deal an extra 10 (3d6) radiant damage to a target on a hit. This benefit lasts until the end of the turn. If the priest expends a spell slot of 2nd level or higher, the extra damage increases by 1d6 for each level above 1st.
- **Trait — Spellcasting:** Spellcasting. The priest is a 5th-level spellcaster. Its spellcasting ability is Wisdom (spell save DC 13, +5 to hit with spell attacks). The priest has the following cleric spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 090. Pseudodragon — INFORMATION / NONCOMBAT

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Limited Telepathy`.

**Printed actions:** `Bite`, `Sting`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-buff-debuff-modifier-stack` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Limited Telepathy:** Limited Telepathy. The pseudodragon can magically communicate simple ideas, emotions, and images telepathically with any creature within 100 feet of it that can understand a language.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 091. Purple Worm — OTHER / SOURCE BINDING

**Blocking categories:** `attack:complex`, `mechanic:swallow`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Bite`, `Tail Stinger`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported); `grappled-restrained-escape` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 092. Quasit — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `attack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Claws (Bite in Beast Form)`, `Scare (1/Day)`, `Invisibility`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The quasit can use its action to polymorph into a beast form that resembles a bat (speed 10 ft. fly 40 ft.), a centipede (40 ft., climb 40 ft.), or a toad (40 ft., swim 40 ft.), or back into its true form. Its statistics are the same in each form, except for the speed changes noted. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Action — Scare (1/Day):** Scare (1/Day). One creature of the quasit's choice within 20 feet of it must succeed on a DC 10 Wisdom saving throw or be frightened for 1 minute. The target can repeat the saving throw at the end of each of its turns, with disadvantage if the quasit is within line of sight, ending the effect on itself on a success.
- **Action — Invisibility:** Invisibility. The quasit magically turns invisible until it attacks or uses Scare, or until its concentration ends (as if concentrating on a spell). Any equipment the quasit wears or carries is invisible with it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 093. Rakshasa — SPELLCASTING

**Blocking categories:** `mechanic:defense`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Limited Magic Immunity`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Claw`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:defense`:** Bind printed conditional magic/condition damage defense to universal attack/save/spell predicates without monster-specific code.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Limited Magic Immunity:** Limited Magic Immunity. The rakshasa can't be affected or detected by spells of 6th level or lower unless it wishes to be. It has advantage on saving throws against all other spells and magical effects.
- **Trait — Innate Spellcasting:** Innate Spellcasting. The rakshasa's innate spellcasting ability is Charisma (spell save DC 18, +10 to hit with spell attacks). The rakshasa can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 094. Remorhaz — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `mechanic:swallow`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Heated Body`.

**Printed actions:** `Bite`, `Swallow`.

**Fix queue for this monster:**
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** PR #673 covers only Heated Body; Swallow remains.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Heated Body: contact retaliation with source fire dice and temperature-independent Pit interpretation.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported); `grappled-restrained-escape` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Heated Body:** Heated Body. A creature that touches the remorhaz or hits it with a melee attack while within 5 feet of it takes 10 (3d6) fire damage.
- **Action — Swallow:** Swallow. The remorhaz makes one bite attack against a Medium or smaller creature it is grappling. If the attack hits, that creature takes the bite's damage and is swallowed, and the grapple ends. While swallowed, the creature is blinded and restrained, it has total cover against attacks and other effects outside the remorhaz, and it takes 21 (6d6) acid damage at the start of each of the remorhaz's turns.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 095. Roper — RESTRAINT / SWALLOW

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Grasping Tendrils`.

**Printed actions:** `Multiattack`, `Bite`, `Tendril`, `Reel`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Grasping Tendrils:** Grasping Tendrils. The roper can have up to six tendrils at a time. Each tendril can be attacked (AC 20; 10 hit points; immunity to poison and psychic damage). Destroying a tendril deals no damage to the roper, which can extrude a replacement tendril on its next turn. A tendril can also be broken if a creature takes an action and succeeds on a DC 15 Strength check against it.
- **Action — Tendril:** Tendril. Melee Weapon Attack: +7 to hit, reach 50 ft., one creature. Hit: The target is grappled (escape DC 15). Until the grapple ends, the target is restrained and has disadvantage on Strength checks and Strength saving throws, and the roper can't use the same tendril on another target.
- **Action — Reel:** Reel. The roper pulls each creature grappled by it up to 25 feet straight toward it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 096. Rug of Smothering — RESTRAINT / SWALLOW

**Blocking categories:** `attack:none`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Damage Transfer`.

**Printed actions:** `Smother`.

**Fix queue for this monster:**
- **`attack:none`:** Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Damage Transfer: reuse distributed incoming damage primitive if exact; integrate grapple/restrain and existing susceptibility.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Damage Transfer:** Damage Transfer. While it is grappling a creature, the rug takes only half the damage dealt to it, and the creature grappled by the rug takes the other half.
- **Action — Smother:** Smother. Melee Weapon Attack: +5 to hit, reach 5 ft., one Medium or smaller creature. Hit: The creature is grappled (escape DC 13). Until this grapple ends, the target is restrained, blinded, and at risk of suffocating, and the rug can't smother another target. In addition, at the start of each of the target's turns, the target takes 10 (2d6 + 3) bludgeoning damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 097. Rust Monster — OTHER / SOURCE BINDING

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Iron Scent`, `Rust Metal`.

**Printed actions:** `Bite`, `Antennae`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Iron Scent:** Iron Scent. The rust monster can pinpoint, by scent, the location of ferrous metal within 30 feet of it.
- **Trait — Rust Metal:** Rust Metal. Any nonmagical weapon made of metal that hits the rust monster corrodes. After dealing damage, the weapon takes a permanent and cumulative −1 penalty to damage rolls. If its penalty drops to −5, the weapon is destroyed. Nonmagical ammunition made of metal that hits the rust monster is destroyed after dealing damage.
- **Action — Antennae:** Antennae. The rust monster corrodes a nonmagical ferrous metal object it can see within 5 feet of it. If the object isn't being worn or carried, the touch destroys a 1-foot cube of it. If the object is being worn or carried by a creature, the creature can make a DC 11 Dexterity saving throw to avoid the rust monster's touch.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 098. Salamander — PASSIVE RETALIATION / DAMAGE AURA

**Blocking categories:** `attack:complex`, `source:trait`. **Unbound named traits:** `Heated Body`.

**Printed actions:** `Multiattack`, `Spear`, `Tail`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Linked implementation/decision:** PR #673 covers only Heated Body; source Tail remains.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Heated Body: generic touch retaliation; tail: exact own-grapple auto-hit constraint, not mere Advantage.

**Reusable universal capabilities to inspect:** `typed-damage-resistance-immunity-vulnerability` (supported); `ongoing-periodic-damage` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Heated Body:** Heated Body. A creature that touches the salamander or hits it with a melee attack while within 5 feet of it takes 7 (2d6) fire damage.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 099. Sea Hag — OTHER / SOURCE BINDING

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Horrific Appearance`.

**Printed actions:** `Claws`, `Death Glare`, `Illusory Appearance`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Horrific Appearance:** Horrific Appearance. Any humanoid that starts its turn within 30 feet of the hag and can see the hag's true form must make a DC 11 Wisdom saving throw. On a failed save, the creature is frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, with disadvantage if the hag is within line of sight, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the hag's Horrific Appearance for the next 24 hours.
- **Action — Death Glare:** Death Glare. The hag targets one frightened creature she can see within 30 feet of her. If the target can see the hag, it must succeed on a DC 11 Wisdom saving throw against this magic or drop to 0 hit points.
- **Action — Illusory Appearance:** Illusory Appearance. The hag covers herself and anything she is wearing or carrying with a magical illusion that makes her look like an ugly creature of her general size and humanoid shape. The effect ends if the hag takes a bonus action to end it or if she dies.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 100. Sea Horse — SOURCE-ONLY / ARENA POLICY

**Blocking categories:** `attack:none`. **Unbound named traits:** none separately listed.

**Fix queue for this monster:**
- **`attack:none`:** Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.
- **Previously recorded specific ruling / dependency:** - **USER DECISION / QUEUED:** Sea Horse may be selected and fielded in Iron Pit; it simply deals **0 attack damage**. Do not invent a damaging attack or alter the printed source. Change arena-neutral exclusion/certification behavior to allow a valid non-damaging participant; ensure combat can terminate without stalls. Not implemented/certified.
- **Previously recorded specific ruling / dependency:** - **Further user suggestion:** Rather than a fabricated 0-damage attack, Sea Horse may repeatedly take the **existing Dodge Action** on its turns, retaining exactly RAW Dodge conditions and no damage output; still arena-selectable. Avoid new machinery; guard against no-damage stalemates. Proposal queued, not implemented/certified.

**Reusable universal capabilities to inspect:** `action-economy` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 101. Shadow — ATTACK RIDERS / MULTICOMPONENT DAMAGE

**Blocking categories:** `attack:incomplete`, `source:trait`. **Unbound named traits:** `Sunlight Weakness`.

**Printed actions:** `Strength Drain`.

**Incomplete source attacks:** `Strength Drain`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `typed-damage-resistance-immunity-vulnerability` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Sunlight Weakness:** Sunlight Weakness. While in sunlight, the shadow has disadvantage on attack rolls, ability checks, and saving throws.
- **Incomplete attack — Strength Drain:** Strength Drain. Melee Weapon Attack: +4 to hit, reach 5 ft., one creature. Hit: 9 (2d6 + 2) necrotic damage, and the target's Strength score is reduced by 1d4. The target dies if this reduces its Strength to 0. Otherwise, the reduction lasts until the target finishes a short or long rest.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 102. Shambling Mound — RESTRAINT / SWALLOW

**Blocking categories:** `mechanic:swallow`, `multiattack:complex`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Slam`, `Engulf`.

**Fix queue for this monster:**
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Engulf:** Engulf. The shambling mound engulfs a Medium or smaller creature grappled by it. The engulfed target is blinded, restrained, and unable to breathe, and it must succeed on a DC 14 Constitution saving throw at the start of each of the mound's turns or take 13 (2d8 + 4) bludgeoning damage. If the mound moves, the engulfed target moves with it. The mound can have only one creature engulfed at a time.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 103. Shield Guardian — RECHARGE / RESOURCES

**Blocking categories:** `source:reaction`, `source:trait`. **Unbound named traits:** `Bound`, `Spell Storing`.

**Printed actions:** `Multiattack`, `Fist`.

**Printed reactions:** `Shield`.

**Fix queue for this monster:**
- **`source:reaction`:** Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `generic-reaction-trigger-grammar` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Bound:** Bound. The shield guardian is magically bound to an amulet. As long as the guardian and its amulet are on the same plane of existence, the amulet's wearer can telepathically call the guardian to travel to it, and the guardian knows the distance and direction to the amulet. If the guardian is within 60 feet of the amulet's wearer, half of any damage the wearer takes (rounded up) is transferred to the guardian.
- **Trait — Spell Storing:** Spell Storing. A spellcaster who wears the shield guardian's amulet can cause the guardian to store one spell of 4th level or lower. To do so, the wearer must cast the spell on the guardian. The spell has no effect but is stored within the guardian. When commanded to do so by the wearer or when a situation arises that was predefined by the spellcaster, the guardian casts the stored spell with any parameters set by the original caster, requiring no components. When the spell is cast or a new spell is stored, any previously stored spell is lost.
- **Reaction — Shield:** Shield. When a creature makes an attack against the wearer of the guardian's amulet, the guardian grants a +2 bonus to the wearer's AC if the guardian is within 5 feet of the wearer.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 104. Shrieker — OTHER / SOURCE BINDING

**Blocking categories:** `attack:none`, `source:reaction`. **Unbound named traits:** none separately listed.

**Printed reactions:** `Shriek`.

**Fix queue for this monster:**
- **`attack:none`:** Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.
- **`source:reaction`:** Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `action-economy` (supported); `generic-reaction-trigger-grammar` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Reaction — Shriek:** Shriek. When bright light or a creature is within 30 feet of the shrieker, it emits a shriek audible within 300 feet of it. The shrieker continues to shriek until the disturbance moves out of range and for 1d4 of the shrieker's turns afterward.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 105. Solar — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Divine Awareness`, `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Greatsword`, `Slaying Longbow`, `Flying Sword`, `Healing Touch (4/Day)`.

**Printed legendary choices:** `Teleport`, `Searing Burst (Costs 2 Actions)`, `Blinding Gaze (Costs 3 Actions)`.

**Incomplete source attacks:** `Slaying Longbow`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported); `legendary-actions` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Divine Awareness:** Divine Awareness. The solar knows if it hears a lie.
- **Trait — Innate Spellcasting:** Innate Spellcasting. The solar's spellcasting ability is Charisma (spell save DC 25). It can innately cast the following spells, requiring no material components:
- **Action — Flying Sword:** Flying Sword. The solar releases its greatsword to hover magically in an unoccupied space within 5 feet of it. If the solar can see the sword, the solar can mentally command it as a bonus action to fly up to 50 feet and either make one attack against a target or return to the solar's hands. If the hovering sword is targeted by any effect, the solar is considered to be holding it. The hovering sword falls if the solar dies.
- **Action — Healing Touch (4/Day):** Healing Touch (4/Day). The solar touches another creature. The target magically regains 40 (8d8 + 4) hit points and is freed from any curse, disease, poison, blindness, or deafness.
- **Legendary action — Teleport:** Teleport. The solar magically teleports, along with any equipment it is wearing or carrying, up to 120 feet to an unoccupied space it can see.
- **Legendary action — Searing Burst (Costs 2 Actions):** Searing Burst (Costs 2 Actions). The solar emits magical, divine energy. Each creature of its choice in a 10-foot radius must make a DC 23 Dexterity saving throw, taking 14 (4d6) fire damage plus 14 (4d6) radiant damage on a failed save, or half as much damage on a successful one.
- **Legendary action — Blinding Gaze (Costs 3 Actions):** Blinding Gaze (Costs 3 Actions). The solar targets one creature it can see within 30 feet of it. If the target can see it, the target must succeed on a DC 15 Constitution saving throw or be blinded until magic such as the lesser restoration spell removes the blindness.
- **Incomplete attack — Slaying Longbow:** Slaying Longbow. Ranged Weapon Attack: +13 to hit, range 150/600 ft., one target. Hit: 15 (2d8 + 6) piercing damage plus 27 (6d8) radiant damage. If the target is a creature that has 100 hit points or fewer, it must succeed on a DC 15 Constitution saving throw or die.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 106. Spectator — AREA / SAVE ACTIONS

**Blocking categories:** `source:extra-action`, `source:reaction`. **Unbound named traits:** none separately listed.

**Printed actions:** `Bite`, `Eye Rays`, `Create Food and Water`.

**Printed reactions:** `Spell Reflection`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:reaction`:** Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Reusable universal capabilities to inspect:** `area-target-placement` (supported); `saving-throws` (supported); `generic-reaction-trigger-grammar` (partial). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Eye Rays:** Eye Rays. The spectator shoots up to two of the following magical eye rays at one or two creatures it can see within 90 feet of it. It can use each ray only once on a turn.
- **Action — Create Food and Water:** Create Food and Water. The spectator magically creates enough food and water to sustain itself for 24 hours.
- **Reaction — Spell Reflection:** Spell Reflection. If the spectator makes a successful saving throw against a spell, or a spell attack misses it, the spectator can choose another creature (including the spellcaster) it can see within 30 feet of it. The spell targets the chosen creature instead of the spectator. If the spell forced a saving throw, the chosen creature makes its own save. If the spell was an attack, the attack roll is rerolled against the chosen creature.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 107. Spirit Naga — SPELLCASTING

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Spellcasting`.

**Printed actions:** `Bite`.

**Spell binding preflight:** prepared spell structure present, innate structure not populated. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `spell-attack-rolls` (supported); `one-slot-spell-per-turn` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Spellcasting:** Spellcasting. The naga is a 10th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 14, +6 to hit with spell attacks), and it needs only verbal components to cast its spells. It has the following wizard spells prepared:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 108. Sprite — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `attack:complex`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Longsword`, `Shortbow`, `Heart Sight`, `Invisibility`.

**Fix queue for this monster:**
- **`attack:complex`:** Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Heart Sight:** Heart Sight. The sprite touches a creature and magically knows the creature's current emotional state. If the target fails a DC 10 Charisma saving throw, the sprite also knows the creature's alignment. Celestials, fiends, and undead automatically fail the saving throw.
- **Action — Invisibility:** Invisibility. The sprite magically turns invisible until it attacks or casts a spell, or until its concentration ends (as if concentrating on a spell). Any equipment the sprite wears or carries is invisible with it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 109. Steam Mephit — DEATH / HP-LIFECYCLE

**Blocking categories:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Death Burst`, `Innate Spellcasting`.

**Printed actions:** `Claws`, `Steam Breath (Recharge 6)`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:death-trigger`:** Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Death Burst:** Death Burst. When the mephit dies, it explodes in a cloud of steam. Each creature within 5 feet of the mephit must succeed on a DC 10 Dexterity saving throw or take 4 (1d8) fire damage.
- **Trait — Innate Spellcasting:** Innate Spellcasting.(1/Day). The mephit can innately cast blur, requiring no material components. Its innate spellcasting ability is Charisma.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 110. Stirge — SOURCE-ONLY / ARENA POLICY

**Blocking categories:** `arena:removed`. **Unbound named traits:** none separately listed.

**Printed actions:** `Blood Drain`.

**Fix queue for this monster:**
- **`arena:removed`:** Retain full source, record approved arena removal, no mechanical substitute.
- **Previously recorded specific ruling / dependency:** - **USER DECISION — REMOVED FOR NOW:** Retain source/stat block, but exclude Stirge from selectable arena roster. Do not build Blood Drain/attachment until revisited. This is an intentional exclusion, not combat certification.

**Reusable universal capabilities to inspect:** `action-economy` (supported). These are candidates, not proof of correct binding.

**Source action review:** No isolated unbound prose excerpt was found in the source parser for this category. Inspect the exact source action(s) above and existing structured binding (e.g. Swallow) to identify the failing generator gate; do not infer it works.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 111. Stone Giant — REACTIONS / TRIGGERS

**Blocking categories:** `source:reaction`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Rock`.

**Printed reactions:** `Rock Catching`.

**Fix queue for this monster:**
- **`source:reaction`:** Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.
- **Previously recorded specific ruling / dependency:** - **User ruling / queued:** Reuse existing 1 Reaction per round for Rock Catching: when a qualifying ranged attack hits, make DC 10 Dexterity save; pass negates damage, fail resolves ordinary damage and defenses. User broadened rock/similar hurled objects to ranged attacks as Iron Pit simplification; implementation must distinguish ranged attack hits from spells/AoE before activating. Source text remains unchanged. **Not implemented/certified.**

**Reusable universal capabilities to inspect:** `generic-reaction-trigger-grammar` (partial); `parry-redirect-reactions` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Reaction — Rock Catching:** Rock Catching. If a rock or similar object is hurled at the giant, the giant can, with a successful DC 10 Dexterity saving throw, catch the missile and take no bludgeoning damage from it.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 112. Storm Giant — RECHARGE / RESOURCES

**Blocking categories:** `mechanic:spellcasting`, `source:trait`. **Unbound named traits:** `Innate Spellcasting`.

**Printed actions:** `Multiattack`, `Greatsword`, `Rock`, `Lightning Strike (Recharge 5–6)`.

**Spell binding preflight:** prepared spell structure not populated, innate structure present. Read printed list, all slots/uses and each action's outcome.

**Fix queue for this monster:**
- **`mechanic:spellcasting`:** Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `recharge` (supported); `generic-limited-use-resources` (partial); `spell-attack-rolls` (supported); `concentration` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Innate Spellcasting:** Innate Spellcasting. The giant's innate spellcasting ability is Charisma (spell save DC 17). It can innately cast the following spells, requiring no material components:

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 113. Succubus/Incubus — FEAR / CHARM / STATUS

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Telepathic Bond`, `Shapechanger`.

**Printed actions:** `Claw (Fiend Form Only)`, `Charm`, `Draining Kiss`, `Etherealness`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Telepathic Bond:** Telepathic Bond. The fiend ignores the range restriction on its telepathy when communicating with a creature it has charmed. The two don't even need to be on the same plane of existence.
- **Trait — Shapechanger:** Shapechanger. The fiend can use its action to polymorph into a Small or Medium humanoid, or back into its true form. Without wings, the fiend loses its flying speed. Other than its size and speed, its statistics are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Action — Charm:** Charm. One humanoid the fiend can see within 30 feet of it must succeed on a DC 15 Wisdom saving throw or be magically charmed for 1 day. The charmed target obeys the fiend's verbal or telepathic commands. If the target suffers any harm or receives a suicidal command, it can repeat the saving throw, ending the effect on a success. If the target successfully saves against the effect, or if the effect on it ends, the target is immune to this fiend's Charm for the next 24 hours.
- **Action — Draining Kiss:** Draining Kiss. The fiend kisses a creature charmed by it or a willing creature. The target must make a DC 15 Constitution saving throw against this magic, taking 32 (5d10 + 5) psychic damage on a failed save, or half as much damage on a successful one. The target's hit point maximum is reduced by an amount equal to the damage taken. This reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0.
- **Action — Etherealness:** Etherealness. The fiend magically enters the Ethereal Plane from the Material Plane, or vice versa.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 114. Tarrasque — FEAR / CHARM / STATUS

**Blocking categories:** `mechanic:legendary`, `mechanic:swallow`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Reflective Carapace`.

**Printed actions:** `Multiattack`, `Bite`, `Claw`, `Horns`, `Tail`, `Frightful Presence`, `Swallow`.

**Printed legendary choices:** `Attack`, `Move`, `Chomp (Costs 2 Actions)`.

**Fix queue for this monster:**
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`mechanic:swallow`:** Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `legendary-actions` (supported); `grappled-restrained-escape` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Reflective Carapace:** Reflective Carapace. Any time the tarrasque is targeted by a magic missile spell, a line spell, or a spell that requires a ranged attack roll, roll a d6. On a 1 to 5, the tarrasque is unaffected. On a 6, the tarrasque is unaffected, and the effect is reflected back at the caster as though it originated from the tarrasque, turning the caster into the target.
- **Action — Frightful Presence:** Frightful Presence. Each creature of the tarrasque's choice within 120 feet of it and aware of it must succeed on a DC 17 Wisdom saving throw or become frightened for 1 minute. A creature can repeat the saving throw at the end of each of its turns, with disadvantage if the tarrasque is within line of sight, ending the effect on itself on a success. If a creature's saving throw is successful or the effect ends for it, the creature is immune to the tarrasque's Frightful Presence for the next 24 hours.
- **Action — Swallow:** Swallow. The tarrasque makes one bite attack against a Large or smaller creature it is grappling. If the attack hits, the target takes the bite's damage, the target is swallowed, and the grapple ends. While swallowed, the creature is blinded and restrained, it has total cover against attacks and other effects outside the tarrasque, and it takes 56 (16d6) acid damage at the start of each of the tarrasque's turns.
- **Legendary action — Attack:** Attack. The tarrasque makes one claw attack or tail attack.
- **Legendary action — Move:** Move. The tarrasque moves up to half its speed.
- **Legendary action — Chomp (Costs 2 Actions):** Chomp (Costs 2 Actions). The tarrasque makes one bite attack or uses its Swallow.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 115. Vampire — FEAR / CHARM / STATUS

**Blocking categories:** `attack:incomplete`, `mechanic:legendary`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`. **Unbound named traits:** `Shapechanger`, `Misty Escape`, `Vampire Weaknesses`.

**Printed actions:** `Multiattack. (Vampire Form Only)`, `Unarmed Strike (Vampire Form Only)`, `Bite. (Bat or Vampire Form Only)`, `Charm`, `Children of the Night (1/Day)`.

**Printed legendary choices:** `Move`, `Unarmed Strike`, `Bite`.

**Incomplete source attacks:** `Unarmed Strike (Vampire Form Only)`, `Bite. (Bat or Vampire Form Only)`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`mechanic:legendary`:** Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:legendary`:** Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Shapechanger + Misty Escape + weaknesses: separate form state, zero-HP escape and environmental/debuff rules before legendary/actions.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `legendary-actions` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. If the vampire isn't in sunlight or running water, it can use its action to polymorph into a Tiny bat or a Medium cloud of mist, or back into its true form.
- **Trait — Misty Escape:** Misty Escape. When it drops to 0 hit points outside its resting place, the vampire transforms into a cloud of mist (as in the Shapechanger trait) instead of falling unconscious, provided that it isn't in sunlight or running water. If it can't transform, it is destroyed.
- **Trait — Vampire Weaknesses:** Vampire Weaknesses. The vampire has the following flaws:
- **Action — Charm:** Charm. The vampire targets one humanoid it can see within 30 feet of it. If the target can see the vampire, the target must succeed on a DC 17 Wisdom saving throw against this magic or be charmed by the vampire. The charmed target regards the vampire as a trusted friend to be heeded and protected. Although the target isn't under the vampire's control, it takes the vampire's requests or actions in the most favorable way it can, and it is a willing target for the vampire's bite attack.
- **Action — Children of the Night (1/Day):** Children of the Night (1/Day). The vampire magically calls 2d4 swarms of bats or rats (swarm of bats, swarm of rats), provided that the sun isn't up. While outdoors, the vampire can call 3d6 wolves (wolf) instead. The called creatures arrive in 1d4 rounds, acting as allies of the vampire and obeying its spoken commands. The beasts remain for 1 hour, until the vampire dies, or until the vampire dismisses them as a bonus action.
- **Legendary action — Move:** Move. The vampire moves up to its speed without provoking opportunity attacks.
- **Legendary action — Unarmed Strike:** Unarmed Strike. The vampire makes one unarmed strike.
- **Legendary action — Bite:** Bite.(Costs 2 Actions). The vampire makes one bite attack.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 116. Vampire Spawn — DEATH / HP-LIFECYCLE

**Blocking categories:** `attack:incomplete`, `multiattack:complex`, `source:trait`. **Unbound named traits:** `Vampire Weaknesses`.

**Printed actions:** `Multiattack`, `Claws`, `Bite`.

**Incomplete source attacks:** `Claws`, `Bite`.

**Fix queue for this monster:**
- **`attack:incomplete`:** Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Vampire Weaknesses: evaluate environment-derived damage/restrictions plus existing attack riders.

**Reusable universal capabilities to inspect:** `generic-death-triggers` (partial); `zero-hp-death-lifecycle` (supported); `multiattack-extra-attack` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Vampire Weaknesses:** Vampire Weaknesses. The vampire has the following flaws:
- **Incomplete attack — Claws:** Claws. Melee Weapon Attack: +6 to hit, reach 5 ft., one creature. Hit: 8 (2d4 + 3) slashing damage. Instead of dealing damage, the vampire can grapple the target (escape DC 13).
- **Incomplete attack — Bite:** Bite. Melee Weapon Attack: +6 to hit, reach 5 ft., one willing creature, or a creature that is grappled by the vampire, incapacitated, or restrained. Hit: 6 (1d6 + 3) piercing damage plus 7 (2d6) necrotic damage. The target's hit point maximum is reduced by an amount equal to the necrotic damage taken, and the vampire regains hit points equal to that amount. The reduction lasts until the target finishes a long rest. The target dies if this effect reduces its hit point maximum to 0.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 117. Vrock — FEAR / CHARM / STATUS

**Blocking categories:** `mechanic:recharge`, `source:extra-action`. **Unbound named traits:** none separately listed.

**Printed actions:** `Multiattack`, `Beak`, `Talons`, `Spores (Recharge 6)`, `Stunning Screech (1/Day)`.

**Printed action recharge mapping:** `{"spores":6}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Reusable universal capabilities to inspect:** `saving-throws` (supported); `condition-immunity` (supported); `timed-condition-lifecycle-repeat-save` (supported); `recharge` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Action — Spores (Recharge 6):** Spores (Recharge 6). A 15-foot-radius cloud of toxic spores extends out from the vrock. The spores spread around corners. Each creature in that area must succeed on a DC 14 Constitution saving throw or become poisoned. While poisoned in this way, a target takes 5 (1d10) poison damage at the start of each of its turns. A target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success. Emptying a vial of holy water on the target also ends the effect on it.
- **Action — Stunning Screech (1/Day):** Stunning Screech (1/Day). The vrock emits a horrific screech. Each creature within 20 feet of it that can hear it and that isn't a demon must succeed on a DC 14 Constitution saving throw or be stunned until the end of the vrock's next turn.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 118. Water Elemental — RESTRAINT / SWALLOW

**Blocking categories:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Water Form`, `Freeze`.

**Printed actions:** `Multiattack`, `Slam`, `Whelm (Recharge 4–6)`.

**Printed action recharge mapping:** `{"whelm":4}`.

**Fix queue for this monster:**
- **`mechanic:recharge`:** Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Water Form/Freeze: reuse space/water traversal and susceptibility/condition with actual trigger.

**Reusable universal capabilities to inspect:** `grappled-restrained-escape` (supported); `ongoing-periodic-damage` (supported); `recharge` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Water Form:** Water Form. The elemental can enter a hostile creature's space and stop there. It can move through a space as narrow as 1 inch wide without squeezing.
- **Trait — Freeze:** Freeze. If the elemental takes cold damage, it partially freezes; its speed is reduced by 20 feet until the end of its next turn.
- **Action — Whelm (Recharge 4–6):** Whelm (Recharge 4–6). Each creature in the elemental's space must make a DC 15 Strength saving throw. On a failure, a target takes 13 (2d8 + 4) bludgeoning damage. If it is Large or smaller, it is also grappled (escape DC 14). Until this grapple ends, the target is restrained and unable to breathe unless it can breathe water. If the saving throw is successful, the target is pushed out of the elemental's space.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 119. Werebear — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `multiattack:complex`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Multiattack`, `Bite (Bear or Hybrid Form Only)`, `Claw (Bear or Hybrid Form Only)`, `Greataxe (Humanoid or Hybrid Form Only)`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The werebear can use its action to polymorph into a Large bear-humanoid hybrid or into a Large bear, or back into its true form, which is humanoid. Its statistics, other than its size and AC, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 120. Wereboar — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Multiattack (Humanoid or Hybrid Form Only)`, `Maul (Humanoid or Hybrid Form Only)`, `Tusks (Boar or Hybrid Form Only)`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The wereboar can use its action to polymorph into a boar-humanoid hybrid or into a boar, or back into its true form, which is humanoid. Its statistics, other than its AC, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 121. Wererat — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Multiattack (Humanoid or Hybrid Form Only)`, `Bite (Rat or Hybrid Form Only)`, `Shortsword (Humanoid or Hybrid Form Only)`, `Hand Crossbow (Humanoid or Hybrid Form Only)`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The wererat can use its action to polymorph into a rat-humanoid hybrid or into a giant rat, or back into its true form, which is humanoid. Its statistics, other than its size, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 122. Weretiger — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`, `Pounce (Tiger or Hybrid Form Only)`.

**Printed actions:** `Multiattack (Humanoid or Hybrid Form Only)`, `Bite (Tiger or Hybrid Form Only)`, `Claw (Tiger or Hybrid Form Only)`, `Scimitar (Humanoid or Hybrid Form Only)`, `Longbow (Humanoid or Hybrid Form Only)`.

**Fix queue for this monster:**
- **`multiattack:complex`:** Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The weretiger can use its action to polymorph into a tiger-humanoid hybrid or into a tiger, or back into its true form, which is humanoid. Its statistics, other than its size, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.
- **Trait — Pounce (Tiger or Hybrid Form Only):** Pounce (Tiger or Hybrid Form Only). If the weretiger moves at least 15 feet straight toward a creature and then hits it with a claw attack on the same turn, that target must succeed on a DC 14 Strength saving throw or be knocked prone. If the target is prone, the weretiger can make one bite attack against it as a bonus action.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 123. Werewolf — SHAPECHANGE / TRANSFORMATION

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Shapechanger`.

**Printed actions:** `Multiattack. (Humanoid or Hybrid Form Only)`, `Bite (Wolf or Hybrid Form Only)`, `Claws. (Hybrid Form Only)`, `Spear (Humanoid Form Only)`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Reusable universal capabilities to inspect:** `multiattack-extra-attack` (supported); `summons-transformations-splitting` (unsupported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Shapechanger:** Shapechanger. The werewolf can use its action to polymorph into a wolf-humanoid hybrid or into a wolf, or back into its true form, which is humanoid. Its statistics, other than its AC, are the same in each form. Any equipment it is wearing or carrying isn't transformed. It reverts to its true form if it dies.

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

### 124. Will-o'-Wisp — GAZE / SIGHT / INVISIBILITY

**Blocking categories:** `source:extra-action`, `source:trait`. **Unbound named traits:** `Consume Life`, `Ephemeral`, `Variable Illumination`.

**Printed actions:** `Shock`, `Invisibility`.

**Fix queue for this monster:**
- **`source:extra-action`:** Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- **`source:trait`:** Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- **Previously recorded specific ruling / dependency:** - **Known directed work:** Consume Life/Ephemeral/Variable Illumination: separate HP-threshold/terminal trigger, movement/material interactions and illumination.

**Reusable universal capabilities to inspect:** `blinded` (supported); `cover-line-of-sight-obscurement` (partial); `saving-throws` (supported). These are candidates, not proof of correct binding.

**Relevant printed source excerpts:**
- **Trait — Consume Life:** Consume Life. As a bonus action, the will-o'-wisp can target one creature it can see within 5 feet of it that has 0 hit points and is still alive. The target must succeed on a DC 10 Constitution saving throw against this magic or die. If the target dies, the will-o'-wisp regains 10 (3d6) hit points.
- **Trait — Ephemeral:** Ephemeral. The will-o'-wisp can't wear or carry anything.
- **Trait — Variable Illumination:** Variable Illumination. The will-o'-wisp sheds bright light in a 5- to 20-foot radius and dim light for an additional number of feet equal to the chosen radius. The will-o'-wisp can alter the radius as a bonus action.
- **Action — Invisibility:** Invisibility. The will-o'-wisp and its light magically become invisible until it attacks or uses its Consume Life, or until its concentration ends (as if concentrating on a spell).

**Next step:** Map every listed category to the *existing* Python/browser path, identify only genuine gaps, implement and test the actual event/turn pipeline and reset, regenerate, and gate the **exact new head**. **Status: BLUEPRINT ONLY.**

## Queue-maintenance gates

- [ ] Reconcile source admission and remove only verified cleared packets after #673 or other merges.
- [ ] Source-audit and take an independent queued mechanic while CI runs, without starting a duplicate PR.
- [ ] Track new universal primitive IDs in the inventory for later 2024/hero/homebrew reuse.
- [ ] Update parent [#675](https://github.com/cbw29512/D20-ironpit/issues/675) and staged #676–#679 tickets on actual implementation/merge.
