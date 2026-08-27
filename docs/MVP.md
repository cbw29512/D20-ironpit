# Iron Pit D20 — Locked MVP

## Definition of Done

The MVP is complete when a user can open the deployed Netlify site, start a server-resolved duel between **Aldric Vane (Level 1 Fighter)** and the **SRD 5.2.1 Goblin Warrior**, watch the battle replay through stick-figure animation events, and see a winner that matches the FastAPI battle result.

The locked acceptance test remains the **5-foot melee duel**. A separate **90-foot ranged development mode** exercises movement, Dash, weapon selection, range, and projectile replay without changing that acceptance target. Catalog expansion must not weaken this regression target.

## Required combat behavior

- Secure OS-backed dice rolls.
- Initiative with modifiers.
- Melee attack rolls against Armor Class.
- Natural 1 miss behavior.
- Natural 20 hit and critical damage dice.
- Damage and HP tracking.
- Combat ends at 0 HP.
- Immutable-style ordered battle event output for replay/audit.
- Advantage/disadvantage preserves both d20s and the selected result.
- Fighter Second Wind scales its healing modifier and uses from the selected pregen level.

## Implemented development extensions

- Data-driven combatant catalog with stable character and monster IDs.
- Character and monster catalog entries are split into separate modules behind a small registry facade.
- Catalog rules coverage: `fully_implemented`, `arena_assumption`, or `unsupported`.
- Generic ID-driven `POST /api/battles` endpoint plus character and monster catalog endpoints.
- Gladiator and monster selection controls driven by catalog data.
- Original Fighter pregens: Aldric Vane (Level 1) and Mara Stone (Level 5).
- SRD Goblin Warrior, Skeleton (CR 1/4), Ogre (CR 2), and Knight (CR 3) catalog entries.
- Attack actions support a configurable number of attacks while preserving one Action expenditure.
- Fighter Extra Attack is implemented for the Level 5 pregen; Knight Multiattack uses the same action-safe event sequencing.
- Typed melee, ranged, and thrown weapon metadata.
- Attack-profile damage dice overrides keep intrinsic equipment dice combatant-neutral.
- Typed unconditional and Advantage-triggered damage riders.
- Radiant damage and the Knight's always-on Radiant attack rider.
- Typed damage Vulnerability, Resistance, and Immunity with raw roll and applied damage kept separate.
- SRD Resistance-before-Vulnerability ordering and same-type damage grouping.
- Goblin Shortbow: 80/320 ft., Piercing damage, projectile metadata.
- Ogre Javelin melee/thrown handling at 30/120 ft.
- Knight Greatsword and Heavy Crossbow attack profiles, including two attacks per action.
- Ranged/thrown attacks beyond normal range have Disadvantage; attacks beyond long range are illegal.
- Ranged attacks within 5 feet of an active enemy have Disadvantage.
- Goblin attacks made with Advantage add the SRD conditional d4 damage.
- Critical hits double base and other attack damage dice, including unconditional riders.
- Speed, remaining movement, Action availability, movement events, and Dash.
- Arena weapon selection prefers the primary weapon, then a legal alternate.
- Optional 90-foot ranged duel endpoint and UI control.

## Required presentation behavior

- Fighter uses a longsword and shield visual loadout.
- Monster labels, HP, CR, weapon, armor, off-hand, and body style hydrate from catalog/API data.
- Goblinoid, skeleton, giant, and humanoid body styles are supported.
- Monster weapon shapes include Scimitar, Shortsword, Greatclub, Greatsword, Shortbow, Heavy Crossbow, and Javelin.
- Attack replay temporarily renders the weapon actually used by the event rather than only the default loadout.
- Projectile attacks animate arrows, crossbow bolts, or thrown javelins in the attack direction.
- Movement events update the displayed distance and animate an advance.
- Hits visibly react and update HP.
- Critical hits receive a distinct animation state.
- Damage defenses preserve the raw roll in the log and show adjusted damage when different.
- Second Wind produces a healing pulse and HP recovery.
- Death produces a defeated visual state.

## Required platform behavior

- Source is hosted publicly on GitHub.
- Active development occurs on `develop`; `main` is reserved for deliberate production releases.
- GitHub Actions tests backend rules, source-size limits, frontend JavaScript syntax, Netlify configuration generation, and the Docker image build.
- Production Python and JavaScript source files are limited to 150 lines; growth is handled by modularization rather than weakening the guard.
- Netlify builds are guarded so non-production contexts are skipped.
- Frontend production deploys to Netlify only from an intentional `main` release.
- FastAPI deploys as a Docker service.
- No secrets are committed.

## Published arena assumptions / tactics

- Initiative ties currently use initiative bonus as the arena tiebreaker.
- Fighters use Second Wind at or below half maximum HP when a use and Bonus Action remain.
- A combatant prefers its primary weapon; if it is out of range, it selects the first legal alternate weapon.
- If no weapon can attack, the combatant advances toward primary-weapon range and Dashes if one normal move is insufficient.
- The Goblin does not yet kite away from the Fighter.
- Ogre Javelin inventory depletion is not yet tracked; its SRD stat block lists three Javelins.
- Knight Multiattack currently repeats one selected legal attack profile; the SRD stat block allows Greatsword or Heavy Crossbow in any combination.
- Mara Stone is a fixed original development pregen; Defense is baked into AC 19 while subclass, Action Surge, Tactical Shift, and Weapon Mastery effects remain unsupported.

## Explicitly deferred

- User accounts and Supabase persistence.
- Betting, cash-value predictions, crypto, or NFTs.
- Broad class coverage beyond current Fighter pregens.
- Fighter Action Surge, Tactical Shift, subclass features, and Weapon Mastery effects.
- Knight Parry and Frightened condition immunity.
- Opportunity attacks and Disengage.
- Goblin Nimble Escape/Hide behavior.
- Exhaustion, Poisoned, Frightened, and other general condition-state handling.
- Cover and terrain.
- Spells and spell effects.
- Conditions such as Petrified.
- Breath weapons.
- Finite weapon/ammunition inventory.

These remain expansions after the deployed Fighter-vs-Goblin vertical slice is verified.
