# 2014 Lore Bard 1–20 Capability Audit

## Scope

Canonical hero: **Lyra Silverstring**, 2014 Bard, College of Lore.

This is a preparation/capability document, not a READY manifest. The source authority is the D&D Basic Rules 2014 / SRD 5.1 Bard and College of Lore. The canonical deterministic 2014 build uses Human + Entertainer, Charisma first, Dexterity second, and one persistent character from level 1 through 20.

## RAW progression

| Level | Combat-relevant additions | Iron Pit disposition |
| --- | --- | --- |
| 1 | Spellcasting; Bardic Inspiration d6 | Spell slots/actions reuse existing spell engine. Inspiration requires source-neutral transferable d20 bonus-die state. |
| 2 | Jack of All Trades | Generic nonproficient ability-check bonus. Song of Rest is between-fight/short-rest support and does not alter a fresh Pit fight. |
| 3 | College of Lore; Cutting Words; Expertise | Expertise is skill-data. Cutting Words requires universal reaction roll/damage subtraction with hearing/charm-immunity gate. |
| 4 | ASI | Data only. |
| 5 | Inspiration d8; Font of Inspiration | Die-size/resource recovery data. Fresh Pit fights begin restored; short-rest reset semantics remain source metadata. |
| 6 | Countercharm; Additional Magical Secrets | Countercharm is a timed 30-ft ally save-Advantage aura vs Charmed/Frightened. Magical Secrets expands spell data only. |
| 7 | 4th-level spells | Existing slot/spell primitives where spells are supported. |
| 8 | ASI | Data only. |
| 9 | Song of Rest d8 | Arena-neutral under fresh-fight model. |
| 10 | Inspiration d10; Expertise; Magical Secrets | Die size/data; spell expansion. |
| 11 | 6th-level spells | Spell data. |
| 12 | ASI | Data only. |
| 13 | Song of Rest d10; 7th-level spells | Song of Rest arena-neutral; spell data. |
| 14 | Magical Secrets; Peerless Skill | Peerless Skill is resource-backed additive Bardic Inspiration die on own ability check; reuse generic failed-d20/additive revision path with ability-check eligibility. |
| 15 | Inspiration d12; 8th-level spells | Die-size/spell data. |
| 16 | ASI | Data only. |
| 17 | Song of Rest d12; 9th-level spells | Song of Rest arena-neutral; spell data. |
| 18 | Magical Secrets | Spell data. |
| 19 | ASI | Data only. |
| 20 | Superior Inspiration | Initiative-start conditional resource refill: if Bardic Inspiration uses are 0, restore 1. Reuse generic initiative resource refill semantics if compatible. |

## Existing universal reuse

- Spell slots, spell attack/save actions, healing actions, concentration, conditions, and modifier-stack behavior.
- ResourceDefinition / ResourceState for Bardic Inspiration uses.
- Roll revision evidence and additive bonus-die handling already exist for saving throws/ability checks.
- Initiative resource refill already exists for other class features and should be parameterized, not duplicated.
- Saving-throw Advantage and source-owned timed effects exist for Countercharm composition.
- Exact source names remain presentation/log metadata.

## Blockers

### Bardic Inspiration
**ENGINE_TRULY_MISSING or narrow extension of existing bonus-die machinery.**

The current FailedD20BonusDieGrant is owner-only and limited to saving throws/ability checks after failure. 2014 Bardic Inspiration is transferable to another creature, can affect attack rolls, ability checks, or saving throws, is granted by the Bard's Bonus Action, persists up to 10 minutes, and is consumed when the recipient chooses to roll it. Implement this as a universal transferable resource-backed d20 bonus-die effect, not a Bard-name resolver.

### Cutting Words
**ENGINE_TRULY_MISSING unless the reaction-interrupt audit finds a compatible generic reducer.**

Semantics:
- reaction;
- visible/heard creature within 60 ft;
- spend Bardic Inspiration;
- subtract Bardic Inspiration die from attack roll, ability check, or damage roll;
- target is immune if it cannot hear the Bard or is immune to Charmed.

The engine needs one universal reaction roll/damage reduction primitive usable by future monsters/features.

### Countercharm
**ENGINE_EXISTS_BINDING_MISSING / possible narrow aura extension.**

Existing save-Advantage and timed/source-owned effects cover most behavior. Required parameters: Action activation, 30-ft friendly aura, until end of Bard's next turn, Advantage on saves against Charmed/Frightened, ends early if source is incapacitated/silenced.

### Peerless Skill
**ENGINE_EXISTS_BINDING_MISSING with generic d20 additive revision extension.**

Owner-only ability-check bonus using Bardic Inspiration die. It is not a replacement roll and should share the additive roll-revision path.

### Superior Inspiration
**ENGINE_EXISTS_BINDING_MISSING.**

Use generic initiative resource-refill semantics: when initiative is rolled and resource is at 0, restore exactly 1 use.

## Initial deterministic build decisions

- Species: Human (2014 standard human, +1 all abilities).
- Background: Entertainer.
- Starting ability array before species: CHA 15, DEX 14, CON 13, WIS 12, INT 10, STR 8.
- Starting equipment: Rapier, Entertainer's Pack, lute, leather armor, dagger.
- ASI plan: level 4 +2 CHA; level 8 +2 DEX; level 12 +2 CON; level 16 +2 DEX; level 19 +2 CON.
- This plan is persistent and may only change through an explicit audited build decision.

## Implementation order

1. Compile legal immutable profile/resource/slot progression 1–20 without READY registration.
2. Add transferable bonus-die effect for Bardic Inspiration with Python/browser parity.
3. Bind Countercharm to universal timed aura/save-Advantage behavior.
4. Add generic reaction reducer for Cutting Words if no equivalent exists.
5. Bind Peerless Skill and Superior Inspiration.
6. Add only supported combat spells; unsupported outcome-changing spells remain explicit blockers rather than being silently omitted.
7. Run targeted Bard smoke tests during the lane.
8. Add Lyra to certification only after all combat-relevant mechanics selected for her legal build are represented and browser/reference parity is complete.
