(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const L = () => window.IRON_PIT_BROWSER_LIGHT_WEAPONS;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function inRange(attack, distance) {
    if (attack.kind === "melee") return distance <= (attack.reach || 5);
    return Number.isFinite(attack.long) && distance <= attack.long;
  }

  function resolve(sequence, round, member, setup, triggerAttack, turnKey) {
    const plan = L().plan(member.state, triggerAttack, turnKey);
    if (!plan) return { events: [], sequence };
    if (plan.usesBonusAction && !E().available(member.state, "bonus_action")) {
      return { events: [], sequence };
    }
    const target = S().nearestTarget(member, setup);
    if (!target) return { events: [], sequence };
    const distance = S().distance(member, target);
    if (!inRange(plan.attack, distance)) return { events: [], sequence };
    if (plan.usesBonusAction) E().spend(member.state, "bonus_action");
    L().markUsed(member.state, turnKey);
    const pack = S().packTactics(member, setup);
    const event = A().resolveAttack(sequence++, round, member, target, plan.attack, distance, {
      spendAction: false, advantage: pack ? 1 : 0, setup,
      featureId: plan.featureId, turnKey, allowReckless: true,
    });
    return { events: [event], sequence };
  }

  window.IRON_PIT_BROWSER_LIGHT_ATTACK = { inRange, resolve };
})();
