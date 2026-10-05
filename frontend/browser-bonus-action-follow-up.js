(() => {
  "use strict";

  const D = () => window.IRON_PIT_BROWSER_DODGE;
  const Dice = () => window.IRON_PIT_DICE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TACTICAL_ACTIONS;
  const A = () => window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT;

  function resolve(sequence, round, member, triggeringFeatureId, turnKey) {
    try {
      if (!triggeringFeatureId || member.state.bonus_action_available) return null;
      const rules = member.state.template.bonus_action_follow_up_tactical_grants || [];
      for (const rule of rules) {
        if (member.state.feature_last_turn_keys?.[rule.source_id] === turnKey) continue;
        if ((rule.excluded_trigger_ids || []).includes(triggeringFeatureId)) continue;
        const grant = (T()?.grants(member) || []).find((item) => item.id === rule.tactical_grant_id);
        if (!grant) throw new Error(
          `${rule.source_name} references missing tactical grant ${rule.tactical_grant_id}.`,
        );
        if (grant.resourceId) throw new Error(
          `${rule.source_name} follow-up tactical grant must be resource-free.`,
        );

        const effects = grant.effects || [];
        let movement = 0;
        if (effects.includes("dash")) {
          movement = M().effectiveSpeed(member.state);
          member.state.movement_remaining_ft += movement;
          member.state.dash_uses_this_turn = (member.state.dash_uses_this_turn || 0) + 1;
        }
        if (effects.includes("disengage")) member.state.disengaged_this_turn = true;
        if (effects.includes("dodge")) D()?.applyEffect(member.state);

        const temporaryHpBefore = member.state.temporary_hp || 0;
        let temporaryHpAfter = temporaryHpBefore;
        if ((grant.temporaryHpDiceCount || 0) > 0) {
          if (!Dice()?.roll || !S()?.grantTemporaryHp) {
            throw new Error("Bonus Action follow-up Temporary HP requires dice and state APIs.");
          }
          let amount = 0;
          for (let index = 0; index < grant.temporaryHpDiceCount; index += 1) {
            amount += Dice().roll(grant.temporaryHpDiceSize);
          }
          temporaryHpAfter = S().grantTemporaryHp(member.state, amount);
        }

        member.state.feature_last_turn_keys = member.state.feature_last_turn_keys || {};
        member.state.feature_last_turn_keys[rule.source_id] = turnKey;
        return {
          sequence,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: member.state.template.name,
          feature_id: rule.source_id,
          movement_ft: movement,
          ...((grant.temporaryHpDiceCount || 0) > 0 ? {
            temporary_hp_before: temporaryHpBefore,
            temporary_hp_after: temporaryHpAfter,
          } : {}),
          applied_condition_ids: effects.includes("dodge") ? ["dodge"] : [],
          animation: effects.includes("dash") ? "movement" : "dodge",
          description: member.state.template.name + " uses " + rule.source_name
            + " to use " + grant.name + ": "
            + effects.map((item) => item[0].toUpperCase() + item.slice(1)).join(", ") + ".",
        };
      }
      return null;
    } catch (error) {
      console.error("Failed browser Bonus Action follow-up", {
        member: member?.combatant_id, triggeringFeatureId, error,
      });
      throw error;
    }
  }
  

  function resolveMovement(sequence, round, member, setup, triggeringFeatureId, turnKey) {
    try {
      if (!triggeringFeatureId || member.state.bonus_action_available) return { events: [], sequence };
      const rules = member.state.template.bonus_action_follow_up_movement_grants || [];
      for (const rule of rules) {
        if (!(rule.required_trigger_ids || []).includes(triggeringFeatureId)) continue;
        if (member.state.feature_last_turn_keys?.[rule.source_id] === turnKey) continue;
        if (!A()) throw new Error(`${rule.source_name} requires browser-activation-movement.js.`);
        const moved = A().resolve(sequence, round, member, setup, {
          speedFraction: rule.speed_fraction,
          desiredDistanceFt: rule.desired_distance_ft,
          provokesOpportunityAttacks: rule.provokes_opportunity_attacks !== false,
          turnKey,
        });
        if (!moved.events.length) return { events: [], sequence };
        for (const event of moved.events) {
          if (event.event_type === "movement") {
            event.feature_id = rule.source_id;
            event.description = `${rule.source_name}: ${event.description}`;
          }
        }
        member.state.feature_last_turn_keys = member.state.feature_last_turn_keys || {};
        member.state.feature_last_turn_keys[rule.source_id] = turnKey;
        return moved;
      }
      return { events: [], sequence };
    } catch (error) {
      console.error("Failed browser Bonus Action follow-up movement", {
        member: member?.combatant_id, triggeringFeatureId, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BONUS_ACTION_FOLLOW_UP = { resolve, resolveMovement };
})();
