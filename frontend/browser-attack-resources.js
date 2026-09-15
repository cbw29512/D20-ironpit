(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const W = () => window.IRON_PIT_BROWSER_RESTRAINTS;

  function actualTarget(target, setup, targetId) {
    if (!setup || target.combatant_id === targetId) return target;
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === targetId) || target;
  }

  function install() {
    const attackRuntime = window.IRON_PIT_BROWSER_ATTACK;
    if (!attackRuntime || attackRuntime.resourceAttackWrapped) return;
    const original = attackRuntime.resolveAttack;
    attackRuntime.resolveAttack = (...args) => {
      const member = args[2], target = args[3], attack = args[4], extra = args[6] || {};
      if (!E().resourceAvailable(member.state, attack)) throw new Error(`${attack.resourceId} resource is unavailable.`);
      const event = original(...args);
      const remaining = E().spendResource(member.state, attack);
      if (remaining != null) event.resource_remaining = remaining;
      if (event.hit && attack.breakableRestraint && W()) {
        const resolvedTarget = actualTarget(target, extra.setup, event.target_id);
        const applied = W().apply(resolvedTarget.state, member.combatant_id, attack);
        if (applied.length) {
          event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), ...applied])];
          for (const condition of applied) event.description += ` ${resolvedTarget.state.template.name} is ${condition}.`;
        }
      }
      return event;
    };
    attackRuntime.resourceAttackWrapped = true;
  }

  window.IRON_PIT_BROWSER_ATTACK_RESOURCES = { install };
  install();
})();
