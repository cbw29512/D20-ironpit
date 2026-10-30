(() => {
  "use strict";

  function resolveEndTurn(sequence, round, swallowed, setup) {
    try {
      const record = swallowed.state.swallowed;
      if (!record || !record.regurgitation_damage_threshold) return {events: [], sequence};

      const members = [...setup.heroes, ...setup.monsters];
      const owner = members.find(item => item.combatant_id === record.source_id);
      if (!owner || owner.state.is_dead || !owner.state.is_alive || owner.state.current_hp <= 0) {
        return {events: [], sequence};
      }

      const dealt = owner.state.damage_taken_this_turn_by_source?.[swallowed.combatant_id] || 0;
      if (dealt < record.regurgitation_damage_threshold) return {events: [], sequence};
      if (!record.regurgitation_save_ability || !record.regurgitation_save_dc) {
        throw new Error("Threshold regurgitation requires a save ability and DC.");
      }

      const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
      const swallow = window.IRON_PIT_BROWSER_SWALLOW;
      if (!saves?.resolveSavingThrow || !swallow?.release) {
        throw new Error("Threshold regurgitation requires shared save and Swallow runtimes.");
      }
      const save = saves.resolveSavingThrow(
        owner.state, record.regurgitation_save_ability, record.regurgitation_save_dc,
      );

      const released = [];
      if (!save.succeeded) {
        let targets = members.filter(item =>
          item.state.swallowed?.source_id === owner.combatant_id
        );
        if (!record.regurgitation_all_swallowed) targets = [swallowed];
        for (const target of targets) {
          if (swallow.release(
            owner.combatant_id, owner.state, target.combatant_id, target.state,
            target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0,
          )) released.push(target.combatant_id);
        }
      }

      return {
        events: [{
          sequence,
          round_number: round,
          event_type: "saving_throw",
          actor_id: owner.combatant_id,
          actor_name: owner.state.template.name,
          target_id: swallowed.combatant_id,
          target_name: swallowed.state.template.name,
          saving_throw_roll: save.roll,
          save_ability: record.regurgitation_save_ability,
          save_dc: record.regurgitation_save_dc,
          save_succeeded: save.succeeded,
          feature_id: record.source_name,
          removed_condition_ids: released.length ? ["blinded", "restrained"] : [],
          animation: "feature",
          description: `${owner.state.template.name} ${save.succeeded ? "keeps" : "regurgitates"} its swallowed creature after taking ${dealt} damage from ${swallowed.state.template.name} during that turn.`,
        }],
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Browser Swallow threshold regurgitation failed.", {
        swallowed: swallowed?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SWALLOW_REGURGITATION = { resolveEndTurn };
})();
