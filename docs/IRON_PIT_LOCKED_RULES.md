# Iron Pit locked rules

This is the single index of **Chris-locked** Iron Pit rules. It exists so those locks are not lost in chat.

It does **not** replace `docs/IRON_PIT_RULES_CONTRACT.md`. That file remains the detailed product/combat contract. Architecture, battlefield UI, and pregen construction stay in their existing docs. If this index and a cited file disagree, stop and reconcile in the cited file. Do not write a third copy of the same rule.

## Engineering

- **Audit and reuse first.** Before any new mechanic, decompose the printed behavior and search the existing hero and monster primitive inventory. Reuse or parameterize a match. Compose from existing primitives when one named ability is several mechanics. Unique code is allowed only for a genuinely unique remainder.
- **Universal conditions.** Prone is Prone, Grappled is Grappled, Frightened is Frightened, Poisoned is Poisoned, and the same for every other shared condition, save, Advantage, and Disadvantage. The card supplies parameters. The engine supplies the mechanic.
- **Printed names in the log.** The player log and card keep the exact source ability name. Engine dispatch uses generic primitive IDs, never class/monster/ability-name branches.
- **2014 families first, then bind 2024.** Finish the 2014 source roster family before expanding an independent 2024 mechanic. After a 2014 primitive is certified, audit 2024 for direct reuse. Edition cards supply printed numbers; do not duplicate engine behavior.
- **Do not stall a family on one blocker.** If a monster, item, spell, or feature hits a real blocker (needs new engine support, RAW ambiguity, missing primitive, or a Chris decision), park that card. Record it below with the printed name, the blocker, and why it cannot ship yet. Keep moving to the next creature or family. Come back to parked items only after the rest of the current family is finished. Do not guess, invent a special case, or strip a printed mechanic to make the card READY. Unsupported outcome-changing mechanics still fail closed.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §1.1, §2, §25; `SOUL.md`; `AGENTS.md` semantic-reuse, 2014-first monster order, and uncertainty gate.

- **2014 Immutable Form is arena-neutral only while no supported hostile form-alter effect exists.** The current replacement-form system changes the acting combatant's own form; it does not alter an opposing golem. Keep the printed trait in source/card/log metadata. If a hostile Polymorph/form-alter capability becomes supported, remove this arena-neutral classification and bind the universal form-alter immunity before certifying affected golems.

## Death and dying

- **Antimagic Susceptibility is terminal in the Iron Pit.** An applied semantic `antimagic` effect kills a susceptible combatant. Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §13, Antimagic susceptibility.
- **Dispel Magic uses Stunned for susceptible creatures.** Reuse the shared 10-round debuff; this supersedes the earlier Dispel-also-kills choice. Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §13, Antimagic susceptibility.
- **Petrified is terminal in the Iron Pit.** When the Petrified debuff is successfully applied, that combatant is immediately Dead for the rest of the match. This is an explicit Iron Pit arena rule, not a statement of tabletop RAW. The universal condition engine owns this consequence; monster/ability names must not dispatch it.
- **Dead is terminal.** No resurrection, rebirth, revive, later stabilization, regeneration, or Death Saving Throw restores a Dead combatant in that match. The Pit deity restores combatants only after combat.
- **Death Saving Throws only while dying.** They occur only while a character is Unconscious/dying at 0 HP and not Dead. Printed 0-HP replacements intercept the drop to 0 in the same resolution and never leave the combatant Dead first.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §13.

## Pit exceptions

These are explicit arena overrides, not RAW changes outside the Pit.

- **No Flyby leave-reach exemption.** An opportunity-attack exemption does not authorize leaving engagement.
- **No teleport relocation, plane shift, ethereal/incorporeal movement state, summoning, or vertical flight.**
- **Natural 1 ends the turn.** A natural 1 on an attack roll is an automatic miss and immediately ends that creature's current turn. It does not undo earlier resolutions.
- **Teleport only clears matching movement debuffs in place.** Grappled, Restrained, and other `ends_on_teleport` / ground-snare effects may end. Grid x/y does not change.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §7, Attack natural 1, §10.1, §20.

- **2014 Rampage omits its movement rider in the Pit.** A qualifying own-turn melee reduction to 0 HP grants exactly one Bite through the creature's available Bonus Action when a legal target exists; no Rampage movement is granted or required. This is an explicit Iron Pit arena simplification, not tabletop RAW. Runtime uses the generic zero-HP trigger plus Bonus Action attack primitive; cards remain immutable.\n\nAuthority: `docs/IRON_PIT_RULES_CONTRACT.md` §25.2.\n\n## Buffs, debuffs, and match lifecycle

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

- **Flexible Attack/Multiattack choices follow the current row deterministically.** See `docs/IRON_PIT_RULES_CONTRACT.md` §10 and `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md` Arena movement policy; fixed printed slots remain fixed.

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

## Parked blockers

Standing instruction: park, record, continue. Revisit this list after the rest of the current family is finished. Folded from the short-lived `docs/PARKED_BLOCKERS.md` working list after #602/#603/#604.

**2014 poison family (this lane).** Extra poison damage, Poisoned on a failed Con save, repeat-save timing, and half-on-success save-damage already compile through the shared on-hit save / `FailedSaveTimedEffect` / typed-damage primitives. Breath weapons stay out of this family. Remaining poison-named cards are parked because a different family still blocks READY:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Assassin | leftover trait | `source:trait` | Shortsword/crossbow poison save-damage already compiles. Assassinate / Evasion / Sneak Attack remain. | Leftover-trait lane for those three traits |
| Basilisk | leftover trait | `source:trait` | Bite poison damage already compiles. Petrifying Gaze remains. | Gaze / petrify machine, shared with Cockatrice / Gorgon |
| Phase Spider | leftover trait | `source:trait` | Bite poison save-damage already compiles. Ethereal Jaunt remains. | Ethereal / jaunt policy |
| Ettercap; Giant Spider | web / recharge | `attack:complex`, `attack:damage-type`, `mechanic:recharge` | Bite poison already compiles. Web is a breakable restraint plus recharge. | Shared web / breakable-restraint primitive |
| Otyugh | incomplete slam | `attack:incomplete`, `source:extra-action`, `source:trait` | Bite Poisoned save already compiles. Tentacle Slam and Limited Telepathy remain. | Finish Tentacle Slam, then leftover trait |
| Giant Toad; Purple Worm | swallow | `mechanic:swallow` | Poison riders compile or are incidental. Swallow/attach is another lane. | Swallow / attach / pull owner |
| Quasit | combined save | `attack:complex` plus Shapechanger / Scare | Same Con save wants fail-only poison damage **and** Poisoned. Still blocked after a bind. | Widen on-hit save to compose save-damage + save-condition; still need extra-action / trait |
| Homunculus; Sprite; Pseudodragon; Drow | fail-by-5 sleep poison | `failure_margin_escalation` plus Unconscious / `wake-sleeper` | Same missing machine as Sleep Breath. Each card also has another leftover. | Extend FailedSaveTimedEffect with fail-margin + generic wake-sleeper Action |
| Drider; Deep Gnome; Guardian Naga; Spirit Naga; and other poison casters | spellcasting | `mechanic:spellcasting` plus leftover trait | Poison riders compile where printed on the weapon. Innate/slot spellcasting remains. | Spellcasting family (highest-level / damage-first) |

**2014 recharge-breath leftovers (from #603).** Do not invent these in a poison or defense lane:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Brass wyrmling / young / adult / ancient | Sleep Breath | Failed-save Unconscious + `wake-sleeper` | No wake-sleeper Action exists. | Same FailedSaveTimedEffect + wake-sleeper machine as the sleep-poison cards |
| Gorgon | Petrifying Breath | `repeat_save_failure_condition_id: petrified` | Same petrify escalation as Cockatrice. | Shared petrify machine; do not invent here |
| Adult / ancient metallic dragons | Change Shape | Extra Action that replaces the combatant | Slowing Breath and Weakening Breath now compile. Form-replace stays parked. | Polymorph / form-replace policy |
| Gibbering Mouther | Blinding Spittle | Recharge + Blinded already compile | Leftover multiattack / extra-action / trait. | Multiattack-complex lane |

**2014 swallow / attach / pull (from #604).** Do not fake these as Grappled. Another agent owns this family:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Giant Frog; Giant Toad; Purple Worm; Remorhaz; Behir; Kraken; Tarrasque | swallow | Swallowed state | Blinded + Restrained + total cover + start-turn acid + death/regurgitate exit. | New swallow machine |
| Stirge | removed from Iron Pit roster | Product decision | Attachment/Blood Drain is not worth a dedicated subsystem for the automated arena. Keep the source record for audit provenance but never compile it into the runnable roster. | None; intentionally excluded |
| Roper | Reel / pull | Tendril attach + pull | Forced-movement pull; only push exists. | Pull primitive |
| Gelatinous Cube; Shambling Mound | Engulf | Swallow-shaped plus form extras | Same swallow machine, then extras. | Swallow machine first |
| Blink Dog | Teleport + extra attack | Recharge Teleport also grants a Bite | `TeleportAction` has no extra-attack rider. In-place teleport (10.1) plus a parameterized extra-attack grant. Do not drop the Bite. | Extra-attack grant on teleport |

**2014 legendary / X/Day leftovers.** Do not invent these here, and do not skip Cast a Spell:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Dretch | Fetid Cloud (1/Day) | Poisoned plus action/bonus exclusive and no reactions | Existing Poisoned does not include Slow-like action economy | Parameterized poisoned rider or compose Slow + Poisoned |
| Knight | Leadership (rest recharge) | Ally d4 on attacks/saves for 1 minute | No shared Leadership/bless-die grant for monsters | Reuse Bless/Bardic Inspiration die if one exists, else new ally d4 aura |
| Aboleth | Psychic Drain legendary | Unstructured legendary drain | Attack/Detect already compile | Legendary save/heal-drain option |
| Androsphinx / Gynosphinx | Cast a Spell legendary | Spellcasting lane | Teleport is pit-banned; Claw Attack compiles | Other agent's spellcasting bind; do not skip Cast a Spell |
| Vampire / Tarrasque | Legendary Move | Move up to speed on another turn, sometimes without OA | No `move` legendary kind | Legendary movement option |
| Solar / Lich / Mummy Lord / Kraken | Remaining legendary menus | Mixed save/gaze/spell/swallow options | Not a single reuse | Bind each compiled option; park the rest |

2024 counterparts after the 2014 octopus unlock stay blocked on their own source. 2024 Giant Octopus Tentacles still need Grappled+Restrained, but Ink Cloud is a 1/Day underwater damage-triggered reaction plus Swim movement. 2024 Octopus Tentacles are damage-only (no grapple) and its Ink Cloud is a different 1/Day underwater reaction. Do not copy 2014 Ink Cloud absence into those 2024 reaction machines.

2024 Death Dog and Ettin stay independently blocked after the 2014 Two Heads bind. 2024 Death Dog Bite is a multi-step disease rider, not Two-Headed. 2024 Ettin Battleaxe knocks Prone and Morningstar imposes next-attack Disadvantage; it has no Two Heads trait. Do not copy 2014 Two Heads grants onto those 2024 actions.

2024 Treant stays independently blocked (`dynamic-combatant-lifecycle` / limited-use). Do not copy the 2014 Animate Trees arena-unavailable extra into that 2024 lifecycle machine. There is no 2024 Nothic counterpart in SRD 5.2.1.

Conditional turning-save buffs use the shared conditional Advantage machinery
(architecture: Universal friendly auras / Saving-throw auras; rules contract §9).
The matched 2014 family is Turning Defiance (Ghast, self and ghouls within 30 ft)
and Turn Resistance (Lich, self). Both initial and repeat turning saves preserve
semantic context. Neither 2024 counterpart prints this trait; no edition backport.

Chris's Pit range instruction: a 30-foot turning-save aura covers the whole Pit.
Preserve its printed radius as source metadata and declare `covers_arena` on the
shared aura payload; all eligible recipients in the encounter qualify regardless
of grid separation. This is the explicit arena override in rules contract §9.
