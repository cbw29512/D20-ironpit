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

  function candidateRules(attacker) {
    const options = attacker?.template?.post_hit_damage_options;
    if (options && options.length) return options;
    const single = attacker?.template?.resource_backed_post_hit_damage;
    return single ? [single] : [];
  }

  function bonusDamage(attacker, attack, turnKey, target = null) {
    try {
      if (!attacker) return null;
      attacker.pending_post_hit_failed_save = null;
      if (!target || target.current_hp <= 0 || target.is_dead || !target.is_alive) return null;
      if (!turnKey) throw new Error("Post-hit resource damage requires the active turn key.");
      let chosen = null;
      for (const rule of candidateRules(attacker)) {
        if (!(rule.trigger_attack_ids || []).includes(attack?.id)) continue;
        if (!E().available(attacker, rule.action_cost)) continue;
        const paid = payment(attacker, rule, turnKey);
        if (!paid) continue;
        chosen = { rule, paid };
        break;
      }
      if (!chosen) return null;

      E().spend(attacker, chosen.rule.action_cost);
      if (chosen.paid.expendsSlot) S().markSlotSpellCast(attacker, turnKey);
      R().spend(attacker, chosen.paid.resourceId, 1);
      attacker.pending_post_hit_failed_save = chosen.rule.failed_save
        ? { ...chosen.rule.failed_save, sourceName: chosen.rule.source_name }
        : null;

      let count = chosen.rule.base_dice_count
        + chosen.rule.dice_per_slot_above * (chosen.paid.slotLevel - chosen.rule.printed_spell_level);
      if ((chosen.rule.bonus_target_creature_types || []).includes(baseCreatureType(target.template.creature_type))) {
        count += chosen.rule.bonus_target_dice_count || 0;
      }
      return {
        source: chosen.rule.source_name,
        diceCount: count,
        diceSize: chosen.rule.dice_size,
        damageBonus: 0,
        damageType: chosen.rule.damage_type,
      };
    } catch (error) {
      console.error("Browser post-hit resource damage failed", { combatant: attacker?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POST_HIT_DAMAGE = { bonusDamage };
})();
