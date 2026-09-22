(() => {
  "use strict";

  const STATE = () => window.IRON_PIT_BROWSER_STATE;
  const CONDITIONS = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => Boolean(state.is_unconscious),
  };
  const DICE = () => window.IRON_PIT_DICE;

  const active = (member) => member.state.is_alive && !member.state.is_dead
    && member.state.current_hp > 0 && !CONDITIONS().incapacitated(member.state);

  function candidates(roller, setup, succeeded) {
    const desiredSide = succeeded
      ? (roller.side === "heroes" ? "monsters" : "heroes")
      : roller.side;
    return [...setup.heroes, ...setup.monsters]
      .filter((member) => {
        const rule = member.state.template.d20_outcome_adjustment;
        return member.side === desiredSide && rule && active(member)
          && (member.state.resources?.[rule.resource_id] || 0) > 0
          && STATE().distance(member, roller) <= rule.range_ft;
      })
      .sort((left, right) =>
        STATE().distance(left, roller) - STATE().distance(right, roller)
        || left.combatant_id.localeCompare(right.combatant_id));
  }

  function reversalGap(total, targetNumber, succeeded) {
    return succeeded ? total - targetNumber + 1 : targetNumber - total;
  }

  function adjust(roll, succeeded, targetNumber, roller, setup, options = {}) {
    try {
      if (!setup || options.outcomeLocked) return { roll, succeeded, sourceId: null };
      for (const source of candidates(roller, setup, succeeded)) {
        const rule = source.state.template.d20_outcome_adjustment;
        const gap = reversalGap(roll.total, targetNumber, succeeded);
        if (gap <= 0 || gap > rule.dice_count * rule.dice_size) continue;
        const adjustmentRolls = DICE().rollMany(rule.dice_count, rule.dice_size);
        const sign = succeeded ? -1 : 1;
        const replacementTotal = roll.total + sign * adjustmentRolls.reduce((sum, value) => sum + value, 0);
        source.state.resources[rule.resource_id] -= 1;
        const revision = {
          source_effect_id: rule.source_id,
          kind: "total_adjustment",
          original_rolls: [...(roll.rolls || [])],
          replacement_rolls: [...(roll.rolls || [])],
          original_modifier: roll.modifier || 0,
          replacement_modifier: roll.modifier || 0,
          original_selected: roll.selected_roll ?? null,
          replacement_selected: roll.selected_roll ?? null,
          original_total: roll.total,
          replacement_total: replacementTotal,
          accepted: "replacement",
          replaced_die_index: null,
          adjustment_rolls: adjustmentRolls,
          adjustment_sign: sign,
        };
        const updated = {
          ...roll,
          notation: `${roll.notation} [${rule.source_id} ${sign > 0 ? "+" : "-"}${rule.dice_count}d${rule.dice_size}]`,
          total: replacementTotal,
          revisions: [...(roll.revisions || []), revision],
        };
        return { roll: updated, succeeded: replacementTotal >= targetNumber, sourceId: source.combatant_id };
      }
      return { roll, succeeded, sourceId: null };
    } catch (error) {
      console.error("Browser D20 outcome adjustment failed", {
        roller: roller?.combatant_id, targetNumber, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS = { adjust, candidates, reversalGap };
})();
