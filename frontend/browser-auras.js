(() => {
  "use strict";
  const O = () => window.IRON_PIT_BROWSER_ONGOING_DAMAGE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const incapacitated = (state) => state.active_effect_ids?.includes("incapacitated") || state.is_unconscious || state.is_dead;

  function turnStart(sequence, round, target, setup) {
    const events = [];
    for (const source of members(setup)) {
      if (source.combatant_id === target.combatant_id || source.state.is_dead || !source.state.is_alive) continue;
      for (const aura of source.state.template.start_turn_save_condition_auras || []) {
        if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
        if (S().distance(source, target) > aura.radius_ft) continue;
        const save = V().resolveSavingThrow(target.state, aura.save_ability, aura.dc, Boolean(aura.magical_effect));
        const applied = [];
        if (!save.succeeded) {
          const condition = T().apply(target.state, aura.condition, source.combatant_id, {
            sourceEffectId: aura.id, appliedRound: round, expiryTiming: aura.expiry_timing,
          });
          if (condition) applied.push(condition);
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: aura.save_ability, save_dc: aura.dc,
          save_succeeded: save.succeeded, applied_condition_ids: applied, feature_id: aura.id,
          animation: "aura-condition", description: `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${aura.dc} ${aura.save_ability} save against ${source.state.template.name}'s ${aura.name}.`,
        });
      }
    }
    return { events, sequence };
  }

  function turnEnd(sequence, round, source, setup) {
    const events = [];
    if (source.state.is_dead || !source.state.is_alive) return { events, sequence };
    for (const aura of source.state.template.end_turn_damage_auras || []) {
      if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
      const targets = members(setup).filter((member) =>
        member.side !== source.side && member.state.is_alive && !member.state.is_dead && S().distance(source, member) <= aura.radius_ft
      );
      for (const target of targets) {
        events.push(O().resolve(sequence++, round, source, target, setup, {
          featureId: aura.id, featureName: aura.name, diceCount: aura.damage_dice_count,
          diceSize: aura.damage_dice_size, damageBonus: aura.damage_bonus || 0,
          damageType: aura.damage_type, animation: "aura-damage",
        }));
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_AURAS = { turnEnd, turnStart };
})();
