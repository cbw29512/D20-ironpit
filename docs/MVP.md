# Iron Pit D20 — Locked MVP

## Definition of Done

The MVP is complete when a user can open the deployed Netlify site, start a server-resolved duel between **Aldric Vane (Level 1 Fighter)** and the **SRD 5.2.1 Goblin Warrior**, watch the battle replay through stick-figure animation events, and see a winner that matches the FastAPI battle result.

The locked acceptance test remains the **5-foot melee duel**. A separate **90-foot ranged development mode** now exercises movement, Dash, weapon selection, Shortbow range, and projectile replay without changing that acceptance target.

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
- Level-1 Fighter Second Wind: 2 uses, Bonus Action, 1d10 + Fighter level healing, capped at max HP.

## Implemented development extensions

- Typed melee/ranged weapon metadata.
- Goblin Shortbow: 80/320 ft., Piercing damage, projectile metadata.
- Ranged attacks beyond normal range have Disadvantage; attacks beyond long range are illegal.
- Ranged attacks within 5 feet of an active enemy have Disadvantage.
- Goblin attacks made with Advantage add the SRD conditional d4 damage.
- Critical hits double both base and other attack damage dice.
- Speed, remaining movement, Action availability, movement events, and Dash.
- Arena weapon selection prefers the primary weapon, then a legal alternate.
- Optional 90-foot ranged duel endpoint and UI control.

## Required presentation behavior

- Fighter uses a longsword and shield visual loadout.
- Goblin uses a scimitar and shield visual loadout with Shortbow available as an alternate.
- Combatant labels, HP, level/CR, weapon, armor, and off-hand data hydrate from the API.
- Attack events produce stick-figure weapon swings.
- Projectile attacks flash an arrow in the attack direction.
- Movement events update the displayed distance and animate an advance.
- Hits visibly react and update HP.
- Critical hits receive a distinct animation state.
- Second Wind produces a healing pulse and HP recovery.
- Death produces a defeated visual state.

## Required platform behavior

- Source is hosted publicly on GitHub.
- GitHub Actions tests backend rules, source-size limits, frontend JavaScript syntax, Netlify configuration generation, and the Docker image build.
- Frontend deploys to Netlify.
- FastAPI deploys as a Docker service.
- No secrets are committed.

## Published arena assumptions / tactics

- Initiative ties currently use initiative bonus as the arena tiebreaker.
- The demo Fighter uses Second Wind at or below half maximum HP when a use and Bonus Action remain.
- A combatant prefers its primary weapon; if it is out of range, it selects the first legal alternate weapon.
- If no weapon can attack, the combatant advances toward primary-weapon range and Dashes if one normal move is insufficient.
- The Goblin does not yet kite away from the Fighter.

## Explicitly deferred

- User accounts and Supabase persistence.
- Betting, cash-value predictions, crypto, or NFTs.
- Multiple character levels and classes.
- Character selection UI.
- Monster selection UI.
- Opportunity attacks and Disengage.
- Goblin Nimble Escape/Hide behavior.
- Cover and terrain.
- Spells and spell effects.
- Conditions such as Petrified.
- Breath weapons.
- Fighter Weapon Mastery.

These are expansions after the deployed Fighter-vs-Goblin vertical slice is verified.
