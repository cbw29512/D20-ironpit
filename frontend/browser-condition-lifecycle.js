(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  const label = (id) => id.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
  function repeatSaveDue(effect, round, timing) {
    if (effect.repeat_save_timing !== timing) return false;
    return !(effect.effect_id === "poisoned" && effect.applied_round != null && round <= effect.applied_round);
  }

  function resolveTargetTiming(sequence, round, target, timing) {
    const events = [];
    for (const effect of [...target.state.timed_effects]) {
      if (!target.state.timed_effects.includes(effect)) continue;
      if (repeatSaveDue(effect, round, timing)) {
        const save = V().resolveSavingThrow(target.state, effect.repeat_save_ability, effect.repeat_save_dc);
        const removed = save.succeeded ? T().removeGroup(target.state, effect) : [];
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: effect.repeat_save_ability,
          save_dc: effect.repeat_save_dc, save_succeeded: save.succeeded,
          removed_condition_ids: removed,
          feature_id: effect.source_effect_id || "condition-repeat-save", animation: "condition-save",
          description: `${target.state.template.name} repeats the ${effect.repeat_save_ability} save against ${label(effect.source_effect_id || effect.effect_id)}: ${save.succeeded ? "SUCCESS" : "FAILURE"}.`,
        });
        if (save.succeeded) continue;
      }
      if (effect.expiry_timing === timing) {
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.`,
        });
      }
    }
    if (timing === "target_turn_end") M()?.expireTargetTurn(target.state);
    return { events, sequence };
  }

  function resolveSourceTiming(sequence, round, source, setup, timing) {
    const events = [];
    for (const target of [...setup.heroes, ...setup.monsters]) {
      const expiring = target.state.timed_effects.filter((effect) =>
        effect.source_id === source.combatant_id && effect.expiry_timing === timing,
      );
      for (const effect of expiring) {
        if (!target.state.timed_effects.includes(effect)) continue;
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.`,
        });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = { resolveSourceTiming, resolveTargetTiming };
})();
