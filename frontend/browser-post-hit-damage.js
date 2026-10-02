(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function payment(state, rule, turnKey) {
    if (rule.free_resource_id && R().available(state, rule.free_resource_id, 1)) {
      return { resourceId: rule.free_resource_id, slotLevel: rule.printed_spell_level, expendsSlot: false };
    }
    if (!S().slotSpellAvailable(state, turnKey)) return null;
    for (let level = rule.max_slot_level; level >= rule.printed_spell_level; level -= 1) {
      const resourceId = "spell-slot-" + level;
      if (R().available(state, resourceId, 1)) {
        return { resourceId, slotLevel: level, expendsSlot: true };
      }
    }
    return null;
  }

  function baseCreatureType(raw) {
    return String(raw || "").split(" (", 1)[0].trim().toLowerCase();
  }

  function bonusDamage(attacker, attack, turnKey, target = null) {
    try {
      const rule = attacker?.template?.resource_backed_post_hit_damage;
      if (!rule || !(rule.trigger_attack_ids || []).includes(attack?.id)) return null;
      if (!target || target.current_hp <= 0 || target.is_dead || !target.is_alive) return null;
      if (!turnKey) throw new Error("Post-hit resource damage requires the active turn key.");
      if (!E().available(attacker, rule.action_cost)) return null;
      const paid = payment(attacker, rule, turnKey);
      if (!paid) return null;

      E().spend(attacker, rule.action_cost);
      if (paid.expendsSlot) S().markSlotSpellCast(attacker, turnKey);
      R().spend(attacker, paid.resourceId, 1);

      let count = rule.base_dice_count
        + rule.dice_per_slot_above * (paid.slotLevel - rule.printed_spell_level);
      if ((rule.bonus_target_creature_types || []).includes(baseCreatureType(target.template.creature_type))) {
        count += rule.bonus_target_dice_count || 0;
      }
      return {
        source: rule.source_name,
        diceCount: count,
        diceSize: rule.dice_size,
        damageBonus: 0,
        damageType: rule.damage_type,
      };
    } catch (error) {
      console.error("Browser post-hit resource damage failed", { combatant: attacker?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POST_HIT_DAMAGE = { bonusDamage };
})();
