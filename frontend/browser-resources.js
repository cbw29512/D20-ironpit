(() => {
  "use strict";

  function available(state, resourceId, cost = 1) {
    if (!resourceId) return true;
    return (state.resources?.[resourceId] || 0) >= cost;
  }

  function spend(state, resourceId, cost = 1, actionId = "action") {
    if (!resourceId) return;
    if (!available(state, resourceId, cost)) {
      throw new Error(`Resource is unavailable for ${actionId}.`);
    }
    state.resources[resourceId] -= cost;
  }

  function attackAvailable(state, attack) {
    return available(state, attack?.resourceId, attack?.resourceCost || 1);
  }

  function spendAttack(state, attack) {
    spend(state, attack?.resourceId, attack?.resourceCost || 1, `attack ${attack?.id || "unknown"}`);
  }

  function rechargeStart(state, dice = window.IRON_PIT_DICE) {
    const metadata = state.template.resource_recharge || {};
    if (!dice?.roll) return [];
    const results = [];
    for (const [id, rule] of Object.entries(metadata)) {
      const current = state.resources?.[id] || 0;
      const maximum = Number(rule.maxUses || 1);
      if (current >= maximum) continue;
      const roll = dice.roll(6);
      const restored = roll >= Number(rule.minimum);
      if (restored) state.resources[id] = maximum;
      results.push({ id, roll, restored });
    }
    return results;
  }

  function ensureAttackWrapper() {
    const runtime = window.IRON_PIT_BROWSER_ATTACK;
    if (!runtime?.resolveAttack || runtime.__resourceWrapped) return;
    const raw = runtime.resolveAttack.bind(runtime);
    runtime.resolveAttack = (...args) => {
      const attacker = args[2], attack = args[4];
      if (!attackAvailable(attacker.state, attack)) {
        throw new Error(`Resource is unavailable for attack ${attack.id}.`);
      }
      const event = raw(...args);
      spendAttack(attacker.state, attack);
      return event;
    };
    runtime.__resourceWrapped = true;
  }

  window.IRON_PIT_BROWSER_RESOURCES = {
    available, attackAvailable, ensureAttackWrapper, rechargeStart, spend, spendAttack,
  };
})();
