# 2014 Roper — universal breakable Grapple, partial source audit

Source: pinned 2014 Roper, not a creature-specific runtime resolver.
**Roper remains blocked** until all combat-relevant traits/actions and
webpage-fight behavior are certified.

## Source parameters and state

- Tendril: +7 melee, 50-foot reach, zero damage; hit applies Grappled
  (escape DC 15) plus Restrained, with Disadvantage on Strength checks
  and saves while held. Limit six active tendrils.
- Each tendril: AC 20, 10 HP, immune to Poison and Psychic damage.
  The object has independent fight-local HP; destroying it releases
  only its corresponding Grapple and source-owned conditions, without
  damaging the held creature or the Roper.
- Break Action: a creature can spend an Action for a DC 15 Strength
  check against the tendril. This is separate from ordinary grapple
  escape. A destroyed tendril may be extruded on the Roper's next turn.
- Multiattack: four Tendril hits, Reel, then Bite. Reel is physical
  displacement only, ignored under the locked Iron Pit position rule.
  The shared ordered Multiattack slot binding already exists.

## This branch's completed universal primitive

The existing breakable object specification and state now also travel
through generic on-hit Grapple data, Python and browser state, and the
ordinary attack compiler/serializer. Both breakable timed restraints
and breakable grapple attachments share one typed damage/HP resolver.
Separate Python and browser tests verify immune and nonimmune damage,
AC misses, object destruction, Grapple release and card immutability.

## Still blocking complete Roper source admission

- Make the direct weapon attack against the appendage a real legal AI
  and player Action target, subject to object AC and reach.
- Implement generic helper Strength DC 15 Action to break the held
  appendage, with proper action economy.
- Restore a destroyed appendage's source capacity only on its next
  turn; do not grant an immediate free replacement.
- Certify those paths and a complete source-verified encounter in the
  Python/browser engines, then through an actual webpage fight.

Do not hand edit generated blockers, inventory or browser exports. This
is a deliberate partial engine improvement, **not a source-admission claim**.
