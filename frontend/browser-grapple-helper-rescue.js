(() => {
  "use strict";

  // A grappling source's immutable card owns the helper rule. Fight state
  // holds the source/target Grapple link; no printed-name combat dispatch.
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const A = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const X = () => window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;

  function eligible(helper, target, owner, rule) {
    try {
      return helper.combatant_id !== target.combatant_id
        && helper.side === target.side && helper.side !== owner.side
        && helper.state.is_alive && !helper.state.is_dead
        && target.state.is_alive && !target.state.is_dead
        && owner.state.is_alive && !owner.state.is_dead
        && !C().incapacitated(helper.state)
        && E().available(helper.state, rule.action_cost)
        && helper.state.template.ability_scores
        && S().distance(helper, owner) <= rule.helper_range_ft
        && (owner.state.template.grapple_rescue_rules || []).includes(rule)
        && (target.state.grapple_sources || []).some(
          (g) => g.source_id === owner.combatant_id
            && g.linked_effect_id === rule.source_action_id);
    } catch (error) {
      console.error("Source-linked helper rescue eligibility failed.", error);
      throw error;
    }
  }

  function choose(helper, setup) {
    try {
      const allies = helper.side === "heroes" ? setup.heroes : setup.monsters;
      const opponents = helper.side === "heroes" ? setup.monsters : setup.heroes;
      const choices = [];
      for (const owner of opponents) {
        for (const rule of owner.state.template.grapple_rescue_rules || []) {
          for (const target of allies) {
            if (eligible(helper, target, owner, rule)) choices.push({owner, target, rule});
          }
        }
      }
      choices.sort((a, b) =>
        a.target.state.current_hp - b.target.state.current_hp
        || a.target.combatant_id.localeCompare(b.target.combatant_id)
        || a.owner.combatant_id.localeCompare(b.owner.combatant_id));
      return choices[0] || null;
    } catch (error) {
      console.error("Unable to choose source-linked helper rescue.", error);
      throw error;
    }
  }

  function resolve(sequence, round, helper, target, owner, rule, setup) {
    try {
      if (!eligible(helper, target, owner, rule))
        throw new Error("Helper rescue target, source, or Action is illegal.");
      const ability = rule.check_ability;
      const poisonOrFear = C().has(helper.state, "poisoned")
        || C().has(helper.state, "frightened", setup) ? 1 : 0;
      const mode = A().mode(helper.state, 0, poisonOrFear, {member: helper, setup});
      let check = R().d20(
        X().abilityCheckBonus(helper.state, ability)
          + (window.IRON_PIT_BROWSER_EXHAUSTION?.d20Modifier(helper.state) || 0),
        mode,
      );
      const result = A().resolve(helper.state, ability, check, rule.check_dc,
        {roller: helper, setup, round});
      check = result.roll;
      const success = result.succeeded;
      E().spend(helper.state, rule.action_cost);
      const before = new Set(target.state.active_effect_ids);
      if (success) window.IRON_PIT_BROWSER_GRAPPLE.release(
        target.state, owner.combatant_id);
      const removed = [...before].filter(
        (id) => !target.state.active_effect_ids.includes(id));
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: helper.combatant_id, actor_name: helper.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: rule.source_action_id, animation: "escape-check",
        ability_check_roll: check, check_ability: ability, check_dc: rule.check_dc,
        check_succeeded: success, removed_condition_ids: removed,
        description: `${helper.state.template.name} uses an Action to pull `
          + `${target.state.template.name} out of ${owner.state.template.name}'s `
          + `${rule.source_name}; ${ability} DC ${rule.check_dc} `
          + (success ? "succeeds." : "fails."),
      };
    } catch (error) {
      console.error("Source-linked helper rescue failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRAPPLE_HELPER_RESCUE = {eligible, choose, resolve};
})();