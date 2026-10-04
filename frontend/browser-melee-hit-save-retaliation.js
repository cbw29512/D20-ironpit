(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => state.is_unconscious || (state.active_effect_ids || []).includes("incapacitated"),
  };
  const SAVES = () => window.IRON_PIT_BROWSER_SAVING_THROWS || window.IRON_PIT_BROWSER_SAVES;

  function creatureType(state) {
    return String(state.template.creature_type || "").split(" (")[0].trim().toLowerCase();
  }

  function auraActive(source, actionId) {
    const state = source.state;
    if (state.is_dead || !state.is_alive || state.current_hp <= 0 || Q().incapacitated(state)) return false;
    return (state.timed_effects || []).some((effect) =>
      effect.source_id === source.combatant_id && effect.source_effect_id === actionId);
  }

  function apply(attacker, defender, options = {}) {
    try {
      if (!options.melee || !options.setup || attacker.state.is_dead || !attacker.state.is_alive) return null;
      if (defender.state.is_dead || !defender.state.is_alive) return null;
      const attackerType = creatureType(attacker.state);
      if (!attackerType) return null;
      const allies = defender.side === "heroes" ? options.setup.heroes : options.setup.monsters;
      for (const source of allies || []) {
        for (const action of source.state.template.timed_self_buff_actions || []) {
          const aura = action.friendlySaveAdvantageAura || action.friendly_save_advantage_aura;
          const rider = aura && (aura.meleeHitSaveRetaliation || aura.melee_hit_save_retaliation);
          if (!rider || !auraActive(source, action.id)) continue;
          const radius = aura.radius_ft ?? aura.radiusFt ?? 0;
          if (S().distance(source, defender) > radius) continue;
          const types = rider.attackerCreatureTypes || rider.attacker_creature_types || [];
          if (!types.map((item) => String(item).toLowerCase()).includes(attackerType)) continue;
          const ability = rider.saveAbility || rider.save_ability;
          const dc = rider.saveDc ?? rider.save_dc;
          const save = SAVES().resolveSavingThrow(attacker.state, ability, dc, {
            conditionId: rider.conditionId || rider.condition_id,
            magicalEffect: rider.magicalEffect !== false && rider.magical_effect !== false,
            roundNumber: options.round,
            encounterRoller: attacker,
            setup: options.setup,
          });
          if (save.succeeded) return null;
          const conditionId = rider.conditionId || rider.condition_id;
          const duration = rider.durationRounds ?? rider.duration_rounds ?? 1;
          const bind = rider.bindToSourceEffect || rider.bind_to_source_effect;
          const timed = window.IRON_PIT_BROWSER_TIMED;
          if (!timed) throw new Error("Melee-hit save retaliation requires timed conditions.");
          return timed.apply(attacker.state, conditionId, source.combatant_id, {
            sourceEffectId: bind ? action.id : `${action.id}-melee-blind`,
            sourceTemplate: source.state.template,
            sourceIsMagical: rider.magicalEffect !== false && rider.magical_effect !== false,
            appliedRound: options.round ?? null,
            expiresRound: bind || options.round == null ? null : options.round + duration,
            expiryTiming: bind ? null : (rider.expiryTiming || rider.expiry_timing || "target_turn_end"),
            useDefaultPoisonRecovery: false,
          });
        }
      }
      return null;
    } catch (error) {
      console.error("Failed melee-hit save retaliation", {
        attacker: attacker?.combatant_id, defender: defender?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MELEE_HIT_SAVE_RETALIATION = { apply };
})();
