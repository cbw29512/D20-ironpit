(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function resolve(sequence, round, member, target, attack, turnKey, setup) {
    try {
      const rider = member.state.template.resource_backed_on_hit_save_rider;
      if (!rider) return null;
      if (!(rider.trigger_attack_ids || []).includes(attack.id)) return null;
      if (target.state.current_hp <= 0 || target.state.is_dead || !target.state.is_alive) return null;
      if (rider.once_per_turn && member.state.feature_last_turn_keys?.[rider.source_id] === turnKey) return null;
      if (!R().available(member.state, rider.resource_id, rider.resource_cost || 1)) return null;

      const remaining = R().spend(member.state, rider.resource_id, rider.resource_cost || 1);
      member.state.feature_last_turn_keys ||= {};
      if (rider.once_per_turn) member.state.feature_last_turn_keys[rider.source_id] = turnKey;

      const save = V().resolveSavingThrow(target.state, rider.save_ability, rider.save_dc, {
        conditionId: rider.failed_condition_id || null,
        roundNumber: round,
        encounterRoller: target,
        setup,
      });

      const applied = [];
      if (!save.succeeded && rider.failed_condition_id) {
        if (!T()) throw new Error("Resource-backed on-hit save requires browser timed-condition runtime.");
        const effect = T().apply(target.state, rider.failed_condition_id, member.combatant_id, {
          sourceEffectId: rider.source_id,
          sourceTemplate: member.state.template,
          appliedRound: round,
          expiryTiming: rider.failed_condition_expiry_timing || null,
          useDefaultPoisonRecovery: false,
        });
        if (effect) applied.push(effect);
      }

      if (save.succeeded) {
        if (rider.successful_save_speed_multiplier != null) {
          M().add(target.state, {
            id: `${member.combatant_id}:${rider.source_id}:speed:${target.combatant_id}`,
            source_id: member.combatant_id,
            source_effect_id: rider.source_id,
            source_name: rider.source_name,
            kind: "speed-multiplier",
            flat_bonus: 0,
            multiplier: rider.successful_save_speed_multiplier,
            expires_at_start_of_source_turn: true,
          });
        }
        if (rider.successful_save_next_attack_advantage) {
          M().add(target.state, {
            id: `${member.combatant_id}:${rider.source_id}:next-attack:${target.combatant_id}`,
            source_id: member.combatant_id,
            source_effect_id: rider.source_id,
            source_name: rider.source_name,
            kind: "attacks-against-advantage",
            flat_bonus: 0,
            consume_on_attack_against: true,
            expires_at_start_of_source_turn: true,
          });
        }
      }

      let description = `${member.state.template.name} spends ${rider.resource_cost || 1} ${String(rider.resource_id).replaceAll("-", " ")} on ${rider.source_name}; ${target.state.template.name} ${save.succeeded ? "succeeds" : "fails"} the DC ${rider.save_dc} ${rider.save_ability} save.`;
      if (save.succeeded && rider.successful_save_speed_multiplier != null) description += " Speed is reduced.";
      if (save.succeeded && rider.successful_save_next_attack_advantage) description += " The next attack against the target has Advantage.";
      if (!save.succeeded && applied.length) description += ` ${target.state.template.name} gains ${applied.join(", ")}.`;

      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: rider.save_ability,
        save_dc: rider.save_dc, save_succeeded: save.succeeded,
        applied_condition_ids: applied, feature_id: rider.source_id,
        resource_remaining: remaining, animation: "stun", description,
      };
    } catch (error) {
      console.error("Browser resource-backed on-hit save failed", {
        actor: member?.combatant_id, target: target?.combatant_id, attack: attack?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE = { resolve };
})();