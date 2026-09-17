(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const R = () => window.IRON_PIT_BROWSER_RAGE;

  function bestMelee(member, target) {
    const distance = S().distance(member, target);
    const legal = (member.state.template.attacks || []).filter((attack) =>
      attack.kind === "melee" && distance <= (attack.reach || 5));
    if (!legal.length) return null;
    legal.sort((left, right) =>
      (right.diceCount * right.diceSize + right.damageBonus) - (left.diceCount * left.diceSize + left.damageBonus)
      || right.bonus - left.bonus);
    return { attack: legal[0], distance };
  }

  function resolve(sequence, round, member, setup, turnKey) {
    const state = member.state;
    if (state.template.ruleset !== "2014" || !state.template.frenzy_bonus_attack_2014 || !R()?.active(state)
        || !state.active_effect_ids.includes("frenzy-2014") || !E().available(state, "bonus_action")) {
      return { events: [], sequence };
    }
    for (const target of F().targetOrder(member, setup)) {
      const choice = bestMelee(member, target);
      if (!choice) continue;
      E().spend(state, "bonus_action");
      const event = A().resolveAttack(sequence, round, member, target, choice.attack, choice.distance, {
        spendAction: false, featureId: "frenzy", turnKey, setup, allowReckless: false,
      });
      return { events: [event], sequence: sequence + 1 };
    }
    return { events: [], sequence };
  }

  window.IRON_PIT_BROWSER_FRENZY_2014 = { resolve };
})();
