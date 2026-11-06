# D20 Iron Pit — single operational monster ability queue (2014 first)

## Magmin Touch douse range — parked single-blocker 2026-11-06

- **Selected highest-yield remaining source blocker not in open implementation PR:** Magmin `attack:incomplete` (single-blocker opportunity; Frog arena:neutral is intentional exclusion).
- **Source-verified:** printed Touch ignition applies nonstacking Burning (1d6 Fire at target turn end). Another creature may spend an Action to douse, but source specifies no grid distance/range.
- **Parked:** do not infer range, invent free extinguish, or clear blocker. Remains blocked until source range clarified or universal primitive for unspecified-range Action is approved. No name dispatch, no fidelity weaken. Python/browser parity N/A (parked). Tests/regeneration deferred until unpark.
- **Next blocker after this:** highest remaining `source:trait` family (e.g. spellcasting or Fire Form) once this is resolved or clarified.

## Equipment corrosion/destruction universally omitted — 2026-11-05 user decision

- **Active family:** 2014 equipment-only effects, branch `feat/2014-equipment-corrosion-arena-neutral-family`. Full pinned 327-card source scan identifies exactly three relevant printed sources: Black Pudding, Gray Ooze and Rust Monster. No equipment wear, breakage, destruction, corrosion penalties, or material/durability inventory in Python or browser fights. Same product policy applies to 2024 after separate source proof.
- **Gray Ooze:** its pinned `Corrode Metal` (incoming nonmagical metal weapon/ammunition, plus unheaded object-eating continuation) is strictly source-proven and classified arena-neutral. Pseudopod's printed +3/5-ft **1d6+1 Bludgeoning plus 2d6 Acid** remains a normal live hit; only the full source-proven armor item AC reduction is neutral. No weapon/armor metadata or corrosion-specific combat resolver is introduced. Synthetic source changes and extra combat riders fail closed.
- **Rust Monster:** `Rust Metal` and `Antennae` are both source-proven equipment-only and arena-neutral, preserving printed text. Its Bite Piercing damage remains active. The old parked Antennae question and Gray Ooze fight-only corrosion approval #784 are **superseded** by the user's new policy. Black Pudding's mixed typed hit and Corrosive Form Acid retaliation remain active.
- **Generated branch accounting (provisional):** generator-owned blocker report now classifies **264/327 source-admitted, 63 blocked** (from 263/327 and 64 blocked); `source:trait` declines 52→51 and `attack:incomplete` 15→14. Gray Ooze is absent from generated outstanding blockers, but it is **not** merged or webpage-fight certified yet. The first browser CI ran against pre-sync artifacts and lacked Gray Ooze; exact-head retest is required on the synchronized branch.
- **Certification:** do not cross Gray Ooze off as fully finished until exact-head CI, generated artifact sync, merge, and actual webpage-fight evidence. Source-admitted classification, automated CI and webpage fight status are reported separately; production Netlify stays locked. The generated blocker report is never hand-edited.


## Source-semantic Read Thoughts classification — 2014 family

- **Full source scan:** all 327 immutable cards scanned by the Action's semantic outcome rather than card or Action name. Exactly one clause reads surface thoughts and grants only Wisdom (Insight) and Charisma (Deception, Intimidation, Persuasion) check Advantage: Doppelganger.
- **Universal source proof:** one identity-independent full-clause validator classifies the Action as nonactionable in standard Pit combat because those social/information checks have no combat outcome. Renaming the card and Action retains classification; changing range, barrier values, or adding attack Advantage fails closed. The printed Action remains immutable and visible.
- **Coverage:** `docs/generated/READ_THOUGHTS_CLASSIFICATION_2014.json` records 327 scanned, 1 applicable, 1 source-classified, 0 remaining and 0 exceptions. This clears Doppelganger's last generated blocker and advances source admission from 262/327 to 263/327. The classification adds no fight-local runtime mechanic; a separate browser regression verifies the newly admitted immutable card and deterministic 1v1/6v6 fights with its already-supported printed combat kit. No real-webpage certification is claimed.

## Source-semantic no-action arena-neutral classification — 2014 family

- **Full source scan:** all 327 immutable cards scanned. Exactly one card has no attacks, Actions, Reactions, Legendary Actions, spellcasting or other callable combat surface and contains only the complete printed Amphibious plus Standing Leap payload: Frog.
- **Classification:** the shared source classifier now proves the complete breathing/jump-only clause instead of dispatching on card ID or name. Renaming preserves the result; changing printed jump distance or adding any callable combat surface fails closed.
- **Accounting:** Frog remains intentionally arena-neutral and excluded from runnable source admission. This removes an identity-based classification branch but does not claim a newly playable monster, automated fight, or webpage certification. Current generated roster remains 262/327 admitted and 65 blocked until the next combat-active family lands.

## Source-semantic Shapechanger classification — 2014 family

- **Full source scan:** all 327 immutable cards scanned; 11 contain a printed Shapechanger clause. Ten complete clauses are arena-inert under locked Pit rules because the optional Action changes only appearance, size, AC or listed movement while preserving all other statistics. Vampire is the single explicit exception: its mist form changes actions, saves, space passage and damage immunity and still requires a combat-active form runtime.
- **Universal source proof:** one identity-independent full-clause validator replaces the prior Imp, Quasit and lycanthrope card-ID branches and also binds Doppelganger, Mimic and Succubus/Incubus. Renamed cards retain classification; any changed printed value fails closed. No browser runtime is fabricated for an arena-inert optional Action.
- **Coverage:** `docs/generated/SHAPECHANGER_CLASSIFICATION_2014.json` records 327 scanned, 11 applicable, 10 classified, 1 remaining and 1 explicit exception. The generated unresolved Shapechanger demand falls from four cards to Vampire alone and `source:trait` blockers fall from 54 to 53. Unrelated Actions, attacks and traits remain blocked; admission stays 262/327 and no automated fight or webpage certification is inferred.

## Form-qualified Charge / Pounce source headings — 2014 family

- **Full source scan:** all 327 immutable cards scanned semantically; two applicable declarations: Wereboar `Charge (Boar or Hybrid Form Only)` and Weretiger `Pounce (Tiger or Hybrid Form Only)`.
- **Universal binding:** both source headings compile through the existing declarative Charge/Pounce profile and shared Python/browser runtime. Printed movement, triggering attack, save DC/ability, bonus damage, Prone rider, follow-up attack and Bonus Action cost are source-proved. Monster/card identity is not a runtime switch; renamed-card proof retains behavior and source mutations fail closed.
- **Coverage:** `docs/generated/FORM_QUALIFIED_CHARGE_BINDINGS_2014.json` records 327 scanned, 2 applicable, 2 Python wired, 2 browser wired, 0 remaining and 0 exceptions. Wereboar remains covered; Weretiger becomes source-admitted and is covered by deterministic direct, 1v1 and 6v6 browser fights. Exact-head CI and merge remain required before merged certification; production stays locked.

## Shared on-hit single-save damage + timed condition — Quasit poison family

- **Verified source:** 2014 Quasit Claws (Bite in Beast Form): melee +4, 1d4+3 Piercing; one DC 10 Constitution saving throw after hit. Failed save applies **both** 2d4 Poison damage and Poisoned for ten rounds, with end-of-target-turn repeat saves; success negates both. The pinned typed row already contains these parameters.
- **Precise engine gap:** Current `SaveDamageEffectDefinition` and `SaveConditionEffectDefinition` are distinct alternatives; the 2014 source validators correctly reject the combined row. The next universal primitive must roll one save and atomically apply the ordered failed-save damage and timed condition, using existing typed damage and timed-condition lifecycle in Python/browser; never roll a second save or apply unconditional poison damage. This applies to other source-equivalent monsters and homebrew.
- **Regression:** `backend/tests/test_2014_quasit_composite_save_contract.py` locks the original source and fail-closed admission while wiring remains incomplete. This is blocker documentation/tests, **not** a completed combat resolver or monster admission.
- **Remaining independent Quasit obligations:** Scare, Invisible ends on Scare, Shapechanger source classification from PR #1138, and generated artifacts. Do not mark it battle-ready before full Python/browser tests and webpage fight.

## Generic source-owned Invisible self-buff exits — 2014 family

- **Implementation branch:** `feat/2014-source-invisibility-expiry-family` (ACTIVE). Same existing Invisible/concentration buff in Python/browser; printed source decides attack exit and optional spell-cast exit. No monster-name runtime decision or new condition.
- **Full 327-card source scan:** two fully supported source clauses: Sprite (attack or spell cast) and Imp (attack only). Quasit (using Scare) and Will-o'-Wisp (using Consume Life) remain unbound pending an exact generic named-action exit primitive; their clauses must never be weakened to spell casting.
- **Proof:** positive/negative source-mutating cases, renamed source, actual compiled Imp state and browser non-spell expiry regression. Generator-owned blocker and inventory artifacts synchronized on branch: Imp's `source:extra-action` is cleared; independent `source:trait` Shapechanger remains. **254/327** source-admitted and **73** blocked. Full exact-head CI still required; production locked.

## Source-only Etherealness movement — 2014 cross-roster family

- **Scope:** All 327 pinned cards scanned. Three complete printed `Etherealness` actions (Ghost, Night Hag, Succubus/Incubus) are verified as exclusively entering or leaving the Ethereal Plane, with source-specific visibility/heartstone restrictions. This is a general full-clause source proof, not monster-ID dispatch.
- **Locked Pit policy:** entering the Ethereal Plane is unavailable; the printed actions remain on immutable cards, but create no fight-local planar state, saves, damage, buffs or resources. If a future card adds an in-combat rider, the proof fails closed; no invented magical effect.
- **Obligations cleared:** three extra-action source obligations, not three fully admitted monsters. Their other printed combat effects remain blocked and no admission increase is claimed. Do not alter generated reports manually. Pending CI/exact-head verification and production stays locked.

## Source-owned grapple target save — PR #1132 (2014)

- **Single universal mechanic:** the existing save Action now supports a declarative `requires_target_grappled_by_source` filter. The generic Python/browser save engines inspect fight-local grapple ownership, not the ability or monster name. Live held friends as well as foes are eligible only when `target_scope: all-other-creatures`; source/other-grappler/unheld targets are rejected.
- **327 pinned source cards scanned:** one complete source-matching Slam, Otyugh Tentacle Slam. Its two held creatures each independently make the printed DC 14 Constitution save. A failed save takes 2d6+3 Bludgeoning and Stunned until the source's next turn end; success takes half damage and no Stunned. The two-target cap and 10-ft grapple reach are sourced from the bound Tentacle attack rather than invented. One Action and one common damage roll feed the existing save resolver. Renames do not alter engine dispatch; unfamiliar source clauses fail closed.
- **Committed evidence:** source classification and adapter, Python/browser serialization and reverse-template capability, immutable source mutation and rename tests, real Python and browser two-target combat regressions. Generated 2014 source classifier on branch: **254/327 admitted; 73 blocked**. Otyugh is source-admitted, **not yet declared finished** until exact-head required CI and an actual webpage fight. Production publishing remains locked.
- **Collisions:** existing #1122 Vrock area-control compiler and #1130 Stirge attachment serializer are separate PRs; reconcile changed files before either later merge. Otyugh's 24-hour Bite disease progression is arena-outside the fight duration; ordinary Poisoned/remove-condition behavior is shared, not a separate Otyugh resolver.

## Shared simultaneous grapple capacity — PR #1131 (2014)

- **State:** Source wiring implemented, exact-head CI and browser webpage fights pending; 2014 main baseline remains 253/327 source-admitted.
- **327 pinned 2014 source cards audited:** five matching full printed attack clauses: Giant Crab (2 Claws), Giant Scorpion (2 Claws), Glabrezu (2 Pincers), Kraken (10 Tentacles), Otyugh (2 Tentacles). Strict full-clause validation reads the printed attack/save DC, range, base and optional extra typed damage, size, Restrained rider and capacity; changed or unfamiliar source clauses stay blocked.
- **One universal capacity rule:** existing Grapple and Restrained state count distinct live targets held by the source; a source-owned `max_active_grapples` limit allows another grapple only below capacity (or on an already held target). Full-capacity hits still resolve their normal weapon damage. Both Python and browser use the same semantics, and the browser serializer carries the optional source parameter. Names never dispatch combat logic.
- **Generated classifier after source adapter:** Otyugh no longer has `attack:incomplete` and is now blocked only on `source:extra-action` (Tentacle Slam). Kraken's incomplete Tentacle is repaired but its independent legendary and other source abilities remain. **Neither is source-admitted by this PR.** Do not hand-edit generated artifacts or count the capability as a certified complete monster.
- **Next separate family:** Tentacle Slam is a DC 14 CON save against each creature grappled by the source, printed 2d6+3 Bludgeoning (half on success), and Stunned through end of source next turn on failed save. Bind that as a source-declared grapple-targeted multi-save Action rather than a named special resolver. Otyugh's printed 24-hour disease recurrence is arena-outside the maximum fight duration; verify its Poisoned/removal provenance separately.

## Surprise-opening attack modifiers — implementation 2026-10-29

- The mandatory source-semantic scan covers all 327 immutable cards and finds two applicable cards: Bugbear and Doppelganger. It does not route on monster or trait name.
- Both cards' printed Surprise Attack dice and damage type are bound to the existing first-round initiative-lead hit rider. Doppelganger's separate printed Ambusher clause now grants attack Advantage through the same fight-local opening window in Python and browser.
- Generator-owned `docs/generated/SURPRISE_OPENING_BINDINGS_2014.json`: 327 scanned; 2 applicable; 2 Python wired; 2 browser wired; zero remaining; zero exceptions.
- Bugbear remains source-admitted. Doppelganger's Ambusher and Surprise Attack obligations are cleared, while its independent Shapechanger Action/trait remains explicitly blocked; no admission is claimed. Production remains locked.

## Recharge save-for-half typed damage — implementation 2026-10-29

- The mandatory semantic scan covers all 327 immutable cards and finds 30 direct Recharge Actions whose complete printed outcome is typed damage on a failed save and half on success.
- All 30 are wired in Python and browser with source-declared save ability/DC, range/area, damage dice/type, half-damage outcome, Recharge threshold and one-use resource. Behir's previously missing Lightning Breath binding adds its exact 20-by-5-foot line, DC 16 Dexterity save, 12d10 Lightning damage and Recharge 5–6 without monster-name runtime dispatch.
- Generator-owned `docs/generated/RECHARGE_SAVE_HALF_DAMAGE_BINDINGS_2014.json`: 327 scanned; 30 applicable; 30 Python wired; 30 browser wired; zero remaining; zero exceptions.
- Behir's `mechanic:recharge` blocker is removed. The simple grapple-then-Swallow profile is now wired for Giant Frog and Giant Toad in Python and browser, raising source admission to 250/327. The 327-card semantic scan finds 8 applicable Swallow/Engulf cards: 2 wired and 6 explicitly blocked by missing structured parameters or distinct failed-save, regurgitation, or Engulf profiles. Behir's printed Swallow remains fail-closed under `source:extra-action`. Production remains locked.

## Magmin Touch — source-proven recurring fire, with one remaining source-data blocker

- **Merged mechanic (PR [#1173](https://github.com/cbw29512/D20-ironpit/pull/1173), merge `150e046ee3d02997be097fbb749d1ee69d9169b9`, five exact-head workflows successful):** all 327 immutable 2014 cards scanned; one source match, Magmin Touch. On a successful hit, a shared nonstacking Burning debuff applies 1d6 Fire at the **target's turn end**, through normal Python/browser typed defenses, HP and death handling. On misses no debuff is applied; later hits do not stack it. Source name is logged; card data is unchanged.
- **Keep only the outstanding `attack:incomplete` task active:** another creature may spend an Action to douse the fire, but the printed source specifies no grid distance. Do **not** infer a 5-foot range from Wake Sleeper, grant free extinguishing, remove the blocker, or call Magmin source-admitted.
- **Complete lighting-only source family:** a full 327-card scan finds two declarations: Magmin's **Ignited Illumination** and Will-o'-Wisp's **Variable Illumination**. Both exact printed Bonus Action/light-radius clauses match one shared strict source-body validator, including unheaded continuations; positive, renamed-card and hostile-source-mutation tests reject altered range, timing and added damage. Standard Pit lighting has no combat outcome. The generated classifier clears Magmin's lighting `source:trait` category but **retains Magmin Touch's `attack:incomplete` douse range**; it also removes only Will-o'-Wisp's Variable Illumination from the unbound-trait list, without clearing its independent Consume Life, Ephemeral or Invisibility blockers. Death Burst is already resolved separately.
- **Completion accounting:** remove the recurring-fire implementation item from the pending list **when #1173 is merged and verified**, preserve this douse-range blocker, and record the merged commit/PR here. Generator-owned coverage and blocker reports are authoritative, not hand-edited.
- PR #1096's Python-only synthetic lifecycle is not integration evidence and must not merge without resolving this source gap, binding Python/browser together, and regenerating this report. Production remains locked.

## Sleep spell semantic family — source-data blocker recorded 2026-10-28

- The mandatory semantic scan covers all 327 immutable 2014 monster cards and finds four applicable cards: Dust Mephit, Night Hag, Oni, and Spirit Naga.
- The cards declare Sleep access and their per-day or prepared-spell access, but omit the spell's effect payload: range, area, hit-point-pool dice, duration, d