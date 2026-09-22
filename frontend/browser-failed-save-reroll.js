(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;

  function d20Count(mode) {
    return mode === "normal" ? 1 : 2;
  }

  function apply(state, original) {
    try {
      for (const grant of state.template.failed_save_reroll_grants || []) {
        const available = state.resources?.[grant.resource_id];
        if (available == null) {
          throw new Error(`Failed-save reroll ${grant.source_id} references missing resource ${grant.resource_id}.`);
        }
        const cost = grant.resource_cost || 1;
        if (available < cost) continue;

        const count = d20Count(original.mode);
        const retained = (original.rolls || []).slice(count);
        const replacementBase = R().d20(original.modifier || 0, original.mode || "normal");
        const replacementRolls = [...replacementBase.rolls, ...retained];
        const replacementTotal = replacementBase.total + retained.reduce((sum, value) => sum + value, 0);
        const revision = {
          source_effect_id: grant.source_id,
          kind: "full_reroll",
          original_rolls: [...(original.rolls || [])],
          replacement_rolls: replacementRolls,
          original_modifier: original.modifier || 0,
          replacement_modifier: original.modifier || 0,
          original_selected: original.selected_roll,
          replacement_selected: replacementBase.selected_roll,
          original_total: original.total,
          replacement_total: replacementTotal,
          accepted: "replacement",
          replaced_die_index: null,
        };
        state.resources[grant.resource_id] -= cost;
        return {
          roll: {
            ...original,
            notation: `${original.notation} [${grant.source_name}]`,
            rolls: replacementRolls,
            selected_roll: replacementBase.selected_roll,
            total: replacementTotal,
            revisions: [...(original.revisions || []), revision],
          },
          featureId: grant.source_id,
          sourceName: grant.source_name,
        };
      }
      return { roll: original, featureId: null, sourceName: null };
    } catch (error) {
      console.error("Failed browser failed-save reroll", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL = { apply };
})();
