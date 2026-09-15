(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  const activeAction = (state) => (state.template.self_buff_actions || [])
    .find((action) => state.active_buff_effect_ids?.includes(action.id)) || null;
  const resourceAvailable = (state, action) => (state.resources?.[action.resourceId] || 0) >= (action.resourceCost || 1);

  function activateReady(sequence, round, member) {
    const state = member.state;
    const action = (state.template.self_buff_actions || []).find((item) => !state.active_buff_effect_ids?.includes(item.id) && resourceAvailable(state, item));
    if (!action || !E().available(state, "action")) return null;
    E().spend(state, "action"); state.resources[action.resourceId] -= action.resourceCost || 1;
    state.active_buff_effect_ids ||= []; state.active_buff_effect_ids.push(action.id);
    state.active_self_buff_expiry_rounds ||= {}; const expiry = round + (action.durationSourceTurns || 1);
    state.active_self_buff_expiry_rounds[action.id] = expiry;
    if (action.armorClassBonus) M().add(state, {
      id: `${member.combatant_id}:${action.id}:ac`, source_id: member.combatant_id, source_effect_id: action.id,
      kind: "armor-class", flat_bonus: action.armorClassBonus, expires_source_turn_end_round: expiry,
    });
    return { handled: true, sequence: sequence + 1, events: [{ sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: state.template.name, feature_id: action.id,
      resource_remaining: state.resources[action.resourceId], applied_condition_ids: [action.id], animation: "feature",
      description: `${state.template.name} uses ${action.name} until the end of its next turn.` }] };
  }

  function saveAdvantage(state, ability) {
    const action = activeAction(state);
    return action?.saveAdvantageAbilities?.includes(ability) ? 1 : 0;
  }

  function finish(sequence, round, member, setup, turnKey) {
    const events = [], state = member.state, action = activeAction(state);
    if (action?.bonusActionAttackId && E().available(state, "bonus_action")) {
      const choice = F().chooseAttack(member, setup, [action.bonusActionAttackId]);
      if (choice) {
        E().spend(state, "bonus_action");
        events.push(A().resolveAttack(sequence++, round, member, choice.target, choice.attack, choice.distance, {
          spendAction: false, featureId: action.id, turnKey, setup,
        }));
      }
    }
    const expiry = state.active_self_buff_expiry_rounds || {};
    for (const [effectId, expiryRound] of Object.entries(expiry)) if (expiryRound <= round) {
      state.active_buff_effect_ids = (state.active_buff_effect_ids || []).filter((id) => id !== effectId); delete expiry[effectId];
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: state.template.name, feature_id: effectId, removed_condition_ids: [effectId], animation: "feature",
        description: `${state.template.name}'s ${effectId.replaceAll("-", " ")} ends.` });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SELF_BUFFS = { activateReady, finish, saveAdvantage };
})();
