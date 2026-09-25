(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
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
      const active = target.state.active_d20_bonus_dice || (target.state.active_d20_bonus_dice = []);
      if (active.some((item) => item.source_id === source.combatant_id && item.source_effect_id === action.id)) {
        throw new Error(target.state.template.name + " already has " + action.name + " from this source.");
      }
      E().spend(source.state, action.actionCost);
      resources[action.resourceId] -= action.resourceCost || 1;
      active.push({
        source_id: source.combatant_id,
        source_effect_id: action.id,
        source_name: action.name,
        dice_count: action.diceCount || 1,
        dice_size: action.diceSize,
        test_kinds: [...action.testKinds],
        applied_round: round,
        expires_round: round + action.durationRounds,
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
      const active = state.active_d20_bonus_dice || [];
      const index = active.indexOf(grant);
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

  window.IRON_PIT_BROWSER_D20_BONUS_DICE = { consume, eligible, expire, resolveGrant, targetAllowed };
})();
