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

  function applySkillMinimum(state, skillId, roll) {
    try {
      const rules = (state.template.skill_check_d20_minimums || [])
        .filter((rule) => (rule.skill_ids || []).includes(skillId))
        .sort((a, b) => b.minimum_roll - a.minimum_roll || a.source_id.localeCompare(b.source_id));
      if (!rules.length) return roll;
      if (!Number.isInteger(roll.selected_roll)) throw new Error("Skill-check d20 minimum requires a selected d20 roll.");
      const rule = rules[0];
      if (roll.selected_roll >= rule.minimum_roll) return roll;
      const replacementRolls = (roll.rolls || []).map((value) => Math.max(value, rule.minimum_roll));
      const replacementSelected = rule.minimum_roll;
      const replacementTotal = replacementSelected + (roll.modifier || 0);
      const revision = {
        source_effect_id: rule.source_id, kind: "die_replacement",
        original_rolls: [...(roll.rolls || [])], replacement_rolls: replacementRolls,
        original_modifier: roll.modifier || 0, replacement_modifier: roll.modifier || 0,
        original_selected: roll.selected_roll, replacement_selected: replacementSelected,
        original_total: roll.total, replacement_total: replacementTotal,
        accepted: "replacement", replaced_die_index: null,
      };
      return {
        ...roll, rolls: replacementRolls, selected_roll: replacementSelected, total: replacementTotal,
        notation: `${roll.notation} [${rule.source_id}]`,
        revisions: [...(roll.revisions || []), revision],
      };
    } catch (error) {
      console.error("Browser skill-check d20 minimum failed", { skillId, combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ABILITY_CHECKS = { applyMinimum, applySkillMinimum };
})();
