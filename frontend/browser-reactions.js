(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const PROVOKING = new Set(["speed", "action", "bonus_action", "reaction"]);

  function unarmedOpportunityAttack(template) {
    const profile = template.unarmed_opportunity_attack;
    if (!profile) return null;
    return {
      id: "unarmed-strike-opportunity",
      name: "Unarmed Strike",
      kind: "melee",
      bonus: profile.attack_bonus,
      diceCount: 0,
      diceSize: 2,
      damageBonus: 0,
      fixedDamage: profile.damage,
      damageType: "bludgeoning",
      reach: 5,
      animation: "punch",
    };
  }

  function opportunityAttackWeapon(reactor, mover, before, after, source, options = {}) {
    if (reactor.side === mover.side || options.canSee === false || options.disengaged === true) return null;
    if (Q()?.has(reactor.state, "blinded") || !PROVOKING.has(source) || !E().available(reactor.state, "reaction")) return null;
    const weapon = (reactor.state.template.attacks || []).find((attack) =>
      attack.kind === "melee" && before <= (attack.reach || 5) && after > (attack.reach || 5),
    );
    if (weapon) return weapon;
    const unarmed = unarmedOpportunityAttack(reactor.state.template);
    return unarmed && before <= 5 && after > 5 ? unarmed : null;
  }

  function parryHit(defender, attack, attackRoll, hit) {
    const parry = defender.template.parry_reaction;
    if (!hit || !parry || attack.kind !== "melee" || attackRoll.selected_roll === 20) return { hit, used: false };
    if (!E().available(defender, "reaction")) return { hit, used: false };
    if (attackRoll.total >= defender.template.armor_class + parry.ac_bonus) return { hit, used: false };
    E().spend(defender, "reaction");
    return { hit: false, used: true };
  }

  function swapWouldProvoke(defender, ally, setup) {
    const opponents = defender.side === "heroes" ? setup.monsters : setup.heroes;
    return opponents.some((reactor) => opportunityAttackWeapon(
      reactor, defender, S().distance(reactor, defender), Math.abs(reactor.position_ft - ally.position_ft), "reaction",
    ));
  }

  function redirectAttack(defender, setup) {
    const rule = defender.state.template.redirect_attack_reaction;
    if (!rule || !setup || !E().available(defender.state, "reaction") || Q()?.has(defender.state, "blinded")) return null;
    const allies = defender.side === "heroes" ? setup.heroes : setup.monsters;
    const candidates = allies.filter((ally) => ally !== defender && ally.state.is_alive && !ally.state.is_dead
      && S().sizeAtMost(ally, rule.ally_max_size) && S().distance(defender, ally) <= rule.ally_range_ft
      && !swapWouldProvoke(defender, ally, setup));
    candidates.sort((a, b) => S().distance(defender, a) - S().distance(defender, b)
      || a.combatant_id.localeCompare(b.combatant_id));
    const ally = candidates[0] || null;
    if (!ally) return null;
    E().spend(defender.state, "reaction");
    [defender.position_ft, ally.position_ft] = [ally.position_ft, defender.position_ft];
    return ally;
  }

  function resolveOpportunityAttack(sequence, round, reactor, mover, setup, before, after, movementSource, options = {}) {
    const attack = opportunityAttackWeapon(reactor, mover, before, after, movementSource, options);
    if (!attack) return null;
    E().spend(reactor.state, "reaction");
    const pack = S().packTactics(reactor, setup);
    return A().resolveAttack(sequence, round, reactor, mover, attack, before, {
      spendAction: false, advantage: pack ? 1 : 0, featureId: "opportunity-attack", setup,
    });
  }

  window.IRON_PIT_BROWSER_REACTIONS = {
    opportunityAttackWeapon, parryHit, redirectAttack, resolveOpportunityAttack,
  };
})();
