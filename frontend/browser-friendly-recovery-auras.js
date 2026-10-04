(() => {
  "use strict";

  const SHARE = "recovery-share";
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => state.is_unconscious || state.active_effect_ids?.includes("incapacitated"),
  };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];
  const alliesOf = (source, setup) => (source.side === "heroes" ? setup.heroes : setup.monsters);

  function active(source, actionId) {
    try {
      const state = source.state;
      if (state.is_dead || !state.is_alive || state.current_hp <= 0 || Q().incapacitated(state)) return false;
      return (state.timed_effects || []).some((effect) =>
        effect.source_id === source.combatant_id && effect.source_effect_id === actionId);
    } catch (error) {
      console.error("Failed recovery-aura source check.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function inAura(source, target, radiusFt) {
    return S().distance(source, target) <= radiusFt;
  }

  function maxHp(state) {
    return S()?.effectiveMaxHp(state)
      ?? ((state.template.max_hp || 0) + (state.max_hp_bonus || 0) - (state.hit_point_maximum_reduction || 0));
  }

  function restore(state, amount) {
    const healing = window.IRON_PIT_BROWSER_HEALING;
    if (healing?.restore) return healing.restore(state, amount);
    if (state.is_dead || amount <= 0) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(maxHp(state), before + amount);
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

  function rollHeal(aura) {
    let total = aura.heal_flat || 0;
    const count = aura.heal_dice_count || 0;
    for (let index = 0; index < count; index += 1) total += window.IRON_PIT_DICE.roll(aura.heal_dice_size || 6);
    return total;
  }

  function chooseHealTarget(source, setup, radiusFt) {
    try {
      const candidates = [];
      for (const target of alliesOf(source, setup)) {
        if (target.state.is_dead || !target.state.is_alive) continue;
        if (!inAura(source, target, radiusFt)) continue;
        const missing = maxHp(target.state) - target.state.current_hp;
        if (missing <= 0) continue;
        candidates.push([target.state.current_hp > 0, -missing, target.combatant_id, target]);
      }
      if (!candidates.length) return null;
      candidates.sort((left, right) => Number(left[0]) - Number(right[0]) || left[1] - right[1]
        || String(left[2]).localeCompare(String(right[2])));
      return candidates[0][3];
    } catch (error) {
      console.error("Failed recovery-aura target choice.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function healTarget(source, action, setup) {
    try {
      const aura = action.friendlyRecoveryAura;
      if (!aura || !setup) return 0;
      if (!(aura.heal_dice_count || aura.heal_flat)) return 0;
      const target = chooseHealTarget(source, setup, aura.radius_ft);
      if (!target) return 0;
      return restore(target.state, rollHeal(aura));
    } catch (error) {
      console.error("Failed recovery-aura heal.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function applyHitPointMaximumReduction(state, amount) {
    try {
      if (amount < 0) throw new Error("Hit point maximum reduction cannot be negative.");
      if (amount === 0) return 0;
      if ((state.timed_effects || []).some((effect) => effect.prevent_hit_point_maximum_reduction)) return 0;
      state.hit_point_maximum_reduction = (state.hit_point_maximum_reduction || 0) + amount;
      const maximum = maxHp(state);
      if (state.current_hp > maximum) state.current_hp = maximum;
      return amount;
    } catch (error) {
      console.error("Failed to reduce hit point maximum.", { error });
      throw error;
    }
  }

  function activate(source, action, setup, round) {
    try {
      const aura = action.friendlyRecoveryAura;
      if (!aura) return;
      for (const effect of source.state.timed_effects || []) {
        if (effect.source_id === source.combatant_id && effect.source_effect_id === action.id) {
          effect.prevent_hit_point_maximum_reduction = Boolean(aura.prevent_hp_maximum_reduction);
        }
      }
      if (aura.heal_on_create) healTarget(source, action, setup);
      if (setup) sync(setup);
    } catch (error) {
      console.error("Failed to activate recovery aura.", { action: action?.id, error });
      throw error;
    }
  }

  function sync(setup) {
    try {
      if (!setup || !T()) return;
      for (const member of members(setup)) {
        member.state.timed_effects = (member.state.timed_effects || [])
          .filter((effect) => effect.source_effect_id !== SHARE);
        if ((member.state.active_effect_ids || []).includes(SHARE)
          && !(member.state.timed_effects || []).some((effect) => effect.effect_id === SHARE)) {
          member.state.active_effect_ids = member.state.active_effect_ids.filter((id) => id !== SHARE);
        }
      }
      for (const source of members(setup)) {
        for (const action of source.state.template.timed_self_buff_actions || []) {
          const aura = action.friendlyRecoveryAura;
          if (!aura || !active(source, action.id)) continue;
          if (!(aura.necrotic_resistance || aura.prevent_hp_maximum_reduction)) continue;
          for (const target of alliesOf(source, setup)) {
            if (target.combatant_id === source.combatant_id) continue;
            if (target.state.is_dead || !target.state.is_alive) continue;
            if (!inAura(source, target, aura.radius_ft)) continue;
            T().apply(target.state, SHARE, source.combatant_id, {
              sourceEffectId: SHARE,
              sourceTemplate: source.state.template,
              sourceIsMagical: true,
              appliedRound: source.state.current_round,
              ownedDamageResistances: aura.necrotic_resistance ? ["necrotic"] : [],
              useDefaultPoisonRecovery: false,
            });
            for (const effect of target.state.timed_effects || []) {
              if (effect.effect_id === SHARE && effect.source_id === source.combatant_id) {
                effect.prevent_hit_point_maximum_reduction = Boolean(aura.prevent_hp_maximum_reduction);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to synchronize friendly recovery auras.", { error });
      throw error;
    }
  }

  function resolveWindows(member, setup) {
    try {
      if (!member || !setup) return;
      if (member.state.current_hp === 0 && !member.state.is_dead) {
        for (const source of members(setup)) {
          if (source.combatant_id === member.combatant_id || source.side !== member.side) continue;
          for (const action of source.state.template.timed_self_buff_actions || []) {
            const aura = action.friendlyRecoveryAura;
            if (!aura || (aura.zero_hp_ally_start_heal || 0) <= 0) continue;
            if (!active(source, action.id) || !inAura(source, member, aura.radius_ft)) continue;
            restore(member.state, aura.zero_hp_ally_start_heal);
            return;
          }
        }
      }
      for (const action of member.state.template.timed_self_buff_actions || []) {
        const aura = action.friendlyRecoveryAura;
        if (!aura || !aura.heal_on_source_turn_start || !active(member, action.id)) continue;
        healTarget(member, action, setup);
      }
    } catch (error) {
      console.error("Failed recovery-aura start-of-turn windows.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS = {
    activate, active, applyHitPointMaximumReduction, resolveWindows, sync,
  };
})();
