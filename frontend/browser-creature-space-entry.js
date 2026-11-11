(() => {
  "use strict";

  // The card supplies the trigger and damage; no monster/ability name dispatch.
  function resolve(sequence, round, mover, setup, turnKey) {
    try {
      if (!mover.state.position || !turnKey) throw new Error("Space entry needs a position and turn key.");
      const actions = (mover.state.template.timed_self_buff_actions || []).filter(
        (action) => action.activationTiming === "passive" && action.creatureSpaceEntryDamage,
      );
      if (!actions.length) return { events: [], sequence };
      const members = [...setup.heroes, ...setup.monsters];
      const affected = members.map((item) => item.state);
      const dice = window.IRON_PIT_DICE;
      const defense = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
      const attacks = window.IRON_PIT_BROWSER_ATTACK;
      const recurrence = window.IRON_PIT_BROWSER_ON_HIT_RECURRING_DAMAGE;
      if (!dice?.rollMany || !defense?.resolveDamage || !attacks?.applyDamage
        || !recurrence?.applyFromSource) throw new Error("Space entry requires shared damage and recurrence.");
      const events = [];
      mover.state.feature_last_turn_keys ||= {};
      for (const target of members) {
        const pos = target.state.position;
        if (target.combatant_id === mover.combatant_id || !pos
          || pos.x !== mover.state.position.x || pos.y !== mover.state.position.y
          || target.state.is_dead || !target.state.is_alive) continue;
        for (const action of actions) {
          const marker = `creature-space:${action.id}:${target.combatant_id}`;
          if (mover.state.feature_last_turn_keys[marker] === turnKey) continue;
          mover.state.feature_last_turn_keys[marker] = turnKey;
          const spec = action.creatureSpaceEntryDamage;
          if (!Number.isInteger(spec.diceCount) || spec.diceCount < 1
            || !Number.isInteger(spec.diceSize) || spec.diceSize < 2
            || !spec.damageType || !spec.recurringDamage) throw new Error("Incomplete space-entry source.");
          const rolls = dice.rollMany(spec.diceCount, spec.diceSize);
          const raw = rolls.reduce((sum, value) => sum + value, 0);
          const before = target.state.current_hp;
          const applied = defense.resolveDamage(target.state, raw, spec.damageType).applied;
          if (applied) attacks.applyDamage(
            target.state, applied, false, [spec.damageType],
            affected, setup, [], mover.combatant_id,
          );
          const burning = recurrence.applyFromSource(
            target, mover.combatant_id, action.id, action.name, spec.recurringDamage,
          );
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: mover.combatant_id, actor_name: mover.state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            feature_id: action.name, hp_before: before,
            hp_after: target.state.current_hp, is_dead: target.state.is_dead,
            damage_components: [{
              source: action.name, damage_type: spec.damageType,
              notation: `${spec.diceCount}d${spec.diceSize}`,
              rolls, modifier: 0, total: raw, applied_total: applied,
            }],
            animation: action.animation || "feature",
            description: `${action.name}: ${mover.state.template.name} enters ${target.state.template.name}'s space, dealing ${applied} ${spec.damageType} damage`
              + (burning ? " and igniting the target." : "."),
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser creature-space entry failed.", { mover: mover?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CREATURE_SPACE_ENTRY = { resolve };
})();
