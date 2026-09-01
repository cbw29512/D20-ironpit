(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;

  function resolve(sequence, round, member, setup) {
    try {
      const fraction = member.state.template.tactical_shift_fraction || 0;
      if (!(fraction > 0) || member.state.is_dead || member.state.is_unconscious || G()?.speedIsZero(member.state)) return null;
      const target = S().nearestTarget(member, setup);
      if (!target) return null;
      const before = S().distance(member, target);
      const allowance = Math.floor(member.state.template.speed_ft * fraction);
      const moved = Math.min(Math.max(0, before - 5), allowance);
      if (!(moved > 0)) return null;
      member.position_ft += (member.position_ft < target.position_ft ? 1 : -1) * moved;
      return {
        sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id,
        actor_name: member.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        distance_before_ft: before, distance_after_ft: S().distance(member, target), movement_ft: moved,
        feature_id: "tactical-shift", animation: "advance",
        description: `${member.state.template.name} uses Tactical Shift to move ${moved} feet without provoking Opportunity Attacks.`,
      };
    } catch (error) {
      console.error("Tactical Shift resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TACTICAL_SHIFT = { resolve };
})();
