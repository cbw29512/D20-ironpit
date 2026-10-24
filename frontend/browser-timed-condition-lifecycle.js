(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function expireOnOwnerEvent(state, event, affectedStates = []) {
    try {
      if (!["attack", "spell_cast"].includes(event)) throw new Error(`Unknown owner expiry event: ${event}.`);
      const flag = event === "attack" ? "ends_on_owner_attack" : "ends_on_owner_spell_cast";
      const removed = [];
      for (const effect of [...(state.timed_effects || [])]) {
        if (!(state.timed_effects || []).includes(effect) || !effect[flag]) continue;
        const concentration = state.concentration;
        let ids;
        if (concentration && concentration.effect_id === effect.source_effect_id
          && concentration.source_id === effect.source_id) {
          ids = state.timed_effects.filter((item) => item.source_id === concentration.source_id
            && item.source_effect_id === concentration.effect_id).map((item) => item.effect_id);
          if (!window.IRON_PIT_BROWSER_CONCENTRATION?.end) throw new Error("Owner expiry requires the concentration engine.");
          window.IRON_PIT_BROWSER_CONCENTRATION.end(state, affectedStates);
        } else ids = T().removeGroup(state, effect);
        for (const id of ids) if (!removed.includes(id)) removed.push(id);
      }
      return removed;
    } catch (error) {
      console.error("Owner action timed-effect expiry failed.", { event, error });
      throw error;
    }
  }

  function removeOnMagicalHealing(state) {
    try {
      const removed = [];
      for (const effect of [...(state.timed_effects || [])]) {
        if (!effect.ends_on_magical_healing) continue;
        if (T().removeEffect(state, effect) && !removed.includes(effect.effect_id)) removed.push(effect.effect_id);
      }
      return removed;
    } catch (error) {
      console.error("Timed effect magical-healing cleanup failed", { error });
      throw error;
    }
  }

  function ownsDamageResistance(state, damageType) {
    try {
      return (state.timed_effects || []).some((effect) =>
        (effect.owned_damage_resistances || []).includes(damageType));
    } catch (error) {
      console.error("Timed resistance lookup failed.", error);
      throw error;
    }
  }

  function expireSourceStart(sequence, round, source, setup) {
    try {
      const events = [];
      for (const target of [...setup.heroes, ...setup.monsters]) {
        const expiring = target.state.timed_effects.filter((effect) =>
          effect.source_id === source.combatant_id
          && (effect.expiry_timing === "source_turn_start" || effect.expires_at_start_of_source_turn)
          && (!effect.expires_round || round >= effect.expires_round));
        for (const effect of expiring) {
          if (!target.state.timed_effects.includes(effect)) continue;
          const removed = T().removeGroup(target.state, effect);
          if (!removed.length) continue;
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: source.combatant_id, actor_name: source.state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
            animation: "condition-ended",
            description: `${target.state.template.name} is no longer affected by ${effect.source_effect_id || effect.effect_id}.`,
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Source-turn timed-effect expiry failed.", { source: source?.combatant_id, error });
      throw error;
    }
  }

  function resolveMovementCounters(state) {
    const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || { movementCost: () => null };
    const resolved = [
      ...(window.IRON_PIT_BROWSER_FLIGHT_GROUND?.resolveGroundConditions(state) || []),
    ];
    for (const effect of [...(state.timed_effects || [])]) {
      const cost = C().movementCost(state, effect.effect_id, { sourceIsMagical: Boolean(effect.source_is_magical) });
      if (cost == null || state.movement_remaining_ft < cost) continue;
      const removed = removeGroup(state, effect);
      if (!removed.length) continue;
      state.movement_remaining_ft -= cost;
      for (const debuffId of removed) resolved.push({ debuffId, sourceId: effect.source_id, movementCost: cost });
    }
    return resolved;
  }

  const timed = T();
  if (!timed) throw new Error("Timed-condition lifecycle extensions require browser-timed-conditions.js.");
  Object.assign(timed, { expireOnOwnerEvent, expireSourceStart, ownsDamageResistance, removeOnMagicalHealing, resolveMovementCounters });
})();