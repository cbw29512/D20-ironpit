(() => {
  "use strict";

  function build(
    sequence, round, actor, target, action, attempt, damage, effects, snapshot,
  ) {
    try {
      const save = attempt.save;
      const context = attempt.saveContext;
      let description = attempt.automaticallyFails
        ? `${target.state.template.name} automatically FAILS a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name} because its creature type is ${target.state.template.creature_type}.`
        : `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
      if (attempt.advantageSources.length) {
        description +=
          ` ${attempt.advantageSources.join(" and ")} grants Advantage on the save.`;
      }
      if (context.disadvantageSources.length) {
        description +=
          ` ${context.disadvantageSources.join(" and ")} imposes Disadvantage on the save.`;
      }
      const override = save.roll
        ? window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE?.sourceNameForRoll(
          target.state, save.roll,
        ) : null;
      if (override) {
        description +=
          ` ${override} turns the failed saving throw roll into a 20.`;
      }
      if (save.roll?.outcome_override_name) {
        description +=
          ` ${save.roll.outcome_override_name} turns the failure into a success (${save.roll.outcome_override_uses_remaining} uses remain).`;
      }
      if (target.state.template.evasion && action.saveAbility === "dexterity"
        && action.successDamage === "half") {
        description += " Evasion reduces the damage.";
      }
      if (damage.damageOutcome === "undead_fortitude") {
        description +=
          ` ${target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
      }
      if (effects.appliedConditions.includes("grappled")) {
        description += ` ${target.state.template.name} is Grappled.`;
      }
      if (effects.appliedConditions.includes("restrained")) {
        description +=
          ` ${target.state.template.name} is Restrained while Grappled.`;
      }
      if (effects.pushedFt) {
        description +=
          ` ${target.state.template.name} is pushed ${effects.pushedFt} feet away.`;
      }
      if (!save.succeeded && action.failureSetsZeroHp) {
        description +=
          ` ${target.state.template.name} drops directly to 0 HP (not damage).`;
      }
      description +=
        window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(target.state) || "";
      description +=
        window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(target.state) || "";

      return {
        sequence,
        round_number: round,
        event_type: "saving_throw",
        actor_id: actor.combatant_id,
        actor_name: actor.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        saving_throw_roll: save.roll,
        save_ability: action.saveAbility,
        save_dc: action.dc,
        save_succeeded: save.succeeded,
        damage_roll: damage.roll,
        damage_components: damage.components,
        applied_condition_ids: effects.appliedConditions,
        hp_before: snapshot.hpBefore,
        hp_after: target.state.current_hp,
        temporary_hp_before: snapshot.temporaryHpBefore,
        temporary_hp_after: target.state.temporary_hp,
        death_save_successes_before: snapshot.deathSuccessBefore,
        death_save_failures_before: snapshot.deathFailureBefore,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable,
        is_dead: target.state.is_dead,
        feature_id: action.id,
        resource_remaining: snapshot.resourceRemaining,
        concentration_ended_effect_id:
          snapshot.concentrationBefore && !target.state.concentration
            ? snapshot.concentrationBefore : null,
        animation: action.animation || "save-effect",
        description,
      };
    } catch (error) {
      console.error("Browser save-event construction failed", {
        actionId: action?.id,
        actor: actor?.combatant_id,
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_EVENT = { build };
})();
