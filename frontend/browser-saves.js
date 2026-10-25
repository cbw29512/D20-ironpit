(() => {
  "use strict";

  const support = window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT;
  const damageRuntime = window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY;
  const savingThrows = window.IRON_PIT_BROWSER_SAVING_THROWS;
  if (!support?.legalAction || !support?.resolveOnHitConditionSave) {
    throw new Error("Browser save-action support runtime is unavailable.");
  }
  if (!damageRuntime?.resolveAndApply) {
    throw new Error("Browser save-damage application runtime is unavailable.");
  }
  if (!savingThrows?.resolveSavingThrow || !savingThrows?.saveMode) {
    throw new Error("Browser saving-throw runtime is unavailable.");
  }

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    try {
      const spendAction = options.spendAction !== false;
      const checkResource = options.checkResource !== false;
      const economy = window.IRON_PIT_ACTION_ECONOMY || {
        available: (state, cost) => cost === "action" && state.action_available,
        spend: (state) => { state.action_available = false; },
      };
      const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES || {
        canSee: () => true,
      };
      if (action.openingInitiativeOnly
        && !window.IRON_PIT_BROWSER_CHARGE?.openingEligible(
          round, actor, options.setup,
        )) {
        throw new Error(
          `${action.name} requires an initiative-winning opening turn.`,
        );
      }
      const actionCost = action.actionCost || "action";
      if (spendAction && !economy.available(actor.state, actionCost)) {
        throw new Error(`${actionCost} is unavailable for ${action.name}.`);
      }
      if (checkResource && action.resourceId
        && (actor.state.resources[action.resourceId] || 0)
          < (action.resourceCost || 1)) {
        throw new Error(`${action.name} resource is unavailable.`);
      }
      if (!support.legalAction(
        action, target, distance, actor.combatant_id, actor,
      )) {
        throw new Error(
          `${action.name} has no legal target at ${distance} feet.`,
        );
      }
      if (action.requiresTargetSight
        && !conditions.canSee(actor.state, target.state, distance)) {
        throw new Error(`${action.name} requires the actor to see the target.`);
      }

      const effectTags = [...new Set([
        ...(action.effectTags || [])
          .map((tag) => String(tag).trim().toLowerCase()).filter(Boolean),
        ...(String(action.damageType || "").trim().toLowerCase() === "poison"
          ? ["poison"] : []),
      ])];
      const saveContext = {
        magicalEffect: Boolean(action.magicalEffect),
        spellEffect: Boolean(options.spellEffect),
        sourceCreatureType: actor.state.template.creature_type || null,
        effectTags,
        roundNumber: round,
        disadvantageSources: [...(options.saveDisadvantageSources || [])],
        advantageSources: [...(options.saveAdvantageSources || [])],
        encounterRoller: target,
        setup: options.setup || null,
      };
      if (action.saveAbilityChoices?.length) {
        const chooser = window.IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE;
        if (!chooser?.choose) {
          throw new Error("Target-chosen saving throw runtime unavailable.");
        }
        action = {
          ...action,
          saveAbility: chooser.choose(
            target.state, action.saveAbilityChoices, action.dc, saveContext,
          ),
        };
      }

      const targetType = String(target.state.template.creature_type || "")
        .split(" (")[0].trim().toLowerCase();
      const automaticTypes = (action.automaticFailureCreatureTypes || [])
        .map((kind) => String(kind).trim().toLowerCase()).filter(Boolean);
      const automaticallyFails = Boolean(
        targetType && automaticTypes.includes(targetType),
      );
      const defensive = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS || {
        saveAdvantageSourceNames: () => [],
      };
      const advantageSources = automaticallyFails ? [] : [
        ...(defensive.saveAdvantageSourceNames?.(
          target.state, action.saveAbility, saveContext,
        ) || []),
        ...(saveContext.advantageSources || []),
      ];
      const save = automaticallyFails
        ? { roll: null, succeeded: false }
        : savingThrows.resolveSavingThrow(
          target.state, action.saveAbility, action.dc, saveContext,
        );

      let resourceRemaining = options.resourceRemaining ?? null;
      if (action.resourceId && options.spendResource !== false) {
        actor.state.resources[action.resourceId] -= action.resourceCost || 1;
        resourceRemaining = actor.state.resources[action.resourceId];
      }
      if (spendAction) economy.spend(actor.state, actionCost);

      const hpBefore = target.state.current_hp;
      const temporaryHpBefore = target.state.temporary_hp;
      const deathSuccessBefore = target.state.death_save_successes;
      const deathFailureBefore = target.state.death_save_failures;
      const concentrationBefore = target.state.concentration?.effect_id || null;
      const damage = damageRuntime.resolveAndApply(
        target, action, save.succeeded, {
          sharedDamageRolls: options.sharedDamageRolls,
          setup: options.setup || null,
        },
      );

      const riderRuntime = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
      const sharedImmunity = window.IRON_PIT_BROWSER_SAVE_IMMUNITY;
      let appliedConditions = [];
      if (save.succeeded && action.sourceEffectImmunityOnSuccess) {
        if (!riderRuntime?.grantImmunity) {
          throw new Error("Source save-immunity runtime is unavailable.");
        }
        riderRuntime.grantImmunity(
          target.state, action.id, actor.combatant_id, round, {
            sourceTemplate: actor.state.template,
            sourceIsMagical: Boolean(action.magicalEffect),
          },
        );
      }
      if (save.succeeded
        && (action.sourceEffectImmunityKeysOnSuccess || []).length) {
        if (!sharedImmunity?.grantSharedImmunities) {
          throw new Error("Shared save-immunity grant runtime is unavailable.");
        }
        sharedImmunity.grantSharedImmunities(
          target.state,
          action.sourceEffectImmunityKeysOnSuccess,
          actor.combatant_id,
          round,
          {
            sourceTemplate: actor.state.template,
            sourceIsMagical: Boolean(action.magicalEffect),
          },
        );
      }
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && action.failedSaveTimedEffect) {
        if (!riderRuntime?.apply) {
          throw new Error("Failed-save timed-effect runtime is unavailable.");
        }
        const applied = riderRuntime.apply(
          actor, target, action, action.failedSaveTimedEffect,
          round, options.setup || null, save.roll?.total ?? null,
        );
        if (Array.isArray(applied)) appliedConditions.push(...applied);
        else if (applied) appliedConditions.push(applied);
      }
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && action.grappleEscapeDc) {
        appliedConditions = window.IRON_PIT_BROWSER_GRAPPLE.apply(
          target.state,
          actor.combatant_id,
          action.grappleEscapeDc,
          action.range,
          Boolean(action.restrainsWhileGrappled),
          Boolean(action.magicalEffect),
        );
      }
      let pushedFt = 0;
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && (action.failedSavePushFt || 0) > 0) {
        const movement = window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
        if (!options.setup || !movement) {
          throw new Error(
            `${action.name} forced movement requires encounter setup.`,
          );
        }
        pushedFt = movement.pushStraightAway(
          target, actor, options.setup, action.failedSavePushFt,
        );
      }

      const survivalLog =
        window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(target.state) || "";
      let description = automaticallyFails
        ? `${target.state.template.name} automatically FAILS a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name} because its creature type is ${target.state.template.creature_type}.`
        : `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
      if (advantageSources.length) {
        description += ` ${advantageSources.join(" and ")} grants Advantage on the save.`;
      }
      if (saveContext.disadvantageSources.length) {
        description += ` ${saveContext.disadvantageSources.join(" and ")} imposes Disadvantage on the save.`;
      }
      const override = save.roll
        ? window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE?.sourceNameForRoll(
          target.state, save.roll,
        ) : null;
      if (override) {
        description += ` ${override} turns the failed saving throw roll into a 20.`;
      }
      if (save.roll?.outcome_override_name) {
        description += ` ${save.roll.outcome_override_name} turns the failure into a success (${save.roll.outcome_override_uses_remaining} uses remain).`;
      }
      if (target.state.template.evasion && action.saveAbility === "dexterity"
        && action.successDamage === "half") {
        description += " Evasion reduces the damage.";
      }
      if (damage.damageOutcome === "undead_fortitude") {
        description += ` ${target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
      }
      if (appliedConditions.includes("grappled")) {
        description += ` ${target.state.template.name} is Grappled.`;
      }
      if (appliedConditions.includes("restrained")) {
        description += ` ${target.state.template.name} is Restrained while Grappled.`;
      }
      if (pushedFt) {
        description += ` ${target.state.template.name} is pushed ${pushedFt} feet away.`;
      }
      if (!save.succeeded && action.failureSetsZeroHp) {
        description += ` ${target.state.template.name} drops directly to 0 HP (not damage).`;
      }

      return {
        sequence, round_number: round, event_type: "saving_throw",
        actor_id: actor.combatant_id, actor_name: actor.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: action.saveAbility,
        save_dc: action.dc, save_succeeded: save.succeeded,
        damage_roll: damage.roll, damage_components: damage.components,
        applied_condition_ids: appliedConditions,
        hp_before: hpBefore, hp_after: target.state.current_hp,
        temporary_hp_before: temporaryHpBefore,
        temporary_hp_after: target.state.temporary_hp,
        death_save_successes_before: deathSuccessBefore,
        death_save_failures_before: deathFailureBefore,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable, is_dead: target.state.is_dead,
        feature_id: action.id, resource_remaining: resourceRemaining,
        concentration_ended_effect_id:
          concentrationBefore && !target.state.concentration
            ? concentrationBefore : null,
        animation: action.animation || "save-effect",
        description: description + survivalLog
          + (window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT
            ?.consumeLog(target.state) || ""),
      };
    } catch (error) {
      console.error("Browser save-action resolution failed", {
        actionId: action?.id,
        actor: actor?.combatant_id,
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVES = {
    legalAction: support.legalAction,
    resolveAction,
    resolveOnHitConditionSave: support.resolveOnHitConditionSave,
    resolveSavingThrow: savingThrows.resolveSavingThrow,
    saveMode: savingThrows.saveMode,
  };
})();
