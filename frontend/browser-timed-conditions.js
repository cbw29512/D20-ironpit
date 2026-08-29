(() => {
  "use strict";

  function apply(state, effectId, sourceId, expiresAtStartOfSourceTurn = true) {
    state.timed_effects = state.timed_effects.filter((effect) => !(effect.effect_id === effectId && effect.source_id === sourceId));
    state.timed_effects.push({ effect_id: effectId, source_id: sourceId, expires_at_start_of_source_turn: expiresAtStartOfSourceTurn });
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  }

  function removeEffect(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    const stillActive = state.timed_effects.some((item) => item.effect_id === effect.effect_id);
    if (!stillActive) state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
    return !stillActive;
  }

  function expireSourceStart(sequence, round, source, setup) {
    const events = [];
    for (const target of [...setup.heroes, ...setup.monsters]) {
      const expiring = target.state.timed_effects.filter((effect) => effect.source_id === source.combatant_id && effect.expires_at_start_of_source_turn);
      for (const effect of expiring) {
        if (!removeEffect(target.state, effect)) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: [effect.effect_id], feature_id: "condition-ended", animation: "condition-ended",
          description: `${target.state.template.name} is no longer ${effect.effect_id}.`,
        });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_TIMED = { apply, expireSourceStart };
})();
