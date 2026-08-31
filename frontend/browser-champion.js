(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;

  function preferredDistance(member) {
    const template = member.state.template;
    const attack = template.attacks?.find((item) => item.id === template.primary_attack_id) || template.attacks?.[0];
    if (!attack) return 5;
    return attack.kind === "melee" ? (attack.reach || 5) : (attack.normal || 5);
  }

  function criticalMove(attacker, setup, event) {
    const fraction = Number(attacker.state.template.critical_move_fraction || 0);
    if (!event.critical || !setup || fraction <= 0 || G()?.speedIsZero(attacker.state)) return event;
    const target = S().nearestTarget(attacker, setup);
    if (!target) return event;
    const before = S().distance(attacker, target), desired = preferredDistance(attacker);
    const moved = Math.min(Math.max(0, before - desired), Math.floor(attacker.state.template.speed_ft * fraction));
    if (moved <= 0) return event;
    attacker.position_ft += attacker.position_ft < target.position_ft ? moved : -moved;
    event.distance_before_ft = before;
    event.distance_after_ft = S().distance(attacker, target);
    event.movement_ft = moved;
    event.description += ` ${attacker.state.template.name} uses Remarkable Athlete to close ${moved} feet without provoking Opportunity Attacks.`;
    return event;
  }

  window.IRON_PIT_BROWSER_CHAMPION = { criticalMove };
})();
