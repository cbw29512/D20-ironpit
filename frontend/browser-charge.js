(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available };
  const W = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT || {
    moveToward: (q, r, m, t, _s, d) => ({ events: [], sequence: q, movement: S().moveToward(m, t, d) }),
  };

  function openingEligible(round, member, setup) {
    if (round !== 1 || !setup || !Number.isInteger(member.state.initiative_total)) return false;
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.length > 0 && enemies.every((enemy) => Number.isInteger(enemy.state.initiative_total)
      && member.state.initiative_total > enemy.state.initiative_total);
  }
  function openingFeature(round, member, setup) {
    if (!openingEligible(round, member, setup)) return null;
    return member.state.template.source_trait_names?.includes("Running Leap") ? "running-leap" : null;
  }
  function movementEvent(sequence, round, member, target, movement) {
    return { sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      distance_before_ft: movement.before, distance_after_ft: movement.after, movement_ft: movement.moved,
      animation: "advance", description: `${member.state.template.name} charges ${movement.moved} feet.` };
  }
  function resolveClosing(sequence, round, member, target, setup = null) {
    if (!openingEligible(round, member, setup)) return { events: [], sequence, handled: false };
    const attack = member.state.template.attacks.find((a) => a.id === member.state.template.primary_attack_id) || member.state.template.attacks[0];
    const profile = attack?.charge;
    if (!profile || !E().available(member.state, "action") || !S().canProne(target, profile.proneMaxSize)) {
      return { events: [], sequence, handled: false };
    }
    const needed = Math.max(0, S().distance(member, target) - (attack.reach || 5));
    if (needed > member.state.movement_remaining_ft) return { events: [], sequence, handled: false };
    const events = [];
    if (needed > 0) {
      const moved = W().moveToward(sequence, round, member, target, setup, attack.reach || 5);
      events.push(...moved.events); sequence = moved.sequence;
      if (!moved.movement) return { events, sequence, handled: events.length > 0 };
      events.push(movementEvent(sequence++, round, member, target, moved.movement));
    }
    const options = { featureId: "charge", proneMaxSize: profile.proneMaxSize };
    if (Number.isInteger(profile.diceCount) && Number.isInteger(profile.diceSize) && profile.damageType) {
      options.bonusDamage = { source: "Charge", diceCount: profile.diceCount,
        diceSize: profile.diceSize, damageType: profile.damageType };
    }
    events.push(A().resolveAttack(sequence++, round, member, target, attack, S().distance(member, target), options));
    return { events, sequence, handled: true };
  }
  window.IRON_PIT_BROWSER_CHARGE = { openingEligible, openingFeature, resolveClosing };
})();
