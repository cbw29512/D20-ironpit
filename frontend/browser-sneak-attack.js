(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function allyAvailable(attacker, setup) {
    if (!setup) return false;
    const allies = attacker.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.some((ally) => ally.combatant_id !== attacker.combatant_id
      && ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0 && !Q().incapacitated(ally.state));
  }

  function bonusDamage(attacker, attack, mode, turnKey, hasAlly) {
    const diceCount = attacker.template.sneak_attack_d6 || 0;
    if (!diceCount || !attack.sneakAttackEligible || mode === "disadvantage") return null;
    if (mode !== "advantage" && !hasAlly) return null;
    if (!turnKey) throw new Error("Sneak Attack requires the actual active-turn key.");
    if (attacker.feature_last_turn_keys["sneak-attack"] === turnKey) return null;
    attacker.feature_last_turn_keys["sneak-attack"] = turnKey;
    return { source: "Sneak Attack", diceCount, diceSize: 6, damageType: attack.damageType };
  }

  window.IRON_PIT_BROWSER_SNEAK_ATTACK = { allyAvailable, bonusDamage };
})();
