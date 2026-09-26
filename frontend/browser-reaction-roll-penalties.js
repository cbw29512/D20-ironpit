(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const D = () => window.IRON_PIT_DICE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    has: (state, id) => (state.active_effect_ids || []).includes(id),
  };

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function eligible(source, roller, action, rollKind) {
    if (!(action.rollKinds || []).includes(rollKind) || source.side === roller.side) return false;
    if (!E().available(source.state, "reaction")) return false;
    if ((source.state.resources?.[action.resourceId] || 0) < (action.resourceCost || 1)) return false;
    if (S().distance(source, roller) > action.range) return false;
    if (action.requiresSourceSight && (Q().has(source.state, "blinded") || Q().has(roller.state, "invisible"))) return false;
    if (action.requiresTargetHearing && Q().has(roller.state, "deafened")) return false;
    if (action.blockedTargetConditionImmunity
        && I().immune(roller.state, action.blockedTargetConditionImmunity, source.state.template)) return false;
    return true;
  }

  function canChange(action, rollKind, roll, threshold = null) {
    if (rollKind === "damage") return roll.total > 0;
    if (threshold == null || roll.total < threshold) return false;
    if (rollKind === "attack" && [1, 20].includes(roll.selected_roll)) return false;
    return roll.total - (action.diceCount || 1) * action.diceSize < threshold;
  }

  function choose(roller, setup, rollKind, roll, threshold = null) {
    try {
      const opposing = roller.side === "heroes" ? setup.monsters : setup.heroes;
      const choices = [];
      for (const source of opposing) {
        for (const action of source.state.template.reactionRollPenaltyActions || []) {
          if (eligible(source, roller, action, rollKind) && canChange(action, rollKind, roll, threshold)) {
            choices.push({ source, action });
          }
        }
      }
      choices.sort((a, b) =>
        (b.action.priority || 0) - (a.action.priority || 0)
        || ((b.action.diceCount || 1) * b.action.diceSize) - ((a.action.diceCount || 1) * a.action.diceSize)
        || S().distance(a.source, roller) - S().distance(b.source, roller)
        || a.source.combatant_id.localeCompare(b.source.combatant_id)
        || a.action.id.localeCompare(b.action.id));
      return choices[0] || null;
    } catch (error) {
      console.error("Failed browser reaction roll-penalty choice.", { combatant: roller?.combatant_id, error });
      throw error;
    }
  }

  function applyIfUseful(roller, setup, rollKind, roll, threshold = null) {
    try {
      if (!setup) return null;
      const selected = choose(roller, setup, rollKind, roll, threshold);
      if (!selected) return null;
      const { source, action } = selected;
      const count = action.diceCount || 1;
      const penaltyRolls = Array.from({ length: count }, () => D().roll(action.diceSize));
      const penalty = penaltyRolls.reduce((sum, value) => sum + value, 0);
      let replacementTotal = roll.total - penalty;
      if (rollKind === "damage") replacementTotal = Math.max(0, replacementTotal);
      E().spend(source.state, "reaction");
      source.state.resources[action.resourceId] -= action.resourceCost || 1;
      const revision = {
        source_effect_id: action.id, kind: "roll_penalty",
        original_rolls: [...(roll.rolls || [])], replacement_rolls: [...(roll.rolls || []), ...penaltyRolls],
        original_modifier: roll.modifier || 0, replacement_modifier: (roll.modifier || 0) - penalty,
        original_selected: roll.selected_roll ?? null, replacement_selected: roll.selected_roll ?? null,
        original_total: roll.total, replacement_total: replacementTotal,
        accepted: "replacement", replaced_die_index: null,
      };
      return {
        roll: {
          ...roll,
          notation: `${roll.notation} - ${count}d${action.diceSize} [${action.name}]`,
          rolls: [...(roll.rolls || []), ...penaltyRolls],
          modifier: (roll.modifier || 0) - penalty,
          total: replacementTotal,
          revisions: [...(roll.revisions || []), revision],
        },
        sourceName: source.state.template.name,
        actionId: action.id,
        penaltyTotal: penalty,
        resourceRemaining: source.state.resources[action.resourceId],
      };
    } catch (error) {
      console.error("Failed browser reaction roll penalty.", { combatant: roller?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REACTION_ROLL_PENALTIES = { applyIfUseful, choose, eligible };
})();
