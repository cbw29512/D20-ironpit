(() => {
  "use strict";

  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Emanation damage requires the shared damage resolver.");
    return rules;
  };

  function resolveHit(sequence, round, source, target, action, setup, turnKey) {
    try {
      const emanation = action.startTurnEmanationDamage;
      if (!emanation) return { event: null, sequence };
      const key = `${source.combatant_id}:${action.id}`;
      target.state.emanation_triggers_this_turn = target.state.emanation_triggers_this_turn || {};
      if (target.state.emanation_triggers_this_turn[key] === turnKey) return { event: null, sequence };
      const distance = window.IRON_PIT_BROWSER_STATE.distance(source, target);
      if (distance > emanation.radius_ft) return { event: null, sequence };
      target.state.emanation_triggers_this_turn[key] = turnKey;
      const D = window.IRON_PIT_DICE;
      let rolls = [];
      let raw = emanation.fixed_damage || 0;
      let notation = String(emanation.fixed_damage || 0);
      if (emanation.dice_count) {
        rolls = D.rollMany(emanation.dice_count, emanation.dice_size || 8);
        raw = rolls.reduce((sum, roll) => sum + roll, 0);
        notation = `${emanation.dice_count}d${emanation.dice_size || 8}`;
      }
      let succeeded = false;
      let saveRoll = null;
      if (emanation.save_ability && emanation.save_dc != null) {
        const save = window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(
          target.state, emanation.save_ability, emanation.save_dc,
          { magicalEffect: true, spellEffect: true, encounterRoller: target, setup },
        );
        saveRoll = save.roll;
        succeeded = save.succeeded;
        if (succeeded && emanation.success_damage === "none") raw = 0;
        else if (succeeded && emanation.success_damage === "half") raw = Math.floor(raw / 2);
      }
      const hpBefore = target.state.current_hp;
      const resolvedDamage = raw
        ? DD().resolveDamage(target.state, raw, emanation.damage_type)
        : { applied: 0, healed: 0, sourceName: null };
      const applied = resolvedDamage.applied;
      if (applied) {
        window.IRON_PIT_BROWSER_ATTACK.applyDamage(
          target.state, applied, false, [emanation.damage_type],
          [...setup.heroes, ...setup.monsters].map((member) => member.state), setup,
        );
      }
      return {
        event: {
          sequence, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: saveRoll, save_ability: emanation.save_ability || null,
          save_dc: emanation.save_dc || null, save_succeeded: emanation.save_ability ? succeeded : null,
          damage_roll: { notation, rolls, modifier: 0, total: applied },
          damage_components: [{
            source: action.name, notation, rolls, modifier: 0,
            damage_type: emanation.damage_type, total: raw, applied_total: applied,
          }],
          hp_before: hpBefore, hp_after: target.state.current_hp,
          feature_id: action.id, animation: action.animation || "radiant-aura",
          distance_before_ft: distance,
          description: `${target.state.template.name} is caught in ${source.state.template.name}'s ${action.name} and takes ${applied} ${emanation.damage_type} damage.`
            + (resolvedDamage.sourceName ? ` ${resolvedDamage.sourceName} restores ${resolvedDamage.healed} HP.` : ""),
        },
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Emanation hit failed.", { target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_EMANATION_SAVE_DAMAGE = { resolveHit };
})();
