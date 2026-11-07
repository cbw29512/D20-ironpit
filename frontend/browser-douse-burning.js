(() => {
  "use strict";
  // Self-douse only; source lacks range for a helper to target fire.
  const ID = "douse-fire";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  function effects(target) {
    try {
      return (target.state.timed_effects || []).filter(effect =>
        (effect.end_of_turn_dice_count > 0 || effect.start_of_turn_dice_count > 0)
        && (effect.allowed_removal_action_ids || []).includes(ID));
    } catch (error) { console.error("Douse eligibility failed", error); throw error; }
  }
  function choose(actor, setup) {
    try {
      if (!E().available(actor.state, "action")) return null;
      return actor.state.is_alive && !actor.state.is_dead && effects(actor).length ? actor : null;
    } catch (error) { console.error("Douse choice failed", error); throw error; }
  }
  function resolve(sequence, round, actor, target) {
    try {
      if (actor.combatant_id !== target.combatant_id)
        throw new Error("Helper dousing requires an unspecified target range.");
      const chosen = effects(target);
      if (!chosen.length || !target.state.is_alive || target.state.is_dead)
        throw new Error("Target has no source-authorized douseable effect.");
      if (!E().available(actor.state, "action")) throw new Error("Douse requires an available Action.");
      E().spend(actor.state, "action");
      const removed = [], sources = [];
      for (const effect of chosen) {
        if (effect.source_name && !sources.includes(effect.source_name)) sources.push(effect.source_name);
        if (T().removeEffect(target.state, effect)) removed.push(effect.effect_id);
      }
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: actor.combatant_id, actor_name: actor.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        removed_condition_ids: removed, feature_id: ID, animation: "condition-ended",
        description: `${actor.state.template.name} uses Douse Fire on ${target.state.template.name}; ${sources.join(", ") || "ongoing fire"} ends.`,
      };
    } catch (error) {
      console.error("Douse action failed", { actor: actor?.combatant_id, target: target?.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_DOUSE_BURNING = { choose, effects, resolve };
})();
