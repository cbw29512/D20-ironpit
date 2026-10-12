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
        if (rule.target_relation !== "creatures_grappling_source") {
          throw new Error("Unsupported source-turn damage target relation: " + rule.target_relation);
        }
        for (const target of members) {
          if (target.combatant_id === member.combatant_id || target.state.is_dead
            || !target.state.is_alive || target.state.current_hp <= 0) continue;
          const active = (state.grapple_sources || []).some((grapple) =>
            grapple.source_id === target.combatant_id
            && Math.abs(target.position_ft - member.position_ft) <= grapple.range_ft);
          if (!active) continue;
          const rolls = D().rollMany(rule.dice_count, rule.dice_size);
          const total = rolls.reduce((sum, roll) => sum + roll, 0);
          const hpBefore = target.state.current_hp;
          const result = DD().resolveDamage(target.state, total, rule.damage_type);
          A().applyDamage(target.state, result.applied, false, [rule.damage_type], affected, setup);
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            feature_id: rule.source_name, hp_before: hpBefore, hp_after: target.state.current_hp,
            damage_components: [{
              source: rule.source_name, damage_type: rule.damage_type,
              notation: rule.dice_count + "d" + rule.dice_size, rolls,
              modifier: 0, total, applied_total: result.applied,
            }],
            animation: "feature",
            description: rule.source_name + " deals " + result.applied + " " + rule.damage_type
              + " damage to " + target.state.template.name + " grappling " + state.template.name + ".",
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
