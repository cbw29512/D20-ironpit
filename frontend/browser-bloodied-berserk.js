(() => {
  "use strict";
  const D = () => window.IRON_PIT_DICE, S = () => window.IRON_PIT_BROWSER_STATE;
  const bloodied = (state) => state.current_hp * 2 <= S().effectiveMaxHp(state);

  function startTurn(sequence, round, member) {
    try {
      const rule = member.state.template.bloodied_berserk_rule;
      if (!rule) return { event: null, sequence };
      if (!bloodied(member.state)) {
        member.state.active_berserk_rule_id = null;
        return { event: null, sequence };
      }
      const roll = D().roll(rule.dieSize);
      const activated = roll >= rule.triggerMinimum && member.state.active_berserk_rule_id !== rule.id;
      if (roll >= rule.triggerMinimum) member.state.active_berserk_rule_id = rule.id;
      return {
        event: {
          sequence, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          resource_roll: { notation: `1d${rule.dieSize}`, rolls: [roll], selected_roll: roll, modifier: 0, mode: "normal", total: roll },
          feature_id: rule.id, animation: "berserk",
          description: `${member.state.template.name} rolls ${roll} for ${rule.name}${activated ? " and goes berserk." : "."}`,
        },
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Browser Bloodied Berserk start-turn resolution failed.", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function targetOrder(member, setup) {
    try {
      const rule = member.state.template.bloodied_berserk_rule;
      if (!rule || member.state.active_berserk_rule_id !== rule.id || !bloodied(member.state)) return null;
      return [...setup.heroes, ...setup.monsters]
        .filter((target) => target.combatant_id !== member.combatant_id && target.state.is_alive && !target.state.is_dead
          && (!target.state.swallowed || !target.state.swallowed.total_cover_from_outside))
        .sort((left, right) => S().distance(member, left) - S().distance(member, right)
          || left.combatant_id.localeCompare(right.combatant_id));
    } catch (error) {
      console.error("Browser Bloodied Berserk targeting failed.", { member: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BLOODIED_BERSERK = { startTurn, targetOrder };
})();
