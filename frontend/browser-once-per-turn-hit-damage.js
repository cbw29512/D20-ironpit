(() => {
  "use strict";

  function qualified(rider, target) {
    if (rider.requires_target_below_max_hp) {
      if (!target) throw new Error(`${rider.source_name} requires target state for its hit qualification.`);
      if (target.current_hp >= target.template.max_hp) return false;
    }
    if (rider.target_creature_types?.length) {
      if (!target) throw new Error(`${rider.source_name} requires target state for its creature-type qualification.`);
      const raw = target.template.creature_type || "";
      const targetType = String(raw).split(" (", 1)[0].trim().toLowerCase();
      if (!rider.target_creature_types.includes(targetType)) return false;
    }
    return true;
  }

  function spec(rider, attack) {
    return {
      source: rider.source_name,
      diceCount: rider.dice_count,
      diceSize: rider.dice_size,
      damageBonus: rider.flat_bonus || 0,
      damageType: rider.damage_type || attack?.damageType,
    };
  }

  function bonusDamages(attacker, turnKey, target = null, attack = null) {
    if (!turnKey) throw new Error("Once-per-turn hit riders require the actual active-turn key.");
    const primary = attacker.template.once_per_turn_weapon_hit_damage_rider || null;
    const extra = attacker.template.once_per_turn_weapon_hit_damage_riders || [];
    const riders = [...(primary ? [primary] : []), ...extra];
    const seen = new Set();
    const result = [];
    for (const rider of riders) {
      if (seen.has(rider.source_id)) throw new Error(`Duplicate once-per-turn hit rider source id: ${rider.source_id}.`);
      seen.add(rider.source_id);
      if (attacker.feature_last_turn_keys[rider.source_id] === turnKey) continue;
      if (!qualified(rider, target)) continue;
      attacker.feature_last_turn_keys[rider.source_id] = turnKey;
      result.push(spec(rider, attack));
    }
    return result;
  }

  function bonusDamage(attacker, turnKey, target = null, attack = null) {
    return bonusDamages(attacker, turnKey, target, attack)[0] || null;
  }

  window.IRON_PIT_BROWSER_ONCE_PER_TURN_HIT_DAMAGE = { bonusDamage, bonusDamages };
})();
