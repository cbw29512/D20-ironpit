(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const PROVOKING = new Set(["speed", "action", "bonus_action", "reaction"]);

  function meleeDepartureAttack(member, before, after) {
    return (member.state.template.attacks || []).find((attack) =>
      attack.kind === "melee" && before <= (attack.reach || 5) && after > (attack.reach || 5),
    ) || null;
  }

  function parryHit(defender, attack, attackRoll, hit) {
    const parry = defender.template.parry_reaction;
    if (!hit || !parry || attack.kind !== "melee" || attackRoll.selected_roll === 20) return { hit, used: false };
    if (!E().available(defender, "reaction")) return { hit, used: false };
    if (attackRoll.total >= defender.template.armor_class + parry.ac_bonus) return { hit, used: false };
    E().spend(defender, "reaction");
    return { hit: false, used: true };
  }

  function redirectAttack(defender, setup) {
    const rule = defender.state.template.redirect_attack_reaction;
    if (!rule || !setup || !E().available(defender.state, "reaction")) return null;
    const allies = defender.side === "heroes" ? setup.heroes : setup.monsters;
    const candidates = allies.filter((ally) => ally !== defender && ally.state.is_alive && !ally.state.is_dead
      && ally.state.current_hp > 0 && S().sizeAtMost(ally, rule.ally_max_size)
      && S().distance(defender, ally) <= rule.ally_range_ft);
    candidates.sort((a, b) => S().distance(defender, a) - S().distance(defender, b)
      || a.combatant_id.localeCompare(b.combatant_id));
    const ally = candidates[0] || null;
    if (!ally) return null;
    E().spend(defender.state, "reaction");
    [defender.position_ft, ally.position_ft] = [ally.position_ft, defender.position_ft];
    return ally;
  }

  function resolveOpportunityAttack(sequence, round, reactor, mover, setup, before, after, movementSource, options = {}) {
    if (reactor.side === mover.side || options.canSee === false || options.disengaged === true) return null;
    if (!PROVOKING.has(movementSource) || !E().available(reactor.state, "reaction")) return null;
    const attack = meleeDepartureAttack(reactor, before, after);
    if (!attack) return null;
    E().spend(reactor.state, "reaction");
    const pack = S().packTactics(reactor, setup);
    return A().resolveAttack(sequence, round, reactor, mover, attack, before, {
      spendAction: false, advantage: pack ? 1 : 0, featureId: "opportunity-attack", setup,
    });
  }

  window.IRON_PIT_BROWSER_REACTIONS = { parryHit, redirectAttack, resolveOpportunityAttack };
})();
