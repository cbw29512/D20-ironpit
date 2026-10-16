> **Superseded historical evidence.** Not the live execution cursor. See [MONSTER_ABILITY_WORK_QUEUE.md](MONSTER_ABILITY_WORK_QUEUE.md). Old Actions URLs in this file will age out.

# 2014 monster trait audit — 82 currently blocked monsters

Audit basis: generated `docs/MONSTER_BLOCKERS_2014.md` on `main` and `docs/UNIVERSAL_MECHANIC_INVENTORY.md`, October 12, 2026. This is **semantic triage**, not a claim that all 82 source wordings, individual runtime bindings or Python/browser certification tests have been exhaustively verified. **REUSE / VERIFY** means a matching shared capability exists conceptually but source-specific binding/coverage must be inspected and tested, not that the monster is certified. **NEUTRAL** means the trait appears inactive under locked standard-arena rules; validate full printed clause before compiler exemption. **NEW** means a missing shared semantic/lifecycle requiring implementation or verified composition of partial primitives. No monster has been promoted by this audit.

| Monster (82) | Source-printed unbound trait → classification | Required follow-up / rationale |
|---|---|---|
| Aboleth | `Probing Telepathy` **NEUTRAL** | Probing Telepathy: Thought probing not a combat action/target locator with supported arena effects. |
| Acolyte | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Air Elemental | `Air Form` **NEW** | Air Form: Shared-square occupancy, hostile overlap and passing occupied spaces require generic grid rules. |
| Androsphinx | `Inscrutable` **REUSE / VERIFY**; `Spellcasting` **REUSE / VERIFY** | Inscrutable: Source-driven immunity to divination/emotion reading; preserve irrelevant clauses, verify magic-save rider. Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Archmage | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Balor | `Death Throes` **NEW**; `Fire Aura` **REUSE / VERIFY** | Death Throes: Generic death-trigger area damage/save with full Python/browser lifecycle. Fire Aura: Existing aura/damage-on-contact events; validate trigger timing and typed damage. |
| Banshee | `Detect Life` **NEUTRAL** | Detect Life: Detection of hidden life is not a combat target/reveal mechanism in standard arena; retain card. |
| Basilisk | `Petrifying Gaze` **NEW** | Petrifying Gaze: General start-turn gaze, eye-avert choice, source-linked staged saving throws and petrification. |
| Bearded Devil | `Steadfast` **REUSE / VERIFY** | Steadfast: Existing active nearby ally conditional Frightened immunity; verify source-bound monster gating. |
| Chuul | `Sense Magic` **NEUTRAL** | Sense Magic: Detect magic presence alone; does not reveal an invisible enemy's location. |
| Cloaker | `Damage Transfer` **NEW**; `Light Sensitivity` **REUSE / VERIFY** | Damage Transfer: Generic attached-victim damage share, prevention of cycles and correct typed HP resolution. Light Sensitivity: Generic bright-light disadvantage; no default bright sun unless effect supplies context. |
| Cloud Giant | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Couatl | `Innate Spellcasting` **REUSE / VERIFY**; `Shielded Mind` **NEUTRAL** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. Shielded Mind: Scrying, emotion, mind-reading and location detection do not affect standard arena. |
| Cult Fanatic | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Deep Gnome (Svirfneblin) | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Deva | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Djinni | `Elemental Demise` **NEUTRAL**; `Innate Spellcasting` **REUSE / VERIFY** | Elemental Demise: Return to elemental plane on death; no extra arena combat action/effect. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Doppelganger | `Shapechanger` **REUSE / VERIFY**; `Ambusher` **REUSE / VERIFY**; `Surprise Attack` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. Ambusher: Existing initiative/first-round advantage primitives; confirm exact trigger. Surprise Attack: Existing initiative-opener damage semantic; verify source binding. |
| Drider | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Drow | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Druid | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Dryad | `Innate Spellcasting` **REUSE / VERIFY**; `Speak with Beasts and Plants` **NEUTRAL**; `Tree Stride` **NEUTRAL** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. Speak with Beasts and Plants: Communication-only ability; no arena combat interaction. Tree Stride: No trees in standard arena; preserve source action/trait. |
| Duergar | `Duergar Resilience` **REUSE / VERIFY** | Duergar Resilience: Existing defensive advantage/condition resistance; bind exact save contexts. |
| Dust Mephit | `Death Burst` **NEW**; `Innate Spellcasting` **REUSE / VERIFY** | Death Burst: Reusable on-death radius, saving throw, damage/half and friend-or-foe filter. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Efreeti | `Elemental Demise` **NEUTRAL**; `Innate Spellcasting` **REUSE / VERIFY** | Elemental Demise: Return to elemental plane on death; no extra arena combat action/effect. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Erinyes | `Hellish Weapons` **REUSE / VERIFY** | Hellish Weapons: Existing weapon-on-hit typed damage components. |
| Fire Elemental | `Fire Form` **NEW**; `Water Susceptibility` **NEUTRAL** | Fire Form: Passive contact and space-entry burn with shared-space movement and repeated event handling. Water Susceptibility: No water terrain in arena; preserve printed water damage clause. |
| Flameskull | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Gelatinous Cube | `Ooze Cube` **NEW**; `Transparent` **REUSE / VERIFY** | Ooze Cube: Transparent collision/Engulf, creature occupancy and restrain/escape semantics. Transparent: Visibility/surprise conditional trait; source-aware passive Stealth/notice. |
| Ghost | `Ethereal Sight` **NEUTRAL** | Ethereal Sight: No ethereal combatants/movement; keep source trait. |
| Gibbering Mouther | `Aberrant Ground` **NEW**; `Gibbering` **NEW** | Aberrant Ground: Source-driven difficult terrain aura/field + position lifecycle. Gibbering: Start-turn hearing-based saving throw, confusion action outcomes and immunity gating. |
| Glabrezu | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Gray Ooze | `Corrode Metal` **NEUTRAL** | Corrode Metal: Equipment deterioration excluded from arena weapon/armor durability rules; retain printed trait. |
| Green Hag | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Guardian Naga | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Gynosphinx | `Inscrutable` **REUSE / VERIFY**; `Spellcasting` **REUSE / VERIFY** | Inscrutable: Source-driven immunity to divination/emotion reading; preserve irrelevant clauses, verify magic-save rider. Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Homunculus | `Telepathic Bond` **NEUTRAL** | Telepathic Bond: Telepathic communication/location-of-master does not change standard combat targeting. |
| Hydra | `Multiple Heads` **NEW**; `Reactive Heads` **NEW** | Multiple Heads: Reusable multiple-head independent lifecycle and awareness; shared Hydra source semantics. Reactive Heads: Universal extra reactions keyed to surviving heads. |
| Ice Mephit | `Death Burst` **NEW**; `Innate Spellcasting` **REUSE / VERIFY** | Death Burst: Reusable on-death radius, saving throw, damage/half and friend-or-foe filter. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Imp | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Kraken | `Freedom of Movement` **REUSE / VERIFY** | Freedom of Movement: Already supported movement debuff/immunity counters; inspect exact creature wording. |
| Lamia | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Lich | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Mage | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Magma Mephit | `Death Burst` **NEW**; `Innate Spellcasting` **REUSE / VERIFY** | Death Burst: Reusable on-death radius, saving throw, damage/half and friend-or-foe filter. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Magmin | `Death Burst` **NEW**; `Ignited Illumination` **REUSE / VERIFY** | Death Burst: Reusable on-death radius, saving throw, damage/half and friend-or-foe filter. Ignited Illumination: Existing illumination/property display; combat-relevant lighting only if engine models it. |
| Manticore | `Tail Spike Regrowth` **REUSE / VERIFY** | Tail Spike Regrowth: Resource refill at turn start/round as source-defined. |
| Marilith | `Reactive` **NEW** | Reactive: Multiple reactions per round with legal trigger budget. |
| Medusa | `Petrifying Gaze` **NEW** | Petrifying Gaze: General start-turn gaze, eye-avert choice, source-linked staged saving throws and petrification. |
| Mimic | `Shapechanger` **REUSE / VERIFY**; `Adhesive (Object Form Only)` **REUSE / VERIFY**; `False Appearance (Object Form Only)` **NEUTRAL**; `Grappler` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. Adhesive (Object Form Only): Existing on-contact owner Grapple, apply only in object form. False Appearance (Object Form Only): No deceptive exploration object-identity in standardized known-foe arena. Grappler: Existing advantage/target-ownership grapple attack primitives. |
| Mummy Lord | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Night Hag | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Nightmare | `Confer Fire Resistance` **REUSE / VERIFY** | Confer Fire Resistance: Existing transferable typed resistance and buff expiry/source ownership. |
| Oni | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Otyugh | `Limited Telepathy` **NEUTRAL** | Limited Telepathy: Communication-only trait, no combat targeting effect. |
| Pit Fiend | `Fear Aura` **REUSE / VERIFY**; `Innate Spellcasting` **REUSE / VERIFY** | Fear Aura: Existing emanation and Frightened saves; generic turn-based immunity may need binding. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Planetar | `Divine Awareness` **NEUTRAL**; `Innate Spellcasting` **REUSE / VERIFY** | Divine Awareness: Source-only lie-detection awareness; no arena relevance. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Priest | `Divine Eminence` **REUSE / VERIFY**; `Spellcasting` **REUSE / VERIFY** | Divine Eminence: Generic limited resource expenditure for on-hit radiant damage. Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Pseudodragon | `Limited Telepathy` **NEUTRAL** | Limited Telepathy: Communication-only trait, no combat targeting effect. |
| Quasit | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Rakshasa | `Limited Magic Immunity` **NEW**; `Innate Spellcasting` **REUSE / VERIFY** | Limited Magic Immunity: Source-conditioned spell level immunity and saving throw Advantage; preserve exceptions. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Roper | `Grasping Tendrils` **REUSE / VERIFY** | Grasping Tendrils: Existing grapple, escape, restrained, reach and target limit primitives; verify pull/target lifecycle. |
| Rug of Smothering | `Damage Transfer` **NEW** | Damage Transfer: Generic attached-victim damage share, prevention of cycles and correct typed HP resolution. |
| Rust Monster | `Iron Scent` **NEUTRAL**; `Rust Metal` **NEUTRAL** | Iron Scent: Metal location detection not a tactical target locator in the standardized arena. Rust Metal: Non-damage equipment corrosion/durability excluded; printed attack damage still separate. |
| Sea Hag | `Horrific Appearance` **NEW** | Horrific Appearance: Sight-based action/turn-start fear with source-owned immunity and special failure severity. |
| Shadow | `Sunlight Weakness` **NEUTRAL** | Sunlight Weakness: Standard arena has no sunlight; source context check required if introduced. |
| Shield Guardian | `Bound` **NEUTRAL**; `Spell Storing` **NEW** | Bound: Master/binding instructions and out-of-fight behavior; preserve traits. Spell Storing: Source-configured stored spell slot/action and release behavior, conditional on stored payload. |
| Solar | `Divine Awareness` **NEUTRAL**; `Innate Spellcasting` **REUSE / VERIFY** | Divine Awareness: Source-only lie-detection awareness; no arena relevance. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Spirit Naga | `Spellcasting` **REUSE / VERIFY** | Spellcasting: Existing caster/slots/actions; inspect each printed spell and missing effect. |
| Steam Mephit | `Death Burst` **NEW**; `Innate Spellcasting` **REUSE / VERIFY** | Death Burst: Reusable on-death radius, saving throw, damage/half and friend-or-foe filter. Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Storm Giant | `Innate Spellcasting` **REUSE / VERIFY** | Innate Spellcasting: Existing innate spell slots/at-will casting; audit source spells/AI. |
| Succubus/Incubus | `Telepathic Bond` **NEUTRAL**; `Shapechanger` **REUSE / VERIFY** | Telepathic Bond: Telepathic communication/location-of-master does not change standard combat targeting. Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Tarrasque | `Reflective Carapace` **NEW** | Reflective Carapace: Source-driven spell attack immunity and ray/line reflection targeting via Reaction-free trait. |
| Vampire | `Shapechanger` **REUSE / VERIFY**; `Misty Escape` **NEW**; `Vampire Weaknesses` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. Misty Escape: Zero-HP form/reposition/lair restrictions; requires source-specific death override composition. Vampire Weaknesses: Sunlight/running-water/invitation/stake clauses mostly arena-neutral; regeneration/healing exceptions require source verification. |
| Vampire Spawn | `Vampire Weaknesses` **REUSE / VERIFY** | Vampire Weaknesses: Sunlight/running-water/invitation/stake clauses mostly arena-neutral; regeneration/healing exceptions require source verification. |
| Water Elemental | `Water Form` **NEW**; `Freeze` **NEW** | Water Form: Move through occupied spaces, enter creature space and water-specific damage resistance. Freeze: Cold-damage-triggered speed reduction, timed stack/expiry and source gates. |
| Werebear | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Wereboar | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Wererat | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Weretiger | `Shapechanger` **REUSE / VERIFY**; `Pounce (Tiger or Hybrid Form Only)` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. Pounce (Tiger or Hybrid Form Only): Existing charge/movement hit -> prone/save/bonus bite sequence with form gate. |
| Werewolf | `Shapechanger` **REUSE / VERIFY** | Shapechanger: Existing alternate form overlay where combat-significant; neutral cosmetic shape changes only. Audit each printed form. |
| Will-o'-Wisp | `Consume Life` **NEW**; `Ephemeral` **REUSE / VERIFY**; `Variable Illumination` **REUSE / VERIFY** | Consume Life: Zero-HP target targeting and death-trigger heal/action legality. Ephemeral: Existing anti-grapple/restrain effects + incorporeal movement restriction. Variable Illumination: Existing optional light-radius state; no default damage; source visual effect. |

## Implementation handling

1. **REUSE / VERIFY:** look up the exact existing Python/browser universal capability, check exact printed triggers/saves/targets/durations, bind without monster-name runtime dispatch, test both environments. Spellcasting and form-change often have uncovered clauses—do not automatically admit.
2. **NEUTRAL:** inspect original trait fully. Only apply an arena-neutral source-classification when every printed clause is irrelevant under locked arena context; retain immutable card text. Do not assume a similar-sounding trait has identical semantics.
3. **NEW:** organize by generic trigger/event type, add smallest reusable cross-monster primitive to Python/browser, test source-specific metadata and lifecycle before reclassifying any monster.
4. Regenerate the authoritative blocker report, then evaluate each monster's **other** unresolved blockers. A cleared trait does not automatically mean a complete monster.

**Trait incidences, not distinct monsters:** NEUTRAL: 22; REUSE / VERIFY: 71; NEW: 26. Some of 82 monsters have multiple listed traits and mixed classifications.
