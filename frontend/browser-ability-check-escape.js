(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;
  const FRIGHTENED = "frightened";
  const POISONED = "poisoned";

  function escapeCheckEffects(state) {
    try {
      return (state.timed_effects || []).filter((effect) =>
        effect.escape_check_ability && effect.escape_check_dc != null);
    } catch (error) {
      console.error("Failed to list escape-check effects.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function shouldEscape(state) {
    try {
      return Boolean(E().available(state, "action") && escapeCheckEffects(state).length);
    } catch (error) {
      console.error("Failed to classify escape-check opportunity.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function abilityCheckBonus(state, ability) {
    const scores = state.template.ability_scores;
    if (!scores || !Number.isInteger(scores[ability])) {
      throw new Error(`${state.template.name} lacks ability scores for a ${ability} check.`);
    }
    return Math.floor((scores[ability] - 10) / 2);
  }

  function resolve(sequence, round, actor, setup = null) {
    try {
      if (!E().available(actor.state, "action")) throw new Error("Action is not available to attempt an escape check.");
      const effect = escapeCheckEffects(actor.state)[0];
      const ability = effect.escape_check_ability;
      const dc = effect.escape_check_dc;
      if (!ability || dc == null) throw new Error(`${actor.state.template.name} escape check is missing ability or DC.`);
      const disadvantage = (actor.state.active_effect_ids.includes(POISONED)
        || actor.state.active_effect_ids.includes(FRIGHTENED)) ? 1 : 0;
      const mode = A()?.mode
        ? A().mode(actor.state, 0, disadvantage)
        : R().modeFromSources(0, disadvantage);
      let check = R().d20(abilityCheckBonus(actor.state, ability) + (X()?.d20Modifier(actor.state) || 0), mode);
      const resolved = A()?.resolve
        ? A().resolve(actor.state, ability, check, dc, { roller: actor, setup, round })
        : { roll: check, succeeded: check.total >= dc };
      check = resolved.roll;
      const success = resolved.succeeded;
      E().spend(actor.state, "action");
      if (success) T().removeEffect(actor.state, effect);
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: actor.combatant_id,
        actor_name: actor.state.template.name,
        ability_check_roll: check,
        check_ability: ability,
        check_dc: dc,
        check_succeeded: success,
        feature_id: "escape-check",
        animation: "escape-check",
        removed_condition_ids: success ? [effect.effect_id] : [],
        description: `${actor.state.template.name} ${success ? "escapes" : "fails to escape"} ${effect.effect_id} with a ${ability} check against DC ${dc}.`,
      };
    } catch (error) {
      console.error("Failed escape check.", { combatant: actor?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE = {
    abilityCheckBonus, escapeCheckEffects, resolve, shouldEscape,
  };
})();
