(() => {
  "use strict";

  function apply(state, roll, failed, testKind) {
    try {
      if (!failed) return { roll, featureId: null, sourceName: null };
      const rules = [...(state.template.failed_d20_test_replacements || [])]
        .filter((rule) => (rule.test_kinds || []).includes(testKind))
        .sort((a, b) => a.source_id.localeCompare(b.source_id));
      for (const rule of rules) {
        if (state.resources?.[rule.resource_id] == null) {
          throw new Error(`${rule.source_name} references missing resource ${rule.resource_id}.`);
        }
        if (state.resources[rule.resource_id] <= 0) continue;
        if (!Number.isInteger(roll.selected_roll)) {
          throw new Error(`${rule.source_name} requires a selected d20 roll.`);
        }
        const d20Count = roll.mode === "normal" ? 1 : 2;
        const replacementRolls = [...roll.rolls];
        const selectedIndex = replacementRolls.slice(0, d20Count)
          .findIndex((value) => value === roll.selected_roll);
        if (selectedIndex < 0) {
          throw new Error(`${rule.source_name} could not locate the selected d20 in roll evidence.`);
        }
        const replacement = rule.replacement_roll ?? 20;
        replacementRolls[selectedIndex] = replacement;
        const replacementTotal = roll.total - roll.selected_roll + replacement;
        const revision = {
          source_effect_id: rule.source_id,
          kind: "die_replacement",
          original_rolls: [...roll.rolls],
          replacement_rolls: [...replacementRolls],
          original_modifier: roll.modifier || 0,
          replacement_modifier: roll.modifier || 0,
          original_selected: roll.selected_roll,
          replacement_selected: replacement,
          original_total: roll.total,
          replacement_total: replacementTotal,
          accepted: "replacement",
          replaced_die_index: selectedIndex,
        };
        state.resources[rule.resource_id] -= 1;
        return {
          featureId: rule.source_id,
          sourceName: rule.source_name,
          roll: {
            ...roll,
            notation: `${roll.notation} [${rule.source_name}]`,
            rolls: replacementRolls,
            selected_roll: replacement,
            total: replacementTotal,
            revisions: [...(roll.revisions || []), revision],
          },
        };
      }
      return { roll, featureId: null, sourceName: null };
    } catch (error) {
      console.error("Failed browser D20 Test replacement", { error, testKind });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_D20_REPLACEMENT = { apply };
})();
