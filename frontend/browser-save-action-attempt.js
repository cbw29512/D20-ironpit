(() => {
  "use strict";

  function resolveAttempt(actor, target, action, round, options = {}) {
    try {
      const savingThrows = window.IRON_PIT_BROWSER_SAVING_THROWS;
      if (!savingThrows?.resolveSavingThrow) {
        throw new Error("Browser saving-throw runtime is unavailable.");
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
      let activeAction = action;
      if (action.saveAbilityChoices?.length) {
        const chooser = window.IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE;
        if (!chooser?.choose) {
          throw new Error("Target-chosen saving throw runtime unavailable.");
        }
        activeAction = {
          ...action,
          saveAbility: chooser.choose(
            target.state, action.saveAbilityChoices, action.dc, saveContext,
          ),
        };
      }
      const targetType = String(target.state.template.creature_type || "")
        .split(" (")[0].trim().toLowerCase();
      const automaticTypes = (activeAction.automaticFailureCreatureTypes || [])
        .map((kind) => String(kind).trim().toLowerCase()).filter(Boolean);
      const automaticallyFails = Boolean(
        targetType && automaticTypes.includes(targetType),
      );
      const defensive = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS || {
        saveAdvantageSourceNames: () => [],
      };
      const advantageSources = automaticallyFails ? [] : [
        ...(defensive.saveAdvantageSourceNames?.(
          target.state, activeAction.saveAbility, saveContext,
        ) || []),
        ...(saveContext.advantageSources || []),
      ];
      const save = automaticallyFails
        ? { roll: null, succeeded: false }
        : savingThrows.resolveSavingThrow(
          target.state, activeAction.saveAbility, activeAction.dc, saveContext,
        );
      return {
        action: activeAction,
        saveContext,
        automaticallyFails,
        advantageSources,
        save,
      };
    } catch (error) {
      console.error("Browser save-attempt resolution failed", {
        actionId: action?.id,
        actor: actor?.combatant_id,
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_ACTION_ATTEMPT = { resolveAttempt };
})();
