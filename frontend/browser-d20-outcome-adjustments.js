(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const D = () => window.IRON_PIT_DICE;

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function distance(source, roller, rangeFt) {
    const formation = F();
    if (!formation?.saveDistance) throw new Error("D20 outcome adjustment requires formation distance.");
    return formation.saveDistance(source, roller, rangeFt);
  }

  function direction(source, roller, rule, roll, targetTotal) {
    const maximum = (rule.dice_count || 1) * (rule.dice_size || 4);
    const allied = source.side === roller.side;
    if (allied && rule.can_add !== false && roll.total < targetTotal
        && roll.total + maximum >= targetTotal) return "add";
    if (!allied && rule.can_subtract !== false && roll.total >= targetTotal
        && roll.total - maximum < targetTotal) return "subtract";
    return null;
  }

  function applyIfUseful(roller, setup, testKind, roll, targetTotal, options = {}) {
    try {
      if (!roller || !setup || !roll) return { roll, sourceId: null, sourceName: null };
      if (testKind === "attack" && [1, 20].includes(options.naturalAttackRoll)) {
        return { roll, sourceId: null, sourceName: null };
      }

      const choices = [];
      for (const source of members(setup)) {
        if (!source.state?.is_alive || source.state?.is_dead) continue;
        for (const rule of source.state.template.resource_backed_d20_outcome_adjustments || []) {
          if (!(rule.test_kinds || []).includes(testKind)) continue;
          if (!R()?.available(source.state, rule.resource_id, rule.resource_cost || 1)) continue;
          if (distance(source, roller, rule.range_ft || 0) > (rule.range_ft || 0)) continue;
          const useDirection = direction(source, roller, rule, roll, targetTotal);
          if (useDirection) choices.push({ source, rule, direction: useDirection });
        }
      }
      if (!choices.length) return { roll, sourceId: null, sourceName: null };

      choices.sort((a, b) =>
        ((b.rule.dice_count || 1) * (b.rule.dice_size || 4))
          - ((a.rule.dice_count || 1) * (a.rule.dice_size || 4))
        || distance(a.source, roller, a.rule.range_ft || 0)
          - distance(b.source, roller, b.rule.range_ft || 0)
        || a.source.combatant_id.localeCompare(b.source.combatant_id)
        || a.rule.source_id.localeCompare(b.rule.source_id)
      );
      const { source, rule, direction: useDirection } = choices[0];
      const count = rule.dice_count || 1, sides = rule.dice_size || 4;
      const adjustmentRolls = Array.from({ length: count }, () => D().roll(sides));
      const adjustment = adjustmentRolls.reduce((sum, value) => sum + value, 0);
      const signed = useDirection === "add" ? adjustment : -adjustment;
      const remaining = R().spend(source.state, rule.resource_id, rule.resource_cost || 1);
      const replacementTotal = roll.total + signed;
      const revision = {
        source_effect_id: rule.source_id,
        kind: "roll_adjustment",
        original_rolls: [...(roll.rolls || [])],
        replacement_rolls: [...(roll.rolls || []), ...adjustmentRolls],
        original_modifier: roll.modifier || 0,
        replacement_modifier: (roll.modifier || 0) + signed,
        original_selected: roll.selected_roll ?? null,
        replacement_selected: roll.selected_roll ?? null,
        original_total: roll.total,
        replacement_total: replacementTotal,
        accepted: "replacement",
        replaced_die_index: null,
      };
      const operator = useDirection === "add" ? "+" : "-";
      return {
        roll: {
          ...roll,
          notation: `${roll.notation} ${operator} ${count}d${sides} [${rule.source_name}]`,
          rolls: [...(roll.rolls || []), ...adjustmentRolls],
          modifier: (roll.modifier || 0) + signed,
          total: replacementTotal,
          revisions: [...(roll.revisions || []), revision],
        },
        sourceId: rule.source_id,
        sourceName: rule.source_name,
        adjustmentTotal: adjustment,
        direction: useDirection,
        resourceRemaining: remaining,
      };
    } catch (error) {
      console.error("Browser D20 outcome adjustment failed", {
        roller: roller?.combatant_id, testKind, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS = { applyIfUseful };
})();
