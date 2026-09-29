(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function members(setup) {
    if (!setup) throw new Error("D20 outcome adjustment requires encounter setup.");
    return [...(setup.heroes || []), ...(setup.monsters || [])];
  }

  function eligible(source, roller, rule, testKind) {
    if (!source?.state?.is_alive || source.state.is_dead) return false;
    if (!(rule.test_kinds || []).includes(testKind)) return false;
    if (!R()?.available(source.state, rule.resource_id, rule.resource_cost || 1)) return false;
    return S().distance(source, roller) <= (rule.range_ft ?? 60);
  }

  function direction(source, roller, rule, roll, threshold) {
    const maximum = (rule.dice_count || 1) * (rule.dice_size || 4);
    const allied = source.side === roller.side;
    if (allied && rule.can_add !== false && roll.total < threshold && roll.total + maximum >= threshold) {
      return "add";
    }
    if (!allied && rule.can_subtract !== false && roll.total >= threshold && roll.total - maximum < threshold) {
      return "subtract";
    }
    return null;
  }

  function applyIfUseful(roller, setup, testKind, roll, threshold, naturalAttackRoll = null) {
    try {
      if (!roller?.state || !roll) throw new Error("D20 outcome adjustment requires a roller and roll.");
      if (!Number.isFinite(threshold)) throw new Error("D20 outcome adjustment requires a numeric threshold.");
      if (testKind === "attack" && [1, 20].includes(naturalAttackRoll)) {
        return { roll, featureId: null, sourceName: null, adjustmentTotal: 0, direction: null };
      }

      const choices = [];
      for (const source of members(setup)) {
        for (const rule of source.state.template.resource_backed_d20_outcome_adjustments || []) {
          if (!eligible(source, roller, rule, testKind)) continue;
          const mode = direction(source, roller, rule, roll, threshold);
          if (!mode) continue;
          choices.push({ source, rule, mode });
        }
      }
      if (!choices.length) {
        return { roll, featureId: null, sourceName: null, adjustmentTotal: 0, direction: null };
      }

      choices.sort((a, b) =>
        ((b.rule.dice_count || 1) * (b.rule.dice_size || 4))
          - ((a.rule.dice_count || 1) * (a.rule.dice_size || 4))
        || S().distance(a.source, roller) - S().distance(b.source, roller)
        || a.source.combatant_id.localeCompare(b.source.combatant_id)
        || a.rule.source_id.localeCompare(b.rule.source_id)
      );
      const { source, rule, mode } = choices[0];
      const diceCount = rule.dice_count || 1;
      const diceSize = rule.dice_size || 4;
      const adjustmentRolls = Array.from({ length: diceCount }, () => D().roll(diceSize));
      const adjustmentTotal = adjustmentRolls.reduce((sum, value) => sum + value, 0);
      const signed = mode === "add" ? adjustmentTotal : -adjustmentTotal;
      const total = roll.total + signed;
      const remaining = R().spend(source.state, rule.resource_id, rule.resource_cost || 1);

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
        replacement_total: total,
        accepted: "replacement",
        replaced_die_index: null,
      };
      return {
        roll: {
          ...roll,
          notation: `${roll.notation} ${mode === "add" ? "+" : "-"} ${diceCount}d${diceSize} [${rule.source_name}]`,
          rolls: [...(roll.rolls || []), ...adjustmentRolls],
          modifier: (roll.modifier || 0) + signed,
          total,
          revisions: [...(roll.revisions || []), revision],
        },
        featureId: rule.source_id,
        sourceName: rule.source_name,
        adjustmentTotal,
        direction: mode,
        resourceRemaining: remaining,
        sourceId: source.combatant_id,
      };
    } catch (error) {
      console.error("Browser D20 outcome adjustment failed", {
        roller: roller?.combatant_id,
        testKind,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS = { applyIfUseful };
})();
