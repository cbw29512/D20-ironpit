(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const P = () => window.IRON_PIT_BROWSER_HEALING_POLICY;
  const H = () => window.IRON_PIT_BROWSER_HEALING;

  function resolveGroup(
    sequence, round, healer, targets, action, turnKey = null, setup = null,
  ) {
    if ((action.maxTargets || 1) <= 1 || !targets.length || targets.length > action.maxTargets) {
      throw new Error("Illegal group healing target set.");
    }
    if (targets.some((target) => !P().targetAllowed(healer, target, action))
      || !P().resourceAvailable(healer, action, turnKey)) {
      throw new Error("Illegal group healing target or turn.");
    }
    if (!P().areaTargetsFit(healer, setup, action, targets)) {
      throw new Error("Group healing targets do not fit one legal healing area.");
    }
    if (P().slotHeal(action)) {
      if (!turnKey) throw new Error("Spell-slot group healing requires an active turn key.");
      C().markSlotSpellCast(healer.state, turnKey);
    }
    E().spend(healer.state, action.actionCost);
    healer.state.resources[action.resourceId] -= action.resourceCost || 1;
    const remaining = healer.state.resources[action.resourceId];
    const events = [];
    for (const target of targets) {
      const maximized = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.healingMaximized(target.state) || false;
      const rolls = Array.from(
        { length: action.diceCount || 0 },
        () => maximized ? (action.diceSize || 6) : window.IRON_PIT_DICE.roll(action.diceSize || 6),
      );
      const total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.healingBonus || 0);
      const before = target.state.current_hp;
      const healed = H().restore(target.state, total);
      events.push({
        sequence: sequence++,
        round_number: round,
        event_type: "healing",
        actor_id: healer.combatant_id,
        actor_name: healer.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        healing_roll: {
          notation: `${rolls.length}d${action.diceSize || 6}+${action.healingBonus || 0}`,
          rolls,
          modifier: action.healingBonus || 0,
          total,
        },
        hp_before: before,
        hp_after: target.state.current_hp,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable,
        is_dead: target.state.is_dead,
        feature_id: action.id,
        resource_remaining: remaining,
        animation: action.animation || "healing",
        description: `${healer.state.template.name} uses ${action.name} on ${target.state.template.name} and restores ${healed} HP.`,
      });
    }
    const rider = H().selfRider(
      sequence,
      round,
      healer,
      action,
      targets.some((target) => target.combatant_id !== healer.combatant_id),
    );
    if (rider) events.push(rider);
    return { events, sequence: sequence + (rider ? 1 : 0) };
  }

  window.IRON_PIT_BROWSER_GROUP_HEALING = { resolveGroup };
})();
