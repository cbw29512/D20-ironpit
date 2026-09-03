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
  function eventTarget(event, fallback, setup) {
    return [...(setup?.heroes || []), ...(setup?.monsters || [])].find((member) => member.combatant_id === event.target_id) || fallback;
  }
  function followUp(sequence, round, member, target, profile, firstEvent, setup) {
    if (!firstEvent.hit || !profile.followUpAttackId) return { events: [], sequence };
    const actualTarget = eventTarget(firstEvent, target, setup);
    if (!actualTarget.state.is_alive || actualTarget.state.is_dead || actualTarget.state.current_hp <= 0) return { events: [], sequence };
    const attack = member.state.template.attacks.find((item) => item.id === profile.followUpAttackId);
    if (!attack) throw new Error(`Charge follow-up attack ${profile.followUpAttackId} is missing from ${member.state.template.id}.`);
    return { events: [A().resolveAttack(sequence++, round, member, actualTarget, attack, S().distance(member, actualTarget), {
      spendAction: false, featureId: "charge-follow-up", setup,
    })], sequence };
  }
  function targetSizeAllowed(target, profile) {
    const maximum = profile.targetMaxSize || profile.proneMaxSize;
    return !maximum || S().canProne(target, maximum);
  }
  function chargedAttack(attack, profile) {
    if (!profile.replacementDamage) return attack;
    return { ...attack, fixedDamage: null,
      diceCount: profile.replacementDamage.diceCount, diceSize: profile.replacementDamage.diceSize,
      damageBonus: profile.replacementDamage.damageBonus || 0, damageType: profile.replacementDamage.damageType };
  }
  function resolveClosing(sequence, round, member, target, setup = null) {
    if (!openingEligible(round, member, setup)) return { events: [], sequence, handled: false };
    const attack = member.state.template.attacks.find((item) => item.charge);
    const profile = attack?.charge;
    if (!profile || !E().available(member.state, "action") || !targetSizeAllowed(target, profile)) {
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
    const options = { featureId: "charge", proneMaxSize: profile.proneMaxSize, setup };
    if (Number.isInteger(profile.diceCount) && Number.isInteger(profile.diceSize) && profile.damageType) {
      options.bonusDamage = { source: "Charge", diceCount: profile.diceCount,
        diceSize: profile.diceSize, damageType: profile.damageType };
    }
    const firstEvent = A().resolveAttack(sequence++, round, member, target, chargedAttack(attack, profile), S().distance(member, target), options);
    events.push(firstEvent);
    const followed = followUp(sequence, round, member, target, profile, firstEvent, setup);
    events.push(...followed.events);
    return { events, sequence: followed.sequence, handled: true };
  }
  window.IRON_PIT_BROWSER_CHARGE = { openingEligible, openingFeature, resolveClosing };
})();
