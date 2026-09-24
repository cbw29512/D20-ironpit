(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_HEALING_POLICY;
  const G = () => window.IRON_PIT_BROWSER_GROUP_HEALING;

  function restore(state, amount) {
    if (state.is_dead || amount <= 0 || P().swarm(state)) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(S().effectiveMaxHp(state), before + amount);
    const healed = state.current_hp - before;
    if (healed > 0) {
      state.is_alive = true;
      state.is_unconscious = false;
      state.is_stable = false;
      state.death_save_successes = 0;
      state.death_save_failures = 0;
    }
    return healed;
  }

  function selfRider(sequence, round, healer, action, healedOther) {
    const rule = healer.state.template.slot_healing_other_self_rider;
    if (!rule || !healedOther || !P().slotHeal(action)) return null;
    const slotLevel = Number(action.resourceId.split("-").at(-1));
    const amount = (rule.flat_bonus || 0) + (rule.per_slot_level || 0) * slotLevel;
    const before = healer.state.current_hp;
    const healed = restore(healer.state, amount);
    if (!healed) return null;
    return {
      sequence,
      round_number: round,
      event_type: "healing",
      actor_id: healer.combatant_id,
      actor_name: healer.state.template.name,
      target_id: healer.combatant_id,
      target_name: healer.state.template.name,
      hp_before: before,
      hp_after: healer.state.current_hp,
      death_save_successes: healer.state.death_save_successes,
      death_save_failures: healer.state.death_save_failures,
      is_stable: healer.state.is_stable,
      is_dead: healer.state.is_dead,
      feature_id: rule.source_id,
      animation: "healing",
      description: `${healer.state.template.name} restores ${healed} HP from ${rule.source_id.replaceAll("-", " ")}.`,
    };
  }

  function resolve(sequence, round, healer, target, action, turnKey = null) {
    if (!P().targetAllowed(healer, target, action)
      || !P().resourceAvailable(healer, action, turnKey)) {
      throw new Error("Illegal healing target or turn.");
    }
    if (P().slotHeal(action)) {
      if (!turnKey) throw new Error("Spell-slot healing requires an active turn key.");
      C().markSlotSpellCast(healer.state, turnKey);
    }
    E().spend(healer.state, action.actionCost);
    let remaining = null;
    if (action.resourceId) {
      healer.state.resources[action.resourceId] -= action.resourceCost || 1;
      remaining = healer.state.resources[action.resourceId];
    }

    let featureRoll = null;
    if (action.percentileSuccessMax != null) {
      const rolled = window.IRON_PIT_DICE.roll(100);
      featureRoll = {
        notation: "1d100", rolls: [rolled], modifier: 0,
        selected_roll: rolled, mode: "normal", total: rolled,
      };
      if (rolled > action.percentileSuccessMax) {
        return {
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
        };
      }
    }

    const hpBefore = target.state.current_hp;
    let rolls = [];
    let total = 0;
    let healed = 0;
    let notation = "";
    let modifier = 0;
    if (action.restoreToEffectiveMax) {
      total = S().effectiveMaxHp(target.state) - target.state.current_hp;
      healed = restore(target.state, total);
      notation = "restore-to-effective-max";
    } else {
      const maximized = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.healingMaximized(target.state) || false;
      rolls = Array.from(
        { length: action.diceCount || 0 },
        () => maximized ? (action.diceSize || 6) : window.IRON_PIT_DICE.roll(action.diceSize || 6),
      );
      total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.healingBonus || 0);
      healed = restore(target.state, total);
      notation = rolls.length
        ? `${rolls.length}d${action.diceSize || 6}+${action.healingBonus || 0}`
        : String(action.healingBonus || 0);
      modifier = action.healingBonus || 0;
    }
    return {
      sequence,
      round_number: round,
      event_type: "healing",
      actor_id: healer.combatant_id,
      actor_name: healer.state.template.name,
      target_id: target.combatant_id,
      target_name: target.state.template.name,
      feature_roll: featureRoll,
      healing_roll: {
        notation,
        rolls,
        modifier,
        total: healed,
      },
      hp_before: hpBefore,
      hp_after: target.state.current_hp,
      death_save_successes: target.state.death_save_successes,
      death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable,
      is_dead: target.state.is_dead,
      feature_id: action.id,
      resource_remaining: remaining,
      animation: action.animation || "healing",
      description: featureRoll
        ? `${healer.state.template.name} uses ${action.name} and rolls ${featureRoll.total} on d100; the intervention succeeds. ${target.state.template.name} is restored for ${healed} HP.`
        : `${healer.state.template.name} uses ${action.name} on ${target.state.template.name} and restores ${healed} HP.`,
    };
  }

  window.IRON_PIT_BROWSER_HEALING = {
    bloodied: (...args) => P().bloodied(...args),
    chooseAction: (...args) => P().chooseAction(...args),
    chooseTarget: (...args) => P().chooseTarget(...args),
    groupTargets: (...args) => P().groupTargets(...args),
    resolve,
    resolveGroup: (...args) => G().resolveGroup(...args),
    restore,
    selfRider,
  };
})();
