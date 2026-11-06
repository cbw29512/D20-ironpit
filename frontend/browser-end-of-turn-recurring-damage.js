(() => {
  "use strict";

  // One typed packet per active fight-local effect, at the target's turn end.
  function resolve(sequence, round, member, setup) {
    try {
      const events = [];
      const state = member.state;
      if (!state.is_alive || state.is_dead) return { events, sequence };
      const dice = window.IRON_PIT_DICE;
      const defenses = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
      const attack = window.IRON_PIT_BROWSER_ATTACK;
      if (!dice?.roll || !defenses?.resolveDamage || !attack?.applyDamage) {
        throw new Error("End-turn damage requires shared dice, defense and HP runtimes.");
      }
      const members = [...(setup.heroes || []), ...(setup.monsters || [])];
      const states = members.map((entry) => entry.state);
      for (const effect of [...(state.timed_effects || [])]) {
        if (!state.timed_effects.includes(effect) || !(effect.end_of_turn_dice_count > 0)) continue;
        if (!effect.end_of_turn_damage_type) throw new Error("Missing typed end-turn damage.");
        let total = 0;
        for (let i = 0; i < effect.end_of_turn_dice_count; i++) {
          total += dice.roll(effect.end_of_turn_dice_size);
        }
        const type = effect.end_of_turn_damage_type;
        const label = effect.source_name || effect.source_effect_id || effect.effect_id;
        const before = state.current_hp;
        const damage = defenses.resolveDamage(state, total, type);
        attack.applyDamage(state, damage.applied, false, [type], states, setup, [], effect.source_id);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: state.template.name,
          target_id: member.combatant_id, target_name: state.template.name,
          feature_id: effect.source_effect_id || effect.effect_id,
          hp_before: before, hp_after: state.current_hp, animation: "feature",
          description: `${label} deals ${damage.applied} ${type} damage to ${state.template.name} at turn end.`,
        });
        if (!state.is_alive || state.is_dead) break;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser end-turn recurring damage failed.", { target: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_END_TURN_RECURRING_DAMAGE = { resolve };
})();
