(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Start-of-turn damage requires the shared damage resolver.");
    return rules;
  };
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function resolve(sequence, round, member, setup) {
    try {
      const events = [];
      const states = members(setup).map((item) => item.state || item);
      for (const effect of [...(member.state.timed_effects || [])]) {
        if ((effect.start_of_turn_dice_count || 0) <= 0 || !effect.start_of_turn_damage_type) continue;
        let total = 0;
        for (let index = 0; index < effect.start_of_turn_dice_count; index += 1) {
          total += D().roll(effect.start_of_turn_dice_size || 6);
        }
        const damageType = effect.start_of_turn_damage_type;
        const hpBefore = member.state.current_hp;
        const applied = DD().resolveDamage(member.state, total, damageType).applied;
        A().applyDamage(
          member.state, applied, false, [damageType], states, setup,
        );
        const name = effect.source_effect_id || effect.effect_id;
        events.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: member.state.template.name,
          target_id: member.combatant_id,
          target_name: member.state.template.name,
          feature_id: name,
          hp_before: hpBefore,
          hp_after: member.state.current_hp,
          animation: "feature",
          description: `${name} deals ${applied} ${damageType} damage to ${member.state.template.name} at the start of the turn.`,
        });
        if (!(effect.start_of_turn_save_ends && effect.start_of_turn_save_ability && effect.start_of_turn_save_dc)) {
          continue;
        }
        const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
          member.state, effect.start_of_turn_save_ability, effect.start_of_turn_save_dc,
          { effect_tags: ["spell"], roundNumber: round },
        );
        if (!save.succeeded) continue;
        T().removeEffect(member.state, effect);
        for (const source of members(setup)) {
          const concentration = source.state.concentration;
          if (!concentration) continue;
          if (concentration.source_id === effect.source_id && concentration.effect_id === effect.source_effect_id) {
            C().end(source.state, states);
          }
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Start-of-turn timed burn failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN = { resolve };
})();
