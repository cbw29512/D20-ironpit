(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { effectiveSpeed: (state) => state.template.speed_ft };

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
  function eventTarget(event, fallback, setup) {
    return [...(setup?.heroes || []), ...(setup?.monsters || [])].find((member) => member.combatant_id === event.target_id) || fallback;
  }
  function followUp(sequence, round, member, target, profile, firstEvent, setup) {
    if (!firstEvent.hit || !profile.followUpAttackId) return { events: [], sequence };
    const actualTarget = eventTarget(firstEvent, target, setup);
    if (!actualTarget.state.is_alive || actualTarget.state.is_dead || actualTarget.state.current_hp <= 0) return { events: [], sequence };
    const attack = member.state.template.attacks.find((item) => item.id === profile.followUpAttackId);
    if (!attack) throw new Error(`Charge follow-up attack ${profile.followUpAttackId} is missing from ${member.state.template.id}.`);
    return { events: [A().resolveAttack(sequence++, round, member, actualTarget, attack, attack.reach || 5, {
      spendAction: false, featureId: "charge-follow-up", setup, ignoreCloseThreat: true,
    })], sequence };
  }
  function targetSizeAllowed(target, profile) {
    const maximum = profile.targetMaxSize || profile.proneMaxSize;
    return !maximum || window.IRON_PIT_BROWSER_STATE.canProne(target, maximum);
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
    if (M().effectiveSpeed(member.state) < (profile.minimumMove || 0)) {
      return { events: [], sequence, handled: false };
    }
    const options = { featureId: "charge", proneMaxSize: profile.proneMaxSize, setup, ignoreCloseThreat: true };
    if (Number.isInteger(profile.diceCount) && Number.isInteger(profile.diceSize) && profile.damageType) {
      options.bonusDamage = { source: "Charge", diceCount: profile.diceCount,
        diceSize: profile.diceSize, damageType: profile.damageType };
    }
    const firstEvent = A().resolveAttack(sequence++, round, member, target, chargedAttack(attack, profile), attack.reach || 5, options);
    const events = [firstEvent];
    const followed = followUp(sequence, round, member, target, profile, firstEvent, setup);
    events.push(...followed.events);
    return { events, sequence: followed.sequence, handled: true };
  }
  window.IRON_PIT_BROWSER_CHARGE = { openingEligible, openingFeature, resolveClosing };
})();
