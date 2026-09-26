(() => {
  "use strict";

  function bonusDamage(attacker, turnKey, target = null, attack = null) {
    const rider = attacker.template.once_per_turn_weapon_hit_damage_rider || null;
    if (!rider) return null;
    if (!turnKey) throw new Error(`${rider.source_name} requires the actual active-turn key.`);
    if (rider.requires_target_below_max_hp) {
      if (!target) throw new Error(`${rider.source_name} requires target state for its hit qualification.`);
      if (target.current_hp >= target.template.max_hp) return null;
    }
    if (attacker.feature_last_turn_keys[rider.source_id] === turnKey) return null;
    attacker.feature_last_turn_keys[rider.source_id] = turnKey;
    return {
      source: rider.source_name,
      diceCount: rider.dice_count,
      diceSize: rider.dice_size,
      damageType: rider.damage_type || attack?.damageType,
    };
  }

  window.IRON_PIT_BROWSER_ONCE_PER_TURN_HIT_DAMAGE = { bonusDamage };
})();
