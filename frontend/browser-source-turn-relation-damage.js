(() => {
  "use strict";
  const D = () => window.IRON_PIT_DICE;
  const DD = () => window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function resolve(sequence, round, member, setup) {
    try {
      const events = [], state = member.state;
      const rules = state.template.source_turn_relation_damages || [];
      if (!rules.length || !state.is_alive || state.is_dead || state.current_hp <= 0) {
        return { events, sequence };
      }
      const members = [...setup.heroes, ...setup.monsters], affected = members.map((item) => item.state);
      if (!DD()?.resolveDamage || !A()?.applyDamage) throw new Error("Typed source-turn damage requires universal damage runtime.");
      for (const rule of rules) {
        if (!["creatures_grappling_source", "creatures_grappled_by_source"].includes(rule.target_relation)) {
          throw new Error("Unsupported source-turn damage target relation: " + rule.target_relation);
        }
        if ((rule.save_ability == null) !== (rule.save_dc == null))
          throw new Error("Source-turn relation save needs ability and DC.");
        for (const target of members) {
          if (target.combatant_id === member.combatant_id || target.state.is_dead
            || !target.state.is_alive || target.state.current_hp <= 0) continue;
          // Source identity is not a dispatch key: the card selects relationship direction.
          const held = rule.target_relation === "creatures_grappling_source" ? state : target.state;
          const ownerId = rule.target_relation === "creatures_grappling_source"
            ? target.combatant_id : member.combatant_id;
          const active = (held.grapple_sources || []).some((grapple) =>
            grapple.source_id === ownerId
            && (!rule.required_grapple_condition_id
              || (grapple.linked_condition_ids || []).includes(rule.required_grapple_condition_id))
            && Math.abs(target.position_ft - member.position_ft) <= grapple.range_ft);
          if (!active) continue;
          let save = null;
          if (rule.save_ability != null) {
            const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
            if (!saves?.resolveSavingThrow || !Number.isInteger(rule.save_dc))
              throw new Error("Source-turn grapple save requires universal saving throws.");
            save = saves.resolveSavingThrow(
              target.state, rule.save_ability, rule.save_dc,
              {roundNumber: round, encounterRoller: target, setup},
            );
          }
          const rolls = save?.succeeded ? [] : D().rollMany(rule.dice_count, rule.dice_size);
          const total = save?.succeeded ? 0 : rolls.reduce((sum, roll) => sum + roll, rule.damage_bonus || 0);
          const hpBefore = target.state.current_hp;
          const result = save?.succeeded ? {applied: 0} : DD().resolveDamage(target.state, total, rule.damage_type);
          if (!save?.succeeded) A().applyDamage(
            target.state, result.applied, false, [rule.damage_type], affected, setup, [],
            member.combatant_id,
          );
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            feature_id: rule.source_name, hp_before: hpBefore, hp_after: target.state.current_hp,
            saving_throw_roll: save?.roll || null,
            save_ability: save ? rule.save_ability : null,
            save_dc: save ? rule.save_dc : null,
            save_succeeded: save ? save.succeeded : null,
            damage_components: save?.succeeded ? [] : [{
              source: rule.source_name, damage_type: rule.damage_type,
              notation: rule.dice_count + "d" + rule.dice_size, rolls,
              modifier: rule.damage_bonus || 0, total, applied_total: result.applied,
            }],
            animation: "feature",
            description: rule.source_name + " deals " + result.applied + " " + rule.damage_type
              + " damage to " + target.state.template.name
              + (rule.target_relation === "creatures_grappling_source" ? " grappling " : " held by ")
              + state.template.name + ".",
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Source-turn relationship damage failed", { member: member?.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_SOURCE_TURN_RELATION_DAMAGE = { resolve };
})();
