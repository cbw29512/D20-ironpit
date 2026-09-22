(() => {
  "use strict";

  function selectedIndex(roll) {
    if (!roll?.rolls?.length || roll.selected_roll == null) throw new Error("Failed D20 override requires a selected d20 roll.");
    if (roll.mode === "advantage") return roll.rolls[0] >= roll.rolls[1] ? 0 : 1;
    if (roll.mode === "disadvantage") return roll.rolls[0] <= roll.rolls[1] ? 0 : 1;
    return 0;
  }

  function apply(state, roll, failed, testKind) {
    try {
      if (!failed || !roll) return { roll, featureId: null, sourceName: null };
      for (const grant of state.template?.failed_d20_test_override_grants || []) {
        if (!(grant.test_kinds || []).includes(testKind)) continue;
        const remaining = state.resources?.[grant.resource_id];
        if (remaining == null) throw new Error(`Failed-D20 override ${grant.source_id} references missing resource ${grant.resource_id}.`);
        if (remaining <= 0) continue;

        const index = selectedIndex(roll), replacement = grant.replacement_roll ?? 20;
        const replacementRolls = [...roll.rolls];
        replacementRolls[index] = replacement;
        const replacementTotal = roll.total - roll.selected_roll + replacement;
        const revision = {
          source_effect_id: grant.source_id, kind: "die_replacement",
          original_rolls: [...roll.rolls], replacement_rolls: replacementRolls,
          original_modifier: roll.modifier || 0, replacement_modifier: roll.modifier || 0,
          original_selected: roll.selected_roll, replacement_selected: replacement,
          original_total: roll.total, replacement_total: replacementTotal,
          accepted: "replacement", replaced_die_index: index,
        };
        state.resources[grant.resource_id] -= 1;
        return {
          roll: { ...roll, rolls: replacementRolls, selected_roll: replacement,
            total: replacementTotal, revisions: [...(roll.revisions || []), revision] },
          featureId: grant.source_id, sourceName: grant.source_name,
        };
      }
      return { roll, featureId: null, sourceName: null };
    } catch (error) {
      console.error("Failed browser D20 Test override", { error, combatant: state?.template?.name, testKind });
      throw error;
    }
  }

  function sourceNameForRoll(state, roll) {
    const revision = [...(roll?.revisions || [])].reverse().find((item) =>
      (state.template?.failed_d20_test_override_grants || []).some((grant) => grant.source_id === item.source_effect_id));
    if (!revision) return null;
    const grant = (state.template.failed_d20_test_override_grants || []).find((item) => item.source_id === revision.source_effect_id);
    return grant?.source_name || revision.source_effect_id;
  }

  window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE = { apply, sourceNameForRoll };
})();
