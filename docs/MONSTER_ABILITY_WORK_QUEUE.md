# D20 Iron Pit — single operational monster ability queue (2014 first)

## Shared on-hit single-save damage + timed condition — Quasit poison family

- **Verified source:** 2014 Quasit Claws (Bite in Beast Form): melee +4, 1d4+3 Piercing; one DC 10 Constitution saving throw after hit. Failed save applies **both** 2d4 Poison damage and Poisoned for ten rounds, with end-of-target-turn repeat saves; success negates both. The pinned typed row already contains these parameters.
- **Engine status:** Universal primitive complete. One shared save roll; failure applies ordered typed damage + timed condition via existing lifecycles; success applies neither. No second save, no unconditional damage, no name dispatch. Python oracle + browser sharedSave path proven.
- **Permanent tests:** `backend/tests/test_2014_composite_save_runtime.py` locks fail-applies-both and success-applies-neither, with dice-call count proving single save. Source contract and compilation tests retained.
- **Remaining independent Quasit obligations:** Scare, Invisible ends on Scare, Shapechanger source classification from PR #1138, and generated artifacts. Do not mark it battle-ready before full Python/browser tests and webpage fight. Admission unchanged (already source-admitted).

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

## End-turn recurring typed damage — source-data blocker recorded 2026-10-29

- The mandatory semantic scan covers all 327 immutable cards and finds one applicable card: Magmin Touch.
- The card supplies hit application, 1d6 Fire, target-turn-end timing, and an Action exit. It does not supply the grid range for a different creature taking that douse Action; Iron Pit does not copy the 5-foot Wake Sleeper range or invent another value.
- Generator-owned `docs/generated/END_TURN_RECURRING_DAMAGE_BINDINGS_2014.json`: 327 scanned; one applicable; zero Python wired; zero browser wired; one remaining; one explicit missing-data exception.
- PR #1096's Python-only synthetic lifecycle is not integration evidence and must not merge without resolving this source gap, binding Python/browser together, and regenerating this report. Production remains locked.

## Sleep spell semantic family — source-data blocker recorded 2026-10-28

- The mandatory semantic scan covers all 327 immutable 2014 monster cards and finds four applicable cards: Dust Mephit, Night Hag, Oni, and Spirit Naga.
- The cards declare Sleep access and their per-day or prepared-spell access, but omit the spell's effect payload: range, area, hit-point-pool dice, duration, damage/wake exits, and creature/condition exclusions. Those values are not inferred from monster or spell names.
- The existing shared Python/browser Unconscious lifecycle, damage exit, and explicit `wake-sleeper` Action are reusable evidence from the certified Brass Dragon Sleep Breath family, but they are not a substitute for the missing spell payload or a complete Sleep cast action.
- Generator-owned `docs/generated/SLEEP_BINDINGS_2014.json`: 327 scanned; 4 applicable; 0 Python wired; 0 browser wired; 4 remaining; 4 explicit missing-data exceptions. Ingest a pinned 2014 spell source before binding all four cards together.
- No monster admission, runtime mechanic, or finished fight is claimed. Production remains locked.


## Staged disease semantic family — IN PR #1041, not merged

- Source: 2014 Tentacle attack's hit applies ordinary Bludgeoning damage, then the victim makes its printed DC 14 Constitution save. Failure attaches a fight-local latent disease; the printed one-minute delay is exactly 10 target turns. An initial successful save does not infect.
- On activation, healing is blocked in the standard no-water Pit and removal requires *heal* or disease-curing magic of 6th level or higher. During latency, ordinary disease-curing magic is sufficient. Disease reset and timed-effect transitions use the shared Python/browser lifecycle; no monster identity dispatch.
- The distinct out-of-water 1d12 Acid / 10-minute / moisture-suppression rider is source-verified, immutable, and explicitly arena-neutral. It neither enters the fight timer nor creates a second active rider; changed or unknown printed text fails source proof.
- Generator-owned `docs/generated/STAGED_DISEASE_BINDINGS_2014.json`: 327 scanned; one applicable, one Python wired, one browser wired, zero remaining, zero exceptions; one preserved arena-neutral periodic source component. This is **mechanic coverage**, not a completed monster or successful webpage fight.
- The generated Aboleth blocker row still lists unrelated extra Action and Legendary Action gaps. PR #1041 also requires reconciliation with overlapping shared files in #1038 and green **exact-final-head** CI. Production stays locked.



## Harpy subsequent-turn source maintenance — IN PR #991

- Owner: Codex on `feat/2014-source-maintenance-lifecycle-20261021`. This scope is independent of roster-wide damage defenses in #989 and Multiattack inventory in #990.
- Immutable card schema: `source_maintenance_action_cost` on a failed-save timed effect. Fight-local primary state: `source_turn_count_at_application`; secondary grouped conditions own no maintenance lifecycle. The source's first application turn is free, and every later source turn (including a same-round extra turn) requires the printed cost.
- Shared Python/browser policy explicitly continues at most one due group, preferring the group affecting the most opponents; all other due groups end. Voluntary stop is immediate and free. An unavailable Bonus Action ends the source/effect group on every target without granting the success-only source immunity. Source and card names remain log-only.
- PR #991 adds paired action-economy integration, sparse browser export, source-turn checkpointing, meaningful end/continue events and renamed-card regressions. At the time of PR #991, production modules remained within the then-current 150-line limit; the current combat runtime ceiling is 200 lines (see docs/CODE_SIZE_POLICY.md). Generated blocker/inventory artifacts are unchanged because Harpy is not source-bound or admitted in this foundation.
- Before merge: require exact-final-head source/Python, browser, Hero, generated-sync and applicable paired-roster checks, then recheck current main and active file ownership. Netlify production stays locked.
- After certified merge: bind the complete 2014 Luring Song source card using the grouped save/control, compelled approach, damage repeat save, damaging-terrain repeat save and this maintenance lifecycle; then inspect the 2024 counterpart independently and complete actual webpage fights. Preserve **237/327 admitted, 90 blocked** and zero finished Harpy until those later steps pass.

## 2014 magical visual disguise / Sea Hag Illusory Appearance — source contract

- Source text is combat-relevant **indirectly**: a visual illusion obscures the true form required by *Horrific Appearance*. It must not be silently declared arena-neutral or treated as Advantage, Invisibility, AC, or a global Blinded condition.
- Exact 2014 card facts: use Action to disguise, owner Bonus Action to end, ends on death, physical contact exposes inconsistencies, and another creature may spend its Action for source-derived DC 16 Intelligence (Investigation) to discern a disguise. A successful check does **not** automatically reveal the underlying true form.
- **Approved 2026-10-20 tactic:** enter with source-declared Illusory Appearance as the creature's **one** free precombat buff, then dismiss it on its own first initiative turn using the printed **Bonus Action** and continue its normal legal Action. PR #982 merged after exact-head checks on 2026-10-20. A creature earlier in initiative cannot retroactively trigger a turn-start save: only later eligible targets see the revealed true form on their turns. Use universal action economy (no free Bonus Action), RAW initiative totals, and source-scoped gaze aversion. A shared source-card-driven **optional Investigation Action** with an ordinary skill check is being implemented as a callable ability in the next PR, not an automatic AI turn: recognizing a disguise alone does not reveal the true form or improve combat math. Full death expiry, tactile detection, AI tactical choice and webpage-battle verification remain separate. Keep `source:extra-action` and **237/327 admitted, 90 blocked** pending full source admission.
- The visual-fear primitive from merged PR #980 respects `true_form_visible`; merged PR #981 provides observer-specific effective Truesight. PR #982 binds source-declared disguise values to **required** `VisualDisguiseAction` fields on the compiled monster/pregen cards (including physical inspection and detection DC) and exposes them in browser card export. Its first-turn opening/dismissal policy is explicitly an Iron Pit tactic, not source RAW. Investigation Action and full death expiry still need separate certification. Printed cards remain immutable; `CombatantState` owns temporary disguise state.


## Visual fear turn-start grammar — 2026-10-20, MERGED + CERTIFIED PR #980

- The source-proven 2014 Sea Hag Horrific Appearance can now compile as a **generic timed visual failed-save rule** rather than the old staged petrification mode: humanoid only, 30-ft source-derived range, DC 11 Wisdom, ten rounds, end-turn repeat saves disadvantaged when source visible, and per-source fight-local 24-hour immunity on success or effect ending.
- A source-neutral visual eligibility policy handles source sight (needed for petrifying gaze, not the hag's passive), source incapacitation, true-form visibility and the automatic initiative-based aversion exception. Card labels are display-only.
- The shared Python and browser turn-start execution bridges merged in PR #980 after all five exact-head gates passed. **Illusory Appearance remains independently blocked**, so the Sea Hag is not playable/admitted. Never count this code as a completed monster without all source Actions and a successful real webpage fight.
- The previous attack-roll-only gaze penalty merged in PR #979 with exact-head CI success. No Netlify release.

## Gaze avoidance attack disadvantage — 2026-10-20, MERGED + CERTIFIED PR #979

- Source-neutral aversion windows already exist for Basilisk/Medusa visual turn-start rules and future Sea Hag visual fear. Browser turn-start records source identity; no creature-name dispatch.
- Work scope: actually include source-specific aversion in Python/browser shared weapon attack roll Disadvantage, retaining the ordinary Blinded condition only when independently applied, not automatically. Each target/source has independent expiration. No invented global Blinded. Exact-head CI success. Production locked.
