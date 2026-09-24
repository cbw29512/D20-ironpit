(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function apply(state, original, dc, testKind) {
    try {
      if (original.total >= dc) return { roll: original, featureId: null, sourceName: null };
      for (const grant of state.template.failed_d20_bonus_die_grants || []) {
        if (!(grant.test_kinds || []).includes(testKind)) continue;
        const available = state.resources?.[grant.resource_id];
        if (available == null) {
          throw new Error(`Failed-D20 bonus ${grant.source_id} references missing resource ${grant.resource_id}.`);
        }
        const cost = grant.resource_cost || 1;
        if (available < cost) continue;
        const bonus = D().roll(grant.dice_size);
        const replacementRolls = [...(original.rolls || []), bonus];
        const replacementTotal = original.total + bonus;
        const revision = {
          source_effect_id: grant.source_id,
          kind: "additive_die",
          original_rolls: [...(original.rolls || [])],
          replacement_rolls: replacementRolls,
          original_modifier: original.modifier || 0,
          replacement_modifier: original.modifier || 0,
          original_selected: original.selected_roll ?? null,
          replacement_selected: original.selected_roll ?? null,
          original_total: original.total,
          replacement_total: replacementTotal,
          accepted: "replacement",
          replaced_die_index: null,
        };
        state.resources[grant.resource_id] -= cost;
        return {
          roll: {
            ...original,
            notation: `${original.notation} + 1d${grant.dice_size} [${grant.source_name}]`,
            rolls: replacementRolls,
            total: replacementTotal,
            revisions: [...(original.revisions || []), revision],
          },
          featureId: grant.source_id,
          sourceName: grant.source_name,
        };
      }
      return { roll: original, featureId: null, sourceName: null };
    } catch (error) {
      console.error("Failed browser D20 bonus die.", { combatant: state?.template?.name, testKind, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_D20_BONUS_DIE = { apply };
})();
