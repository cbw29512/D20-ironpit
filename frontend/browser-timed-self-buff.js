(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function canActivate(member) {
    const rule = member.state.template?.timed_self_buff;
    if (!rule || !E().available(member.state, "action")) return false;
    if ((member.state.timed_effects || []).some((item) => item.source_effect_id === rule.source_id)) return false;
    return (member.state.resources?.[rule.resource_id] || 0) >= (rule.resource_cost || 1);
  }

  function resolve(sequence, round, member) {
    try {
      if (!canActivate(member)) return null;
      const state = member.state, rule = state.template.timed_self_buff;
      state.resources[rule.resource_id] -= rule.resource_cost || 1;
      E().spend(state, "action");
      const expiresRound = round + rule.duration_rounds;
      for (const effectId of rule.effect_ids || []) {
        T().apply(state, effectId, member.combatant_id, {
          sourceEffectId: rule.source_id, appliedRound: round,
          expiresRound, expiryTiming: "source_turn_start",
        });
      }
      for (const damageType of rule.damage_resistances || []) {
        M().add(state, {
          id: `${member.combatant_id}:${rule.source_id}:resistance:${damageType}`,
          source_id: member.combatant_id, source_effect_id: rule.source_id,
          kind: "damage-resistance", damage_type: damageType,
        });
      }
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: state.template.name,
        target_id: member.combatant_id, target_name: state.template.name,
        feature_id: rule.source_id, resource_remaining: state.resources[rule.resource_id],
        animation: "buff",
        description: `${state.template.name} activates ${rule.source_id.replaceAll("-", " ")}.`,
      };
    } catch (error) {
      console.error("Browser timed self-buff failed", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFF = { canActivate, resolve };
})();
