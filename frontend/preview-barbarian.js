(() => {
  "use strict";

  const physical = new Set(["bludgeoning", "piercing", "slashing"]);

  function rageChange(actor, operation) {
    return {
      actor_id: actor.template.id,
      effect_id: "rage",
      operation,
      kind: "buff",
      label: "Rage",
      detail: "B/P/S resistance, Strength save Advantage, and Strength attack damage bonus.",
    };
  }

  function enterRage(actor, events) {
    if (!actor.template.features.includes("rage") || actor.raging || actor.rageUses <= 0) return;
    actor.rageUses -= 1;
    actor.raging = true;
    actor.rageExtensionRequired = false;
    events.push({
      event_type: "status", actor_id: actor.template.id, feature_id: "rage", animation: "status",
      description: `${actor.template.name} enters Rage. ${actor.rageUses} uses remain.`,
      effect_changes: [rageChange(actor, "apply")],
    });
  }

  function beginTurn(actor, events) {
    if (actor.raging) actor.rageExtensionRequired = true;
    else enterRage(actor, events);
  }

  function markAttack(actor) {
    if (actor.raging) actor.rageExtensionRequired = false;
  }

  function endTurn(actor, events) {
    if (!actor.raging || !actor.rageExtensionRequired) return;
    actor.raging = false;
    actor.rageExtensionRequired = false;
    events.push({
      event_type: "status", actor_id: actor.template.id, animation: "status", log_visible: false,
      description: "Rage expires.", effect_changes: [rageChange(actor, "remove")],
    });
  }

  function damageBonus(actor, weapon) {
    return actor.raging && weapon.ability === "strength" ? 2 : 0;
  }

  function damageTaken(target, components) {
    const totals = new Map();
    for (const component of components) {
      const type = component.damageType || "slashing";
      totals.set(type, (totals.get(type) || 0) + Math.max(0, component.total));
    }
    let applied = 0;
    let resisted = false;
    for (const [type, raw] of totals.entries()) {
      if (target.raging && physical.has(type)) {
        applied += Math.floor(raw / 2);
        resisted = true;
      } else applied += raw;
    }
    return { applied, resisted };
  }

  window.IRON_PIT_BARBARIAN = { beginTurn, damageBonus, damageTaken, endTurn, markAttack };
})();
