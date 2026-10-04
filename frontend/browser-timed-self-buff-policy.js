(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;

  function active(member, action) {
    try {
      return (member.state.timed_effects || []).some((effect) =>
        effect.source_id === member.combatant_id && effect.source_effect_id === action.id);
    } catch (error) {
      console.error("Timed self-buff activity lookup failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function friendlyAuraRelevant(member, action, setup) {
    try {
      const aura = action.friendlySaveAdvantageAura;
      if (!aura) return true;
      if (!setup) return false;
      const stateRuntime = window.IRON_PIT_BROWSER_STATE;
      const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES;
      if (!stateRuntime?.distance || !conditions?.has) {
        throw new Error("Timed friendly save-aura policy requires state distance and condition rules.");
      }
      const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
      return (allies || []).some((target) => {
        if (target.state.is_dead || !target.state.is_alive) return false;
        if (stateRuntime.distance(member, target) > aura.radius_ft) return false;
        if (aura.requires_hearing && conditions.has(target.state, "deafened")) return false;
        return (aura.required_effect_tags || []).some((tag) => conditions.has(target.state, tag));
      });
    } catch (error) {
      console.error("Timed friendly save-aura relevance check failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function hostileAuraRelevant(member, action, setup) {
    const aura = action.hostileStartTurnConditionAura;
    if (!aura) return true;
    if (!setup) return false;
    const stateRuntime = window.IRON_PIT_BROWSER_STATE;
    if (!stateRuntime?.distance) throw new Error("Timed hostile aura policy requires state distance.");
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    return (enemies || []).some((target) =>
      target.state.is_alive && !target.state.is_dead
      && stateRuntime.distance(member, target) <= aura.radius_ft);
  }

  function choose(member, setup = null, activationTiming = "action") {
    try {
      const choices = (member.state.template.timed_self_buff_actions || []).filter((action) =>
        (action.activationTiming || "action") === activationTiming
        && (activationTiming === "start_turn" || E().available(member.state, action.actionCost))
        && (action.resourceId == null || (member.state.resources[action.resourceId] || 0) >= (action.resourceCost || 1))
        && !active(member, action)
        && (!action.concentration || !member.state.concentration)
        && !(action.resourceId && String(action.resourceId).startsWith("spell-slot-")
          && setup && window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(member, setup))
        && friendlyAuraRelevant(member, action, setup)
        && hostileAuraRelevant(member, action, setup));
      choices.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return choices[0] || null;
    } catch (error) {
      console.error("Timed self-buff choice failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY = { active, choose };
})();
