(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const O = () => window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function needsDash(member, setup, turnKey) {
    if (!member?.state?.template?.cunning_action || !E().available(member.state, "bonus_action")) return false;
    const speed = M().effectiveSpeed(member.state);
    if (!(speed > 0)) return false;
    const normalMove = member.state.movement_remaining_ft;
    let dashWouldHelp = false;
    for (const target of F().targetOrder(member, setup)) {
      const distance = S().distance(member, target);
      for (const option of O().rangesForTarget(member, target, turnKey)) {
        if (distance <= option.range + normalMove) return false;
        if (distance <= option.range + normalMove + speed) dashWouldHelp = true;
      }
    }
    return dashWouldHelp;
  }

  function useDash(sequence, round, member, setup, turnKey) {
    if (!needsDash(member, setup, turnKey)) return null;
    E().spend(member.state, "bonus_action");
    member.state.movement_remaining_ft += M().effectiveSpeed(member.state);
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      feature_id: "cunning-action-dash", animation: "movement",
      description: `${member.state.template.name} uses Cunning Action to Dash.`,
    };
  }

  window.IRON_PIT_BROWSER_CUNNING_ACTION = { needsDash, useDash };
})();
