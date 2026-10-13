(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function eligible(source, target) {
    try {
      const rule = source.state.template.turn_start_save_reaction;
      if (!rule || rule.trigger !== "other_creature_turn_start") return false;
      if (source.combatant_id === target.combatant_id || source.side === target.side) return false;
      if (!source.state.is_alive || source.state.is_dead || source.state.current_hp <= 0) return false;
      if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
      if (!E().available(source.state, "reaction")) return false;
      const distance = S().distance(source, target);
      if (distance > rule.range_ft) return false;
      if (rule.source_must_see_target && !Q().canSee(source.state, target.state, distance)) return false;
      if (rule.target_must_see_source && !Q().canSee(target.state, source.state, distance)) return false;
      return true;
    } catch (error) {
      console.error("Failed turn-start Reaction eligibility.", { source: source?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, target, setup) {
    try {
      const events = [];
      const enemies = target.side === "heroes" ? setup.monsters : setup.heroes;
      for (const source of enemies) {
        if (!eligible(source, target)) continue;
        const rule = source.state.template.turn_start_save_reaction;
        const save = V().resolveSavingThrow(target.state, rule.save_ability, rule.save_dc, {
          conditionId: rule.failure_condition, effectTags: [rule.failure_condition],
          roundNumber: round, encounterRoller: target, setup,
        });
        E().spend(source.state, "reaction");
        const applied = [];
        if (!save.succeeded) {
          const condition = T().apply(target.state, rule.failure_condition, source.combatant_id, {
            sourceEffectId: rule.source_id, sourceTemplate: source.state.template,
            appliedRound: round, expiryTiming: rule.expires_at,
            affectedStates: [...setup.heroes, ...setup.monsters].map((member) => member.state),
          });
          if (condition) applied.push(condition);
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: rule.save_ability, save_dc: rule.save_dc,
          save_succeeded: save.succeeded, applied_condition_ids: applied,
          feature_id: rule.source_id, animation: "condition",
          description: source.state.template.name + " uses " + rule.source_name + " on " + target.state.template.name + ".",
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed turn-start Reaction resolution.", { target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_SAVE_REACTIONS = { eligible, resolve };
})();
