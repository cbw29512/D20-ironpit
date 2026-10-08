# 2014 Iron Pit — one-by-one remaining monster fix worksheet

**Planning worksheet, not certification evidence.** Source snapshot: generated `docs/MONSTER_BLOCKERS_2014.md` on `main` at worksheet creation; 201 admitted / 327, **126 blocked**. This editable worksheet is separate from generated blockers and inventory. Reconcile it after each merge using the generators; never hand-edit generated outputs. Every line below is an **action hypothesis**, not a claim that exact RAW has been reviewed or that code exists. The current source, repository contracts, existing universal inventory, and focused Python/browser tests decide the actual implementation. Use 2014 source first; copy no printed stats from memory.

## Repeatable completion procedure

For each entry: (1) read exact 2014 printed trait/action and existing code; (2) compare all mechanics with `docs/UNIVERSAL_MECHANIC_INVENTORY.md` and pregen reuse; (3) bind full source parameters into universal schema, or park a genuine missing primitive; (4) cover Python and browser behavior and reset; (5) run focused checks once, regenerate source-owned artifacts with scripts, and submit exact-head CI; (6) merge only green; (7) update checkbox/status and choose next entry. `source:extra-action` alone does not mean summoning or arena exclusion. Treat all medical skill checks as arena-unavailable under locked Pit rules.

## Shared blocker fix recipes

- **`source:trait`:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **`source:extra-action`:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.
- **`mechanic:spellcasting`:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately.
- **`attack:incomplete`:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing.
- **`attack:complex`:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity.
- **`multiattack:complex`:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts.
- **`mechanic:recharge`:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge.
- **`mechanic:legendary`:** Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution.
- **`source:legendary`:** Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs.
- **`source:reaction`:** Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.
- **`mechanic:swallow`:** Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics.
- **`attack:range`:** Correct reach/range bands from printed source; verify legal attack selection and shared range penalties.
- **`mechanic:death-trigger`:** Use generic death/zero-HP event trigger to apply source-driven area/damage/condition consequences.
- **`attack:none`:** Check whether the creature has any legal combat attack; if no, preserve source and classify arena-neutral rather than fabricating one.
- **`attack:damage-type`:** Preserve each distinct printed typed damage component, including hit riders and defense interaction.
- **`arena:neutral`:** Preserve a truthful non-runnable classification; do not invent offensive capabilities.
- **`mechanic:limited-use`:** Bind printed uses, spending and recovery to existing generic resource model.
- **`mechanic:defense`:** Model printed defense as appropriate shared resistance/immunity/saving modifier, with source qualifiers.
- **`arena:removed`:** Check established Pit exclusion and retain explicit audit record; do not quietly count as certified.

## Individual monster queue (fewest blocker categories first)


### 001. Adult Bronze Dragon

- [ ] **FIX NOTE RECORDED — NOT IMPLEMENTED/CERTIFIED.**
- **Recorded blockers:** `source:extra-action` only. Bronze Repulsion Breath is already covered by the existing shared save + push implementation (see `docs/BRONZE_REPULSION_AUDIT.md`).
- **Identified remaining action:** Change Shape; the Bronze Repulsion audit explicitly names this as the independent extra-action blocker.
- **Fix plan:** Read the exact 2014 Change Shape source and compare against existing transformation/replacement-form and arena restrictions. If transformation is allowed and representable, bind it declaratively using the shared form/state primitive and preserve the original dragon's legal capabilities. If Pit policy excludes the action, document the existing rule and classifier consequence rather than invent a replacement. Verify attack choices, stats/HP/form return and browser/Python parity as applicable.
- **Avoid rework:** Do not touch Repulsion Breath or add a dragon-specific transformation resolver. Next classification decision is the permitted scope of Change Shape under the locked Pit rules.

### 002. Adult Gold Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 003. Adult Silver Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 004. Ancient Brass Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 005. Ancient Bronze Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 006. Ancient Copper Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 007. Ancient Gold Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 008. Ancient Silver Dragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 009. Assassin

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Assassinate; Evasion; Sneak Attack
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Assassinate/Sneak Attack/Evasion: reuse rogue pregen combat primitives where semantics match.

### 010. Azer

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Heated Body
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Heated Body: use existing typed retaliatory fire damage and add/reuse generic contact trigger after checking hit-versus-touch distinction.

### 011. Basilisk

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Petrifying Gaze
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Petrifying Gaze: source-triggered sight/save and staged Restrained/Petrified timing; check generic gaze predicate.

### 012. Blink Dog

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge.
- **Arena ruling queued:** Teleport (Recharge 4–6) remains on the source/card but is never executed in Iron Pit; only the normal Bite is available. Recharge attached solely to the excluded action must not block certification after shared classification, regeneration and gates. Not yet merged/certified.

### 013. Bulette

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.
- **Deadly Leap queued / approved arena semantics:** Landing occupies a 10×10-foot (2×2 square) AoE; every enemy overlapping a landing square resolves its own DC 16 Strength-or-Dexterity (better available) save. On failure, roll 3d6+4 bludgeoning plus 3d6+4 slashing, apply typed resistance/immunity/vulnerability independently, and inflict shared Prone. On success, half damage per component after the save, apply defenses, no Prone; 5-ft push deliberately omitted in Iron Pit. A legal 15-ft jump remains required. AI prioritizes leap on opening turn when eligible; ability remains available subsequently. **Queued, not implemented/certified.**

### 014. Dretch

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.
- **Fetid Cloud user-approved fix queued:** Treat as a source-owned 1/day area poison: shared Poisoned + separate action/bonus exclusivity and reaction suppression, delivered by existing saving throw and timed-effect primitives. Do not change the global Poisoned effect; retain exact printed DC/radius/duration/immunity terms for implementation. Source/card retains the printed name. **Not coded or certified.**

### 015. Frog

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `arena:neutral`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Preserve a truthful non-runnable classification; do not invent offensive capabilities.
- **Known directed work:** No printed meaningful arena attack: preserve arena-neutral status.

### 016. Grimlock

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Blind Senses
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **RAW range locked / queued:** Blindsight **30 feet**, not arena-wide (24×16 five-foot squares). Reuse shared Blindsight/sight and source Blinded immunity; no global Blinded disadvantage within perceivable range, no valid gaze eye contact with Basilisk/Medusa, normal limitations beyond 30 ft. Preserve printed Deafened/smell qualifier for future mechanics. **Specification only: not implemented or certified.**

### 017. Harpy

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.
- **Luring Song user decision / queued:** 300-ft range spans the entire current arena but retain hearing and creature-type eligibility. Failure of DC 11 Wisdom save composes existing Charmed and Incapacitated and moves the victim via existing pathfinding toward Harpy's 5-ft melee reach on its own turns, limited by normal movement (not teleport); retain printed follow-up saves, song continuation and 24-hour success immunity. **No implementation or certification yet.**

### 018. Invisible Stalker

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Invisibility; Faultless Tracker
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **User-approved arena policy (queued):** Faultless Tracker remains printed on source/card but has no effect in Iron Pit, no combat vision/targeting bonus. Invisibility uses existing universal system; Slam attacks are unaffected. Apply shared arena-inert trait classification and regenerate blockers; not yet implemented/certified.

### 019. Knight

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.
- **Leadership user decision / queued:** Activate via Action as a nonspell, short/long-rest recharge, 10-round Bless-style +1d4 to qualifying friendly attack rolls and saves within 30 ft and able to hear. No Concentration. **Iron Pit house simplification:** once activated, buff continues until duration expires or the Knight reaches 0 HP; printed Incapacitated-ending restriction is replaced by HP > 0. Reuse shared roll-bonus mechanics. **Not implemented/certified.**

### 020. Medusa

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:trait`.
- **Unbound printed traits:** Petrifying Gaze
- **Fix notes:** Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Petrifying Gaze: reuse timed save escalation to Petrified, but verify sight/gaze avoidance and source timing.
- **User decision, queued:** Same shared gaze mechanic and sight/avert policy as Basilisk. Medusa supplies **DC 14 Constitution, 30-ft range** and the special **fail by 5 or more => immediate Petrified** escalation (terminal Iron Pit outcome). Other failed saves follow existing Restrained → repeat-save → Petrified progression; source qualifiers preserved. Not implemented/certified.

### 021. Ochre Jelly

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:reaction`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.

### 022. Sea Horse

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:none`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Check whether the creature has any legal combat attack; if no, preserve source and classify arena-neutral rather than fabricating one.

### 023. Stirge

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `arena:removed`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Check established Pit exclusion and retain explicit audit record; do not quietly count as certified.

### 024. Stone Giant

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:reaction`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.

### 025. Acolyte

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 026. Archmage

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 027. Balor

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Death Throes; Fire Aura
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 028. Banshee

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Detect Life
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 029. Barbed Devil

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:range`, `source:trait`.
- **Unbound printed traits:** Barbed Hide
- **Fix notes:** Correct reach/range bands from printed source; verify legal attack selection and shared range penalties. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Barbed Hide: reuse contact retaliation; verify printed trigger and damage.

### 030. Behir

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 031. Bugbear

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Surprise Attack
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 032. Clay Golem

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 033. Cloud Giant

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 034. Cult Fanatic

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 035. Darkmantle

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 036. Deep Gnome (Svirfneblin)

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 037. Drider

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 038. Druid

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 039. Erinyes

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Hellish Weapons
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 040. Fire Elemental

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Fire Form; Water Susceptibility
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Fire Form/Water Susceptibility: reuse contact/fire application and damage-from-environment primitives; retain Pit environment policy.

### 041. Gelatinous Cube

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Ooze Cube; Transparent
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 042. Giant Frog

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:swallow`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 043. Giant Toad

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:swallow`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 044. Glabrezu

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 045. Gray Ooze

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Corrode Metal
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 046. Homunculus

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Telepathic Bond
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 047. Horned Devil

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `attack:range`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Correct reach/range bands from printed source; verify legal attack selection and shared range penalties.

### 048. Ice Devil

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 049. Imp

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 050. Mage

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 051. Manticore

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:limited-use`, `source:trait`.
- **Unbound printed traits:** Tail Spike Regrowth
- **Fix notes:** Bind printed uses, spending and recovery to existing generic resource model. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 052. Marilith

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Reactive
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 053. Mimic

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Shapechanger; Adhesive (Object Form Only); False Appearance (Object Form Only); Grappler
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 054. Mummy

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 055. Nightmare

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Confer Fire Resistance
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 056. Priest

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Divine Eminence; Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 057. Pseudodragon

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Limited Telepathy
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 058. Purple Worm

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `mechanic:swallow`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics.

### 059. Roper

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Grasping Tendrils
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 060. Rust Monster

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Iron Scent; Rust Metal
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 061. Salamander

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:trait`.
- **Unbound printed traits:** Heated Body
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Heated Body: generic touch retaliation; tail: exact own-grapple auto-hit constraint, not mere Advantage.

### 062. Sea Hag

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Horrific Appearance
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 063. Shadow

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Sunlight Weakness
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 064. Shield Guardian

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:reaction`, `source:trait`.
- **Unbound printed traits:** Bound; Spell Storing
- **Fix notes:** Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 065. Shrieker

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:none`, `source:reaction`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Check whether the creature has any legal combat attack; if no, preserve source and classify arena-neutral rather than fabricating one. Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.

### 066. Spectator

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:reaction`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.

### 067. Spirit Naga

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 068. Sprite

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 069. Storm Giant

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 070. Succubus/Incubus

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Telepathic Bond; Shapechanger
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 071. Vrock

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 072. Werebear

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 073. Werewolf

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 074. Will-o'-Wisp

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Consume Life; Ephemeral; Variable Illumination
- **Fix notes:** Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Consume Life/Ephemeral/Variable Illumination: separate HP-threshold/terminal trigger, movement/material interactions and illumination.

### 075. Air Elemental

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Air Form
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Air Form: reuse movement, spaces and creature occupancy constraints; do not reduce to presentation.

### 076. Bearded Devil

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `attack:incomplete`, `source:trait`.
- **Unbound printed traits:** Steadfast
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** M-025 Steadfast: conditional Frightened immunity requires live active ally; PR #654 partially implemented, not certified. Then Beard: save -> Poisoned plus healing restriction; Glaive: stacking 1d10 ongoing wound, cleared on magical healing (Pit globally disallows Medicine checks).

### 077. Black Pudding

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:reaction`, `source:trait`.
- **Unbound printed traits:** Corrosive Form
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 078. Chain Devil

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:extra-action`, `source:reaction`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Map the exact trigger, eligibility, timing and effect to shared reaction grammar; preserve one-Reaction economy.

### 079. Cloaker

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Damage Transfer; Light Sensitivity
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 080. Deva

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 081. Doppelganger

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger; Ambusher; Surprise Attack
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 082. Drow

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 083. Dryad

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting; Speak with Beasts and Plants; Tree Stride
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 084. Duergar

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Duergar Resilience
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 085. Efreeti

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:range`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Elemental Demise; Innate Spellcasting
- **Fix notes:** Correct reach/range bands from printed source; verify legal attack selection and shared range penalties. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 086. Ettercap

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Preserve each distinct printed typed damage component, including hit riders and defense interaction. Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge.

### 087. Flameskull

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:range`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Correct reach/range bands from printed source; verify legal attack selection and shared range penalties. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 088. Ghost

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Ethereal Sight
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 089. Giant Spider

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Preserve each distinct printed typed damage component, including hit riders and defense interaction. Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge.

### 090. Gibbering Mouther

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Aberrant Ground; Gibbering
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 091. Green Hag

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 092. Guardian Naga

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 093. Hydra

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Multiple Heads; Reactive Heads
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Multiple/Reactive Heads: shared head count, sever/regrow triggers, attack count and reactions driven by combat state.

### 094. Ice Mephit

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Death Burst; Innate Spellcasting
- **Fix notes:** Use generic death/zero-HP event trigger to apply source-driven area/damage/condition consequences. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 095. Magma Mephit

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Death Burst; Innate Spellcasting
- **Fix notes:** Use generic death/zero-HP event trigger to apply source-driven area/damage/condition consequences. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 096. Magmin

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:death-trigger`, `source:trait`.
- **Unbound printed traits:** Death Burst; Ignited Illumination
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Use generic death/zero-HP event trigger to apply source-driven area/damage/condition consequences. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 097. Night Hag

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 098. Otyugh

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Limited Telepathy
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 099. Pit Fiend

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Fear Aura; Innate Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 100. Planetar

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Divine Awareness; Innate Spellcasting
- **Fix notes:** Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 101. Quasit

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Decompose printed attack into base hit plus reusable saves, conditions, recurring/secondary riders and their exits; prove Python/browser parity. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 102. Rakshasa

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:defense`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Limited Magic Immunity; Innate Spellcasting
- **Fix notes:** Model printed defense as appropriate shared resistance/immunity/saving modifier, with source qualifiers. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 103. Remorhaz

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:swallow`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Heated Body
- **Fix notes:** Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Heated Body: contact retaliation with source fire dice and temperature-independent Pit interpretation.

### 104. Rug of Smothering

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:none`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Damage Transfer
- **Fix notes:** Check whether the creature has any legal combat attack; if no, preserve source and classify arena-neutral rather than fabricating one. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Damage Transfer: reuse distributed incoming damage primitive if exact; integrate grapple/restrain and existing susceptibility.

### 105. Shambling Mound

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:swallow`, `multiattack:complex`, `source:extra-action`.
- **Unbound printed traits:** None listed; inspect actions/other blockers.
- **Fix notes:** Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it.

### 106. Steam Mephit

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`.
- **Unbound printed traits:** Death Burst; Innate Spellcasting
- **Fix notes:** Use generic death/zero-HP event trigger to apply source-driven area/damage/condition consequences. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 107. Vampire Spawn

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `multiattack:complex`, `source:trait`.
- **Unbound printed traits:** Vampire Weaknesses
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Vampire Weaknesses: evaluate environment-derived damage/restrictions plus existing attack riders.

### 108. Water Elemental

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Water Form; Freeze
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Water Form/Freeze: reuse space/water traversal and susceptibility/condition with actual trigger.

### 109. Wereboar

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 110. Wererat

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 111. Weretiger

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Shapechanger; Pounce (Tiger or Hybrid Form Only)
- **Fix notes:** Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 112. Chuul

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Sense Magic
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 113. Couatl

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting; Shielded Mind
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 114. Djinni

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Elemental Demise; Innate Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 115. Dust Mephit

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:recharge`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Death Burst; Innate Spellcasting
- **Fix notes:** Bind printed recharge threshold and trigger to universal resource refill; do not create monster-specific recharge. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 116. Gynosphinx

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Inscrutable; Spellcasting
- **Fix notes:** Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 117. Lich

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 118. Oni

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 119. Aboleth

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:legendary`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Mucous Cloud; Probing Telepathy
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 120. Androsphinx

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Inscrutable; Spellcasting
- **Fix notes:** Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 121. Lamia

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:spellcasting`, `multiattack:complex`, `source:extra-action`, `source:trait`.
- **Unbound printed traits:** Innate Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 122. Tarrasque

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `mechanic:legendary`, `mechanic:swallow`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Reflective Carapace
- **Fix notes:** Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 123. Mummy Lord

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 124. Solar

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Divine Awareness; Innate Spellcasting
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Map only arena-legal printed spells to the correct 2014 spell primitives and slot/at-will resource model; document each unsupported spell separately. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

### 125. Vampire

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:legendary`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Shapechanger; Misty Escape; Vampire Weaknesses
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.
- **Known directed work:** Shapechanger + Misty Escape + weaknesses: separate form state, zero-HP escape and environmental/debuff rules before legendary/actions.

### 126. Kraken

- [ ] **SOURCE REVIEW / BIND / TEST / CERTIFY / MERGE** — not yet individually verified by this worksheet.
- **Recorded blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:swallow`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`.
- **Unbound printed traits:** Freedom of Movement
- **Fix notes:** Restore complete printed attack damage/on-hit rider fields and serialize through attack schema; retain damage types, saves and timing. Connect exact legendary Action costs, turn timing and effects to existing generic legendary-action execution. Inspect swallowed-state lifecycle, damage, escape/release and movement and reuse existing grapple, timed damage, swallowed/exile primitives where equivalent; record any true missing semantics. Represent source's exact slots, alternatives, hit dependencies and count via existing sequence engine; do not approximate attack counts. Inspect the named extra action and represent its action cost, exact targeting/save/damage/condition via shared Action capabilities; mark as arena-unavailable only if an existing locked Pit rule actually covers it. Inventory each printed legendary option and bind to a parameterized generic action; keep source wording for logs. Read each unbound trait verbatim; decompose trigger, effect, qualifiers, duration and exit; reuse existing passive/buff/condition primitives. Do not equate printed names with mechanics.

## Tracking discipline

A checked entry means fully source-bound, tested in both engines, relevant CI green, merged and generated classifier updated. An ability resolved inside a still-blocked monster must be noted in the tracker without marking the whole monster complete. Note PR, SHA, gates and remaining blockers below each entry as work closes. If a category is only classifier metadata, correct the classifier/generator rather than adding duplicate runtime code.
