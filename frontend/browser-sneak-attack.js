(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
  const TRIP = "cunning-strike-trip";
  const OBSCURE = "cunning-strike-obscure";

  function allyAvailable(attacker, setup) {
    if (!setup) return false;
    const allies = attacker.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.some((ally) => ally.combatant_id !== attacker.combatant_id
      && ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0 && !Q().incapacitated(ally.state));
  }

  function obscureDieCost(attacker, target, turnKey) {
    const cost = attacker.template.cunning_strike_obscure_die_cost || 0;
    if (!cost || !target || (attacker.template.sneak_attack_d6 || 0) < cost) return 0;
    if (target.active_effect_ids.includes("blinded") || I().immune(target, "blinded")) return 0;
    attacker.feature_last_turn_keys[OBSCURE] = turnKey;
    return cost;
  }

  function tripDieCost(attacker, target, turnKey) {
    const cost = attacker.template.cunning_strike_trip_die_cost || 0;
    if (!cost || !target || (attacker.template.sneak_attack_d6 || 0) < cost) return 0;
    if ((SIZE_RANK[target.template.size] ?? 99) > SIZE_RANK.large) return 0;
    if (target.active_effect_ids.includes("prone") || I().immune(target, "prone")) return 0;
    attacker.feature_last_turn_keys[TRIP] = turnKey;
    return cost;
  }

  function bonusDamage(attacker, attack, mode, turnKey, hasAlly, target = null) {
    const diceCount = attacker.template.sneak_attack_d6 || 0;
    if (!diceCount || !attack.sneakAttackEligible || mode === "disadvantage") return null;
    if (mode !== "advantage" && !hasAlly) return null;
    if (!turnKey) throw new Error("Sneak Attack requires the actual active-turn key.");
    if (attacker.feature_last_turn_keys["sneak-attack"] === turnKey) return null;
    const cost = obscureDieCost(attacker, target, turnKey) || tripDieCost(attacker, target, turnKey);
    attacker.feature_last_turn_keys["sneak-attack"] = turnKey;
    return { source: "Sneak Attack", diceCount: diceCount - cost, diceSize: 6, damageType: attack.damageType };
  }

  function resolveObscure(attacker, defender, turnKey) {
    if (attacker.feature_last_turn_keys[OBSCURE] !== turnKey) {
      return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    }
    if (defender.is_dead) return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    const dexterity = attacker.template.ability_scores?.dexterity;
    const level = attacker.template.level;
    if (!Number.isInteger(dexterity) || !Number.isInteger(level)) {
      throw new Error("Obscure requires certified Dexterity and level.");
    }
    const dc = 8 + Math.floor((dexterity - 10) / 2) + 2 + Math.floor((level - 1) / 4);
    const save = S().resolveSavingThrow(defender, "dexterity", dc);
    let applied = false;
    if (!save.succeeded) {
      const separator = turnKey.indexOf(":");
      const sourceId = separator >= 0 ? turnKey.slice(separator + 1) : attacker.template.id;
      applied = Boolean(T()?.apply(defender, "blinded", sourceId, {
        sourceEffectId: OBSCURE,
        expiryTiming: "target_turn_end",
        useDefaultPoisonRecovery: false,
      }));
    }
    return { saveRoll: save.roll, saveDc: dc, saveSucceeded: save.succeeded, applied };
  }

  function resolveTrip(attacker, defender, turnKey) {
    if (attacker.feature_last_turn_keys[TRIP] !== turnKey) {
      return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    }
    if (defender.is_dead) return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    const dexterity = attacker.template.ability_scores?.dexterity;
    const level = attacker.template.level;
    if (!Number.isInteger(dexterity) || !Number.isInteger(level)) {
      throw new Error("Cunning Strike requires certified Dexterity and level.");
    }
    const dc = 8 + Math.floor((dexterity - 10) / 2) + 2 + Math.floor((level - 1) / 4);
    const save = S().resolveSavingThrow(defender, "dexterity", dc);
    const applied = !save.succeeded && !defender.active_effect_ids.includes("prone");
    if (applied) defender.active_effect_ids.push("prone");
    return { saveRoll: save.roll, saveDc: dc, saveSucceeded: save.succeeded, applied };
  }

  window.IRON_PIT_BROWSER_SNEAK_ATTACK = {
    allyAvailable, bonusDamage, obscureDieCost, resolveObscure, resolveTrip, tripDieCost,
  };
})();
