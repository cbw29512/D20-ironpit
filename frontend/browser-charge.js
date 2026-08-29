(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function movementEvent(sequence, round, member, target, movement) {
    return {
      sequence, round_number: round, event_type: "movement",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      distance_before_ft: movement.before, distance_after_ft: movement.after,
      movement_ft: movement.moved, animation: "advance",
      description: `${member.state.template.name} charges ${movement.moved} feet.`,
    };
  }

  function resolveClosing(sequence, round, member, target) {
    const attack = member.state.template.attacks.find(
      (item) => item.id === member.state.template.primary_attack_id,
    ) || member.state.template.attacks[0];
    const profile = attack?.charge;
    if (!profile || !member.state.action_available) return { events: [], sequence, handled: false };
    const distance = S().distance(member, target);
    const movementNeeded = Math.max(0, distance - (attack.reach || 5));
    if (movementNeeded < profile.minimumMove || movementNeeded > member.state.movement_remaining_ft) {
      return { events: [], sequence, handled: false };
    }
    if (!S().canProne(target, profile.proneMaxSize)) return { events: [], sequence, handled: false };

    const movement = S().moveToward(member, target, attack.reach || 5);
    if (!movement || movement.moved < profile.minimumMove) return { events: [], sequence, handled: false };
    const moveEvent = movementEvent(sequence++, round, member, target, movement);
    const attackEvent = A().resolveAttack(
      sequence++, round, member, target, attack, S().distance(member, target), {
        featureId: "charge",
        bonusDamage: {
          source: "Charge", diceCount: profile.diceCount, diceSize: profile.diceSize,
          damageType: profile.damageType,
        },
        proneMaxSize: profile.proneMaxSize,
      },
    );
    return { events: [moveEvent, attackEvent], sequence, handled: true };
  }

  window.IRON_PIT_BROWSER_CHARGE = { resolveClosing };
})();
