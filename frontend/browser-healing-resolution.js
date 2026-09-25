(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_HEALING_POLICY;

  function spendResource(healer, action) {
    if (!action.resourceId) return null;
    healer.state.resources[action.resourceId] -= action.resourceCost || 1;
    return healer.state.resources[action.resourceId];
  }

  function percentileGate(sequence, round, healer, target, action, remaining) {
    if (action.percentileSuccessMax == null) return { featureRoll: null, event: null };
    const rolled = window.IRON_PIT_DICE.roll(100);
    const featureRoll = {
      notation: "1d100", rolls: [rolled], modifier: 0,
      selected_roll: rolled, mode: "normal", total: rolled,
    };
    if (rolled <= action.percentileSuccessMax) return { featureRoll, event: null };
    return {
      featureRoll,
      event: {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: healer.combatant_id,
        actor_name: healer.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        feature_roll: featureRoll,
        hp_before: target.state.current_hp,
        hp_after: target.state.current_hp,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable,
        is_dead: target.state.is_dead,
        feature_id: action.id,
        resource_remaining: remaining,
        animation: action.animation || "healing",
        description: `${healer.state.template.name} uses ${action.name} and rolls ${rolled} on d100; the intervention fails (needed ${action.percentileSuccessMax} or lower).`,
      },
    };
  }

  function resolve(sequence, round, healer, target, action, turnKey, restore) {
    if (!P().targetAllowed(healer, target, action)
      || !P().resourceAvailable(healer, action, turnKey)) {
      throw new Error("Illegal healing target or turn.");
    }
    if (P().slotHeal(action)) {
      if (!turnKey) throw new Error("Spell-slot healing requires an active turn key.");
      C().markSlotSpellCast(healer.state, turnKey);
    }
    E().spend(healer.state, action.actionCost);
    const remaining = spendResource(healer, action);
    const gate = percentileGate(sequence, round, healer, target, action, remaining);
    if (gate.event) return gate.event;

    const hpBefore = target.state.current_hp;
    let rolls = [], healed = 0, rollTotal = 0, notation = "", modifier = 0;
    if (action.restoreToEffectiveMax) {
      const amount = S().effectiveMaxHp(target.state) - target.state.current_hp;
      healed = restore(target.state, amount);
      rollTotal = healed;
      notation = "restore-to-effective-max";
    } else {
      const maximized = P().healingMaximized(healer, target);
      rolls = Array.from(
        { length: action.diceCount || 0 },
        () => maximized ? (action.diceSize || 6) : window.IRON_PIT_DICE.roll(action.diceSize || 6),
      );
      const total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.healingBonus || 0);
      rollTotal = total;
      healed = restore(target.state, total);
      notation = rolls.length
        ? `${rolls.length}d${action.diceSize || 6}+${action.healingBonus || 0}`
        : String(action.healingBonus || 0);
      modifier = action.healingBonus || 0;
    }

    const description = gate.featureRoll
      ? `${healer.state.template.name} uses ${action.name} and rolls ${gate.featureRoll.total} on d100; the intervention succeeds. ${target.state.template.name} is restored for ${healed} HP.`
      : `${healer.state.template.name} uses ${action.name} on ${target.state.template.name} and restores ${healed} HP.`;

    return {
      sequence, round_number: round, event_type: "healing",
      actor_id: healer.combatant_id, actor_name: healer.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      feature_roll: gate.featureRoll,
      healing_roll: { notation, rolls, modifier, total: rollTotal },
      hp_before: hpBefore, hp_after: target.state.current_hp,
      death_save_successes: target.state.death_save_successes,
      death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      feature_id: action.id, resource_remaining: remaining,
      animation: action.animation || "healing", description,
    };
  }

  window.IRON_PIT_BROWSER_HEALING_RESOLUTION = { resolve };
})();
