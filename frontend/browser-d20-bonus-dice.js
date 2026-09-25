(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const D = () => window.IRON_PIT_DICE;

  function targetAllowed(source, target, action) {
    try {
      if (target.state.is_dead || !target.state.is_alive) return false;
      if (action.targetMode === "self" && target.combatant_id !== source.combatant_id) return false;
      if (action.targetMode === "other_ally"
          && (target.side !== source.side || target.combatant_id === source.combatant_id)) return false;
      if (action.targetMode === "ally" && target.side !== source.side) return false;
      return S().distance(source, target) <= action.range;
    } catch (error) {
      console.error("Browser d20 bonus-die target validation failed.", {
        source: source?.combatant_id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  function conflicts(source, target, action, round) {
    return (target.state.active_d20_bonus_dice || []).some((item) =>
      item.expires_round > round && (
        (item.source_id === source.combatant_id && item.source_effect_id === action.id)
        || (action.exclusiveGroup && item.exclusive_group === action.exclusiveGroup)
      ));
  }

  function attackBonus(member) {
    const template = member.state.template;
    const primary = (template.attacks || []).find((item) => item.id === template.primary_attack_id)
      || (template.attacks || [])[0];
    return primary?.bonus || 0;
  }

  function choose(source, setup, round) {
    try {
      const resources = source.state.resources || {};
      const allies = source.side === "heroes" ? setup.heroes : setup.monsters;
      const choices = [];
      for (const action of source.state.template.d20BonusDieActions || []) {
        if (!E().available(source.state, action.actionCost)
            || (resources[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
        for (const target of allies) {
          if (targetAllowed(source, target, action) && !conflicts(source, target, action, round)) {
            choices.push({ action, target });
          }
        }
      }
      choices.sort((a, b) =>
        (b.action.priority || 0) - (a.action.priority || 0)
        || Number(F().isBackline(a.target)) - Number(F().isBackline(b.target))
        || attackBonus(b.target) - attackBonus(a.target)
        || a.target.combatant_id.localeCompare(b.target.combatant_id));
      return choices[0] || null;
    } catch (error) {
      console.error("Browser d20 bonus-die support choice failed.", { source: source?.combatant_id, error });
      throw error;
    }
  }

  function resolveGrant(sequence, round, source, target, action) {
    try {
      if (!E().available(source.state, action.actionCost)) {
        throw new Error(action.actionCost + " is unavailable for " + action.name + ".");
      }
      const resources = source.state.resources || {};
      if ((resources[action.resourceId] || 0) < (action.resourceCost || 1)) {
        throw new Error("Resource " + action.resourceId + " is unavailable for " + action.name + ".");
      }
      if (!targetAllowed(source, target, action)) {
        throw new Error(target.state.template.name + " is not a legal target for " + action.name + ".");
      }
      expire(target.state, round);
      const active = target.state.active_d20_bonus_dice || (target.state.active_d20_bonus_dice = []);
      if (conflicts(source, target, action, round)) {
        throw new Error(target.state.template.name + " already has an exclusive " + action.name + " grant.");
      }
      E().spend(source.state, action.actionCost);
      resources[action.resourceId] -= action.resourceCost || 1;
      active.push({
        source_id: source.combatant_id, source_effect_id: action.id, source_name: action.name,
        dice_count: action.diceCount || 1, dice_size: action.diceSize,
        test_kinds: [...action.testKinds], exclusive_group: action.exclusiveGroup || null,
        applied_round: round, expires_round: round + action.durationRounds,
      });
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: action.id, resource_remaining: resources[action.resourceId],
        animation: action.animation || "inspiration",
        description: source.state.template.name + " grants " + action.name + " to " + target.state.template.name + ".",
      };
    } catch (error) {
      console.error("Browser d20 bonus-die grant failed.", {
        source: source?.combatant_id, target: target?.combatant_id, action: action?.id, error,
      });
      throw error;
    }
  }

  function eligible(state, testKind, round) {
    try {
      expire(state, round);
      return (state.active_d20_bonus_dice || []).filter(
        (item) => (item.test_kinds || []).includes(testKind) && item.expires_round > round,
      );
    } catch (error) {
      console.error("Browser d20 bonus-die eligibility failed.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function consume(state, grant, roll) {
    try {
      const active = state.active_d20_bonus_dice || [], index = active.indexOf(grant);
      if (index < 0) throw new Error("Selected d20 bonus-die grant is not active.");
      const bonusRolls = Array.from({ length: grant.dice_count || 1 }, () => D().roll(grant.dice_size));
      active.splice(index, 1);
      return {
        ...roll,
        notation: roll.notation + " + " + (grant.dice_count || 1) + "d" + grant.dice_size + " [" + grant.source_name + "]",
        rolls: [...(roll.rolls || []), ...bonusRolls],
        total: roll.total + bonusRolls.reduce((sum, value) => sum + value, 0),
      };
    } catch (error) {
      console.error("Browser d20 bonus-die consumption failed.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function applyIfUseful(state, testKind, roll, targetTotal, round) {
    if (roll.total >= targetTotal) return { roll, sourceName: null };
    const useful = eligible(state, testKind, round).filter(
      (grant) => roll.total + (grant.dice_count || 1) * grant.dice_size >= targetTotal);
    if (!useful.length) return { roll, sourceName: null };
    useful.sort((a, b) =>
      ((b.dice_count || 1) * b.dice_size) - ((a.dice_count || 1) * a.dice_size)
      || a.source_effect_id.localeCompare(b.source_effect_id));
    const grant = useful[0];
    return { roll: consume(state, grant, roll), sourceName: grant.source_name };
  }

  function expire(state, round) {
    try {
      const active = state.active_d20_bonus_dice || [];
      const expired = active.filter((item) => item.expires_round <= round).map((item) => item.source_effect_id);
      state.active_d20_bonus_dice = active.filter((item) => item.expires_round > round);
      return expired;
    } catch (error) {
      console.error("Browser d20 bonus-die expiry failed.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_D20_BONUS_DICE = {
    applyIfUseful, choose, consume, eligible, expire, resolveGrant, targetAllowed,
  };
})();
