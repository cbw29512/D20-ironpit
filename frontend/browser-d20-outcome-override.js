(() => {
  "use strict";

  function available(state) {
    const resourceId = state?.template?.failed_d20_to_natural_20_resource_id;
    return Boolean(resourceId) && (state.resources?.[resourceId] || 0) > 0;
  }

  function apply(state, roll, dc) {
    try {
      const resourceId = state?.template?.failed_d20_to_natural_20_resource_id;
      if (!resourceId || !roll || roll.total >= dc || !available(state)) return { roll, used: false };
      const selected = roll.selected_roll;
      if (!Number.isInteger(selected)) return { roll, used: false };
      const total = roll.total + (20 - selected);
      const revision = {
        source_effect_id: resourceId,
        kind: "selected_die_replacement",
        original_rolls: [...(roll.rolls || [])],
        replacement_rolls: [...(roll.rolls || [])],
        original_modifier: roll.modifier || 0,
        replacement_modifier: roll.modifier || 0,
        original_selected: selected,
        replacement_selected: 20,
        original_total: roll.total,
        replacement_total: total,
        accepted: "replacement",
        replaced_die_index: null,
      };
      state.resources[resourceId] -= 1;
      return {
        used: true,
        roll: {
          ...roll,
          selected_roll: 20,
          total,
          notation: `${roll.notation} [${resourceId}]`,
          revisions: [...(roll.revisions || []), revision],
        },
      };
    } catch (error) {
      console.error("Failed browser D20 outcome override", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_D20_OVERRIDE = { apply, available };
})();
