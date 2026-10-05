# Iron Pit locked rules

This is the single index of **Chris-locked** Iron Pit rules. It exists so those locks are not lost in chat.

It does **not** replace `docs/IRON_PIT_RULES_CONTRACT.md`. That file remains the detailed product/combat contract. Architecture, battlefield UI, and pregen construction stay in their existing docs. If this index and a cited file disagree, stop and reconcile in the cited file. Do not write a third copy of the same rule.

## Engineering

- **Audit and reuse first.** Before any new mechanic, decompose the printed behavior and search the existing hero and monster primitive inventory. Reuse or parameterize a match. Compose from existing primitives when one named ability is several mechanics. Unique code is allowed only for a genuinely unique remainder.
- **Universal conditions.** Prone is Prone, Grappled is Grappled, Frightened is Frightened, Poisoned is Poisoned, and the same for every other shared condition, save, Advantage, and Disadvantage. The card supplies parameters. The engine supplies the mechanic.
- **Printed names in the log.** The player log and card keep the exact source ability name. Engine dispatch uses generic primitive IDs, never class/monster/ability-name branches.
- **2014 families first, then bind 2024.** Finish the 2014 source roster family before expanding an independent 2024 mechanic. After a 2014 primitive is certified, audit 2024 for direct reuse. Edition cards supply printed numbers; do not duplicate engine behavior.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §1.1, §2, §25; `SOUL.md`; `AGENTS.md` semantic-reuse and 2014-first monster order.

## Death and dying

- **Dead is terminal.** No resurrection, rebirth, revive, later stabilization, regeneration, or Death Saving Throw restores a Dead combatant in that match. The Pit deity restores combatants only after combat.
- **Death Saving Throws only while dying.** They occur only while a character is Unconscious/dying at 0 HP and not Dead. Printed 0-HP replacements intercept the drop to 0 in the same resolution and never leave the combatant Dead first.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §13.

## Pit exceptions

These are explicit arena overrides, not RAW changes outside the Pit.

- **No Flyby leave-reach exemption.** An opportunity-attack exemption does not authorize leaving engagement.
- **No teleport relocation, plane shift, summoning, or vertical flight.**
- **Natural 1 ends the turn.** A natural 1 on an attack roll is an automatic miss and immediately ends that creature's current turn. It does not undo earlier resolutions.
- **Teleport only clears matching movement debuffs in place.** Grappled, Restrained, and other `ends_on_teleport` / ground-snare effects may end. Grid x/y does not change.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §7, Attack natural 1, §10.1, §20.

## Buffs, debuffs, and match lifecycle

- **A buff cancels the matching debuff.** Pairing is by condition identity and modifier kind, never by spell/monster/class name. An already-active matching counter-buff suppresses the current condition and causes a new copy of that debuff to fail closed.
- **Debuffs are checked at the start of the creature's turn** before it acts.
- **Calm blocks new fear.** 2014 Calm Emotions uses the shared charm/frighten suppression / condition-immunity primitives. While that suppression is active, a new Frightened copy does not land.
- **Cards are immutable.** Fight mutation belongs only to temporary combat state.
- **Match end resets all effects.**
- **Printed 24-hour immunities are match-scoped.** They last for the rest of the current fight only. Do not simulate calendar 24 hours and do not persist immunity across fights.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §3, §8 Turn-start buff versus debuff, Calm Emotions, §10.1, §16.

## Casters and pregen weapons

- **Casters use the highest-level spell first** and prefer straight damage spells among legal damaging options.
- **Pregen manufactured weapons are fixed by level.** No random hoard rolls. Same level always gets the same gear.
  - Levels 1–4: PHB silvered material only. Qualifier `silvered`. +0 to hit and damage.
  - Levels 5–10: DMG Table F **Weapon +1**. Qualifier `magical`. +1 / +1.
  - Levels 11–16: DMG Table G **Weapon +2**. Qualifier `magical`. +2 / +2.
  - Levels 17–20: DMG Table H **Weapon +3**. Qualifier `magical`. +3 / +3.
- Silvered is a PHB special-material cost, not a magic-item table roll. A Weapon +N is not also silvered or adamantine.
- **Monster defenses stay on the monsters.** Do not strip printed nonmagical / silvered / adamantine clauses.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §8, §22, §23; `docs/CANONICAL_COMBAT_BUILD_POLICY.md`.

## Attack resolution flow

1. To-hit bonus + d20 versus AC.
2. Natural 20 is a critical: automatic hit; double all damage dice required by the selected ruleset. Natural 1 is a miss and ends the turn.
3. Apply per-type resistance, vulnerability, and immunity to base damage and to each rider separately.
4. Total the accepted components, then apply that total to Temporary HP / HP.
5. Then resolve the on-hit condition save, if any. Condition immunity skips the save and the condition. A failed save applies the shared debuff with the printed duration and repeat-save timing.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §1.2, Attack natural 1 / 20, §11, §14; `docs/COMBAT_RESOLUTION_PIPELINE.md`.

## UI and publish

- **UI is arena-first.** Buyer-facing copy. Touch-sized trash control on each filled card. Fight options stay on the bar below the six-slot arena. Logs are readable and downloadable. Certification/engine jargon does not belong in the main Pit.
- **One big Netlify push only.** Routine development and verification stay in repository CI. Production publish requires Chris to unlock Iron Pit. Completing a feature, PR, or merge is not publish approval.

Authority: `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md`; `docs/IRON_PIT_RULES_CONTRACT.md` §28; `AGENTS.md` Netlify lock.
