(() => {
  "use strict";

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function splitComponents(components, total, sourceTotal) {
    if (!(components || []).length) return [components, components];
    const applied = components.map((item) => Math.max(0, Number(item.applied_total || 0)));
    const sourceParts = applied.map((value) => Math.floor(value * sourceTotal / total));
    let unassigned = Math.min(sourceTotal - sourceParts.reduce((sum, value) => sum + value, 0),
      applied.reduce((sum, value) => sum + value, 0) - sourceParts.reduce((sum, value) => sum + value, 0));
    const order = applied.map((_, index) => index).sort((left, right) =>
      (applied[right] * sourceTotal % total) - (applied[left] * sourceTotal % total) || left - right);
    for (const index of order) {
      if (unassigned <= 0) break;
      if (sourceParts[index] < applied[index]) { sourceParts[index] += 1; unassigned -= 1; }
    }
    return [
      components.map((item, index) => ({ ...item, applied_total: sourceParts[index] })),
      components.map((item, index) => ({ ...item, applied_total: applied[index] - sourceParts[index] })),
    ];
  }

  function resolveForState(sourceState, amount, setup, damageTypes = [], damageComponents = []) {
    try {
      const rule = sourceState.template.damage_transfer;
      if (!rule || amount <= 0) return { amount, damageComponents };
      if (rule.relation !== "source_grapples_target" || rule.source_rounding !== "down") {
        throw new Error("Unsupported Damage Transfer source parameters.");
      }
      if (!setup) throw new Error("Damage Transfer requires encounter setup.");
      const source = members(setup).find((item) => item.state === sourceState);
      if (!source) throw new Error("Damage Transfer source is absent from encounter setup.");
      const targets = members(setup).filter((item) => item.state.is_alive && !item.state.is_dead
        && (item.state.grapple_sources || []).some((link) => link.source_id === source.combatant_id));
      if (!targets.length) return { amount, damageComponents };
      if (targets.length !== 1) throw new Error("Damage Transfer requires exactly one attached/grappled target.");
      const sourceKeeps = Math.floor(amount / 2);
      const targetTakes = amount - sourceKeeps;
      const [sourceComponents, targetComponents] = splitComponents(damageComponents, amount, sourceKeeps);
      window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
        targets[0].state, targetTakes, false, damageTypes, members(setup).map((item) => item.state),
        setup, targetComponents, Boolean(rule.transferred_damage_retriggers),
      );
      return { amount: sourceKeeps, damageComponents: sourceComponents };
    } catch (error) {
      console.error("Failed to resolve Damage Transfer.", { source: sourceState?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRANSFER = { resolveForState };
})();
