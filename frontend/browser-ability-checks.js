(() => {
  "use strict";

  function applyMinimum(state, ability, roll) {
    try {
      const rules = (state.template.ability_check_minimums || []).filter((rule) => rule.ability === ability);
      if (!rules.length) return roll;
      const score = state.template.ability_scores?.[ability];
      if (!Number.isInteger(score)) {
        throw new Error(`${state.template.name} has an ability-check minimum without a certified ${ability} score.`);
      }
      if (roll.total >= score) return roll;
      const rule = [...rules].sort((a, b) => a.source_id.localeCompare(b.source_id))[0];
      const revision = {
        source_effect_id: rule.source_id, kind: "total_replacement",
        original_rolls: [...(roll.rolls || [])], replacement_rolls: [...(roll.rolls || [])],
        original_modifier: roll.modifier || 0, replacement_modifier: roll.modifier || 0,
        original_selected: roll.selected_roll ?? null, replacement_selected: roll.selected_roll ?? null,
        original_total: roll.total, replacement_total: score, accepted: "replacement", replaced_die_index: null,
      };
      return { ...roll, notation: `${roll.notation} [${rule.source_id}]`, total: score,
        revisions: [...(roll.revisions || []), revision] };
    } catch (error) {
      console.error("Browser ability-check minimum failed", { ability, combatant: state?.template?.name, error });
      throw error;
    }
  }

  function resolve(state, ability, roll, dc) {
    try {
      let revised = applyMinimum(state, ability, roll);
      revised = window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE?.apply(
        state, revised, revised.total < dc, "ability_check",
      ).roll || revised;
      return { roll: revised, succeeded: revised.total >= dc };
    } catch (error) {
      console.error("Browser ability-check outcome failed", { ability, combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ABILITY_CHECKS = { applyMinimum, resolve };
})();
