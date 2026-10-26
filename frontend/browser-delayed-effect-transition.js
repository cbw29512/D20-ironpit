(() => {
  "use strict";

  function schedule(state, effectId, sourceId, sourceEffectId, rule) {
    try {
      const effect = [...(state.timed_effects || [])].reverse().find((item) =>
        item.effect_id === effectId && item.source_id === sourceId
        && item.source_effect_id === sourceEffectId);
      if (!effect) throw new Error(`Applied timed effect ${effectId} could not be found.`);
      effect.removal_effect_tag = rule.removalEffectTag || null;
      effect.minimum_removal_spell_level = rule.minimumRemovalSpellLevel || 0;
      effect.removal_action_exceptions = [...(rule.removalActionExceptions || [])];
      if (rule.delayedTransition) {
        const transition = structuredClone(rule.delayedTransition);
        effect.activates_target_turn_count = (state.turns_started || 0) + transition.targetTurns;
        effect.pending_transition = transition;
      }
    } catch (error) {
      console.error("Failed to schedule delayed timed-effect transition.", { effectId, error });
      throw error;
    }
  }

  function activateDue(sequence, round, target) {
    const events = [];
    for (const effect of target.state.timed_effects || []) {
      const due = effect.activates_target_turn_count;
      const rule = effect.pending_transition;
      if (due == null || !rule || (target.state.turns_started || 0) < due) continue;
      effect.cannot_regain_hit_points = Boolean(rule.cannotRegainHitPoints);
      effect.removal_effect_tag = rule.removalEffectTag || null;
      effect.minimum_removal_spell_level = rule.minimumRemovalSpellLevel || 0;
      effect.removal_action_exceptions = [...(rule.removalActionExceptions || [])];
      effect.activates_target_turn_count = null;
      effect.pending_transition = null;
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: target.combatant_id, actor_name: target.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: effect.source_effect_id || effect.effect_id,
        animation: "condition-applied",
        description: `${effect.effect_id.replaceAll("_", " ")} advances on ${target.state.template.name}.`,
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_DELAYED_EFFECT_TRANSITION = { schedule, activateDue };
})();
