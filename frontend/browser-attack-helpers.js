(() => {
  "use strict";

  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { attacksAgainstAdvantage: () => 0 };
  const CAM = () => window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK || { advantage: () => 0, disadvantage: () => 0 };
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || {
    attacksAgainstAdvantage: () => 0, effectiveSpeed: (state) => state.template.speed_ft,
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    attackAdvantage: (state) => state.is_unconscious, has: (state, id) => state.active_effect_ids.includes(id),
    incapacitated: (state) => state.is_unconscious,
  };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;

  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];

  function conditionSources(attacker, defender, distance, targetId) {
    let advantage = M().attacksAgainstAdvantage(defender) + B2().attacksAgainstAdvantage(defender), disadvantage = 0;
    for (const id of ["blinded", "prone", "restrained", "poisoned"]) if (Q().has(attacker, id)) disadvantage += 1;
    disadvantage += G()?.attackDisadvantage(attacker, targetId) || 0;
    if (Q().has(defender, "dodge") && !Q().incapacitated(defender) && M().effectiveSpeed(defender) > 0 && !G()?.speedIsZero(defender)) disadvantage += 1;
    if (Q().attackAdvantage(defender)) advantage += 1;
    if (Q().has(defender, "restrained")) advantage += 1;
    if (Q().has(defender, "prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }

  function rangedCloseThreat(attacker, target, distance, setup) {
    if (!setup) return distance <= 5 && !Q().incapacitated(target.state);
    const enemies = attacker.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.some((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.current_hp > 0
      && !Q().incapacitated(enemy.state) && S().distance(attacker, enemy) <= 5);
  }

  const bloodiedFury = (state, attack) => state.template.traits?.includes("bloodied-fury")
    && attack.kind === "melee" && state.current_hp * 2 <= state.template.max_hp ? 1 : 0;

  function adjustedDamage(target, amount, type, allowVulnerability = true) {
    if (target.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    if (target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type) || Q().has(target, "petrified")) value = Math.floor(value / 2);
    if (allowVulnerability && target.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  }

  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = []) {
    const lifecycle = Z();
    if (!lifecycle) throw new Error("Browser zero-HP runtime is not loaded.");
    return lifecycle.applyDamage(state, amount, critical, damageTypes, affectedStates);
  }

  window.IRON_PIT_BROWSER_ATTACK_HELPERS = {
    adjustedDamage, applyDamage, bloodiedFury, conditionSources, rangedCloseThreat, states, CAM,
  };
})();
