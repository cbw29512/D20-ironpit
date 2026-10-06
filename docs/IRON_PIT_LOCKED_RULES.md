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

## INACTIVE in the Pit

Any printed ability that does **not** change combat math (damage, to-hit, AC, saves, HP, conditions, action economy) stays printed on the card, is marked **INACTIVE** in the Pit, and must **not** block the monster. Data remains on the monster for later use. Only park an ability when it actually changes combat math and lacks a primitive.

Confirmed INACTIVE families (keep printed names; do not strip the card):

- **Form / disguise.** Change Shape, Shapechanger, Illusory Appearance (hag, Oni, Lamia, Couatl, metallic dragons, Mimic). The creature fights in its natural / true form. Object-form-only Mimic traits are inactive while true form is locked.
- **Telepathy, senses, communication, insight.** Limited Telepathy, Telepathic Bond, Probing Telepathy, Read Thoughts, Divine Awareness, Inscrutable, Shielded Mind, Sense Magic, Speak with Beasts/Plants, Ethereal Sight, Blind Senses, Echolocation, Keen Senses.
- **Environment / appearance / post-fight flavor.** False Appearance, Rejuvenation, Siege Monster, Incorporeal Movement, Web Sense, Web Walker, Mimicry, Antimagic Susceptibility, Immutable Form, Amphibious, Spider Climb, Water Breathing, Hold Breath, Elemental Demise, Create Spawn and other after-fight curses (spawn / thrall / lycanthropy transmission).
- **Lair Actions and Regional Effects.** The standard Pit has no lair and no regional overlay. Keep the printed data; do not block.
- **Utility innate spells.** Detect Magic, Disguise Self, Speak with Dead, Tongues, and other printed utility that cannot change a fight.
- **Summon actions.** Summoning is pit-banned. Keep the RAW option in source/audit data; Arena AI never selects it and it does not block.

Do **not** mark these INACTIVE: Gnome Cunning (save Advantage), Grappler, Horrific Appearance, Invisible Passage, Etherealness / Ethereal Jaunt, Invisibility, Scare, Tree Stride, Evasion, and any other leftover that changes combat math.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §1, §10, §20, §25.

## Opening burst

Surprise / charge openers (Charge, Pounce, Trampling Charge, Running Leap, and later Assassinate / Ambusher / Surprise Attack) reuse the existing `opening_burst_available` hook: if the creature **wins initiative** over every enemy it uses the opener on its first turn; if it loses or ties, it fights normally without it. No monster-name dispatch. Charge / Pounce / Trampling Charge already bind through `CombatTrait.CHARGE`. Assassinate / Ambusher / Surprise Attack remain parked until their first-turn Advantage / extra damage / auto-crit riders bind to that same gate — they are combat math, not INACTIVE.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §7.1, §8; `backend/app/combat/opening_burst.py`.

## Legendary Resistance

**ACTIVE.** One shared primitive (`FailedSaveSuccessOverride`): whenever the creature fails a saving throw and has uses left, it automatically spends one use and succeeds. No decision logic. Uses = the printed count (non-lair number when a lair alternate is printed). Per match; resources reset at match end. The log shows the printed name `Legendary Resistance (n/Day)` and remaining uses. Bind every 2014 stat block that prints it, then the matching 2024 blocks.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §19.

## Charm / Possession / Dominate

**ACTIVE.** Vampire Charm, Ghost Possession, Dominate Person / Monster, and similar printed control reuse one shared `FailedSaveTimedEffect`: the affected creature is **incapacitated** (stands and does nothing) until it is hit / takes damage, succeeds on a save, or the printed duration ends. Pit rule overriding printed text: every charmed / possessed / dominated creature gets a repeat save vs the printed DC at the end of each of its turns, even if the stat block gives none. No infinite charm-locks. Caster AI still prefers highest-level / simple damage; these actions are used only when that policy already picks them. No monster-name dispatch.

Authority: `docs/IRON_PIT_RULES_CONTRACT.md` §8, §16, §22.

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

## Parked blockers

Standing instruction: park, record, continue. Revisit this list after the rest of the current family is finished. Folded from the short-lived `docs/PARKED_BLOCKERS.md` working list after #602/#603/#604.

**2014 poison family (this lane).** Extra poison damage, Poisoned on a failed Con save, repeat-save timing, and half-on-success save-damage already compile through the shared on-hit save / `FailedSaveTimedEffect` / typed-damage primitives. Breath weapons stay out of this family. Remaining poison-named cards are parked because a different family still blocks READY:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Assassin | leftover trait | `source:trait` | Shortsword/crossbow poison and Sneak Attack already compile. Assassinate is an opening-burst rider (Advantage / auto-crit), not INACTIVE. Evasion remains. | Bind Assassinate to `opening_burst_available`; leftover-trait Evasion |
| Basilisk | leftover trait | `source:trait` | Bite poison damage already compiles. Petrifying Gaze remains. | Gaze / petrify machine, shared with Cockatrice / Gorgon |
| Death Dog | leftover trait | `source:trait` | Bite Poisoned save already compiles. Two-Headed remains. | Leftover-trait bind for Two-Headed |
| Phase Spider | leftover trait | `source:trait` | Bite poison save-damage already compiles. Ethereal Jaunt remains. | Ethereal / jaunt policy |
| Ettercap; Giant Spider | web / recharge | `attack:complex`, `attack:damage-type`, `mechanic:recharge` | Bite poison already compiles. Web is a breakable restraint plus recharge. | Shared web / breakable-restraint primitive |
| Otyugh | incomplete slam | `attack:incomplete`, `source:extra-action` | Bite Poisoned save already compiles. Limited Telepathy is INACTIVE. Tentacle Slam remains. | Finish Tentacle Slam |
| Giant Toad; Purple Worm | swallow | `mechanic:swallow` | Poison riders compile or are incidental. Swallow/attach is another lane. | Swallow / attach / pull owner |
| Iron Golem | breath + multiattack | `multiattack:choice-or-binding`, `source:trait` | Poison Breath is out of this family by standing instruction. | Recharge-breath or multiattack-choice lane |
| Quasit | combined save | `attack:complex` plus Scare | Shapechanger is INACTIVE (true form). Same Con save wants fail-only poison damage **and** Poisoned. Scare remains. | Widen on-hit save to compose save-damage + save-condition; leftover Scare |
| Homunculus; Sprite; Pseudodragon; Drow | fail-by-5 sleep poison | `failure_margin_escalation` plus Unconscious / `wake-sleeper` | Same missing machine as Sleep Breath. Each card also has another leftover. | Extend FailedSaveTimedEffect with fail-margin + generic wake-sleeper Action |
| Drider; Deep Gnome; Guardian Naga; Spirit Naga; and other poison casters | spellcasting | `mechanic:spellcasting` plus leftover trait | Poison riders compile where printed on the weapon. Innate/slot spellcasting remains. | Spellcasting family (highest-level / damage-first) |

**2014 recharge-breath leftovers (from #603).** Do not invent these in a poison or defense lane:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Brass wyrmling / young / adult / ancient | Sleep Breath | Failed-save Unconscious + `wake-sleeper` | No wake-sleeper Action exists. | Same FailedSaveTimedEffect + wake-sleeper machine as the sleep-poison cards |
| Copper dragons; Stone Golem | Slowing Breath / Slow | `slowed` is not a universal condition | Speed, reactions, action/bonus exclusive, max attacks. | Parameterized slow rider, not a new condition name |
| Gold dragons | Weakening Breath | `weakened-strength` is not a universal condition | Strength-check / attack Disadvantage needs a timed grant. | Existing Disadvantage grant if it can be timed and repeat-saved |
| Gorgon | Petrifying Breath | `repeat_save_failure_condition_id: petrified` | Same petrify escalation as Cockatrice. | Shared petrify machine; do not invent here |
| Adult / ancient metallic dragons | leftover combat | legendary / breath / multiattack | Change Shape is INACTIVE (natural form). Remaining blockers are combat math. | Legendary-action / breath / multiattack lanes |
| Gibbering Mouther | Blinding Spittle | Recharge + Blinded already compile | Leftover multiattack / extra-action / trait. | Multiattack-complex lane |

**2014 swallow / attach / pull (from #604).** Do not fake these as Grappled. Another agent owns this family:

| Card / item | Family | Blocker | Why parked | Needed to unpark |
|---|---|---|---|---|
| Giant Frog; Giant Toad; Purple Worm; Remorhaz; Behir; Kraken; Tarrasque | swallow | Swallowed state | Blinded + Restrained + total cover + start-turn acid + death/regurgitate exit. | New swallow machine |
| Stirge | attach / Blood Drain | Ongoing attach | Source-attack lock, detach movement, HP-loss end. | New attach rider, not a Grapple rename |
| Roper | Reel / pull | Tendril attach + pull | Forced-movement pull; only push exists. | Pull primitive |
| Gelatinous Cube; Shambling Mound | Engulf | Swallow-shaped plus form extras | Same swallow machine, then extras. | Swallow machine first |
| Blink Dog | Teleport + extra attack | Recharge Teleport also grants a Bite | `TeleportAction` has no extra-attack rider. In-place teleport (10.1) plus a parameterized extra-attack grant. Do not drop the Bite. | Extra-attack grant on teleport |

2024 counterparts after the 2014 octopus unlock stay blocked on their own source. 2024 Giant Octopus Tentacles still need Grappled+Restrained, but Ink Cloud is a 1/Day underwater damage-triggered reaction plus Swim movement. 2024 Octopus Tentacles are damage-only (no grapple) and its Ink Cloud is a different 1/Day underwater reaction. Do not copy 2014 Ink Cloud absence into those 2024 reaction machines.
