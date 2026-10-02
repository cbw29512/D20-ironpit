(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const D = () => window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;

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

  function resolve(sequence, round, source, target, attackId, critical, setup, turnKey) {
    try {
      const rule = source?.state?.template?.resource_backed_post_hit_damage;
      if (!rule || !(rule.trigger_attack_ids || []).includes(attackId)) return null;
      if (target.state.current_hp <= 0 || target.state.is_dead || !target.state.is_alive) return null;
      if (!E().available(source.state, rule.action_cost)) return null;
      const paid = payment(source.state, rule, turnKey);
      if (!paid) return null;

      E().spend(source.state, rule.action_cost);
      if (paid.expendsSlot) S().markSlotSpellCast(source.state, turnKey);
      const remaining = R().spend(source.state, paid.resourceId, 1);

      let count = rule.base_dice_count
        + rule.dice_per_slot_above * (paid.slotLevel - rule.printed_spell_level);
      if ((rule.bonus_target_creature_types || []).includes(baseCreatureType(target.state.template.creature_type))) {
        count += rule.bonus_target_dice_count || 0;
      }
      const rolledCount = count * (critical && rule.doubles_on_critical ? 2 : 1);
      const rolls = Array.from({ length: rolledCount }, () => window.IRON_PIT_DICE.roll(rule.dice_size));
      const raw = rolls.reduce((a, b) => a + b, 0);
      const applied = D().adjustedDamage(target.state, raw, rule.damage_type);
      const hpBefore = target.state.current_hp;
      const tempBefore = target.state.temporary_hp || 0;
      if (applied) {
        Z().applyDamage(
          target.state, applied, Boolean(critical), [rule.damage_type],
          [...setup.heroes, ...setup.monsters].map((member) => member.state),
        );
      }
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: source.combatant_id,
        actor_name: source.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        feature_id: rule.source_id,
        damage_roll: { notation: String(rolledCount) + "d" + rule.dice_size, rolls, modifier: 0, total: applied },
        damage_components: [{
          source: rule.source_name,
          notation: String(rolledCount) + "d" + rule.dice_size,
          rolls,
          modifier: 0,
          damage_type: rule.damage_type,
          total: raw,
          applied_total: applied,
        }],
        hp_before: hpBefore,
        hp_after: target.state.current_hp,
        temporary_hp_before: tempBefore,
        temporary_hp_after: target.state.temporary_hp || 0,
        resource_remaining: remaining,
        animation: "radiant",
        description: source.state.template.name + " casts " + rule.source_name
          + " after the hit, dealing " + applied + " " + rule.damage_type + " damage.",
      };
    } catch (error) {
      console.error("Browser post-hit damage resolution failed", { source: source?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POST_HIT_DAMAGE = { resolve };
})();
