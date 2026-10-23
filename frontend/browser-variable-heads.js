(() => {
  "use strict";

  const profile = (state) => state.template.variableHeads || null;

  function initialize(state) {
    const rule = profile(state);
    state.current_heads = rule ? rule.initialHeads : null;
    state.heads_lost_since_owner_turn = 0;
    state.head_regrowth_blocked = false;
    refreshOpportunityReactions(state);
  }

  function refreshOpportunityReactions(state) {
    const rule = profile(state);
    state.opportunity_reactions_remaining = rule?.extraOpportunityReactionsPerHeadBeyondOne
      ? Math.max(0, (state.current_heads || 0) - 1) : 0;
  }

  function opportunityReactionAvailable(state) {
    return Boolean(state.reaction_available || state.opportunity_reactions_remaining > 0);
  }

  function spendOpportunityReaction(state) {
    if (state.reaction_available) state.reaction_available = false;
    else if (state.opportunity_reactions_remaining > 0) state.opportunity_reactions_remaining -= 1;
    else throw new Error("No Opportunity Attack reaction remains.");
  }

  function noteDamage(state, before) {
    const rule = profile(state);
    if (!rule || !(state.current_heads > 0)) return false;
    const after = state.damage_taken_this_turn_by_type || {};
    if (rule.regrowthBlockingDamageTypes.some((kind) => (after[kind] || 0) > (before[kind] || 0))) {
      state.head_regrowth_blocked = true;
    }
    const beforeTotal = Object.values(before).reduce((a, b) => a + Number(b), 0);
    const afterTotal = Object.values(after).reduce((a, b) => a + Number(b), 0);
    if (beforeTotal < rule.severDamageThreshold && afterTotal >= rule.severDamageThreshold) {
      state.current_heads -= 1;
      state.heads_lost_since_owner_turn += 1;
      state.opportunity_reactions_remaining = Math.min(
        state.opportunity_reactions_remaining, Math.max(0, state.current_heads - 1));
      return state.current_heads === 0;
    }
    return false;
  }

  function endOwnerTurn(state) {
    const rule = profile(state);
    if (!rule) return { grown: 0, healed: 0 };
    let grown = 0, healed = 0;
    if (!state.is_dead && state.current_heads > 0 && state.heads_lost_since_owner_turn > 0
      && !state.head_regrowth_blocked) {
      grown = state.heads_lost_since_owner_turn * rule.headsPerRegrowth;
      state.current_heads += grown;
      if (!(state.timed_effects || []).some((effect) => effect.cannot_regain_hit_points)) {
        const maximum = window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state);
        healed = Math.max(0, Math.min(maximum, state.current_hp + grown * rule.healingPerRegrownHead) - state.current_hp);
        state.current_hp += healed;
      }
    }
    state.heads_lost_since_owner_turn = 0;
    state.head_regrowth_blocked = false;
    return { grown, healed };
  }


  function headsSaveAdvantage(state, conditionId) {
    const rule = profile(state);
    if (!rule || !conditionId || !(state.current_heads > 1)) return false;
    const list = (rule.saveAdvantageConditions || []).map(c => String(c).toLowerCase());
    return list.includes(String(conditionId).toLowerCase());
  }

  window.IRON_PIT_BROWSER_VARIABLE_HEADS = {
    endOwnerTurn, initialize, noteDamage, opportunityReactionAvailable,
    refreshOpportunityReactions, spendOpportunityReaction, headsSaveAdvantage,
  };
})();