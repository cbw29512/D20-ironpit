(() => {
  "use strict";

  function removed(state) {
    return (state.timed_effects || []).some((effect) => effect.removed_from_battlefield);
  }

  function emitted(action) {
    return action.emittedEnvironmentContexts || action.emitted_environment_contexts || [];
  }

  function reactions(member) {
    const template = member?.state?.template || {};
    return template.environment_context_reactions || template.environmentContextReactions || [];
  }

  function activeActions(source) {
    try {
      const activeIds = new Set(
        (source.state.timed_effects || [])
          .filter((effect) => effect.source_id === source.combatant_id && effect.source_effect_id)
          .map((effect) => effect.source_effect_id),
      );
      return (source.state.template.timed_self_buff_actions || []).filter(
        (action) => activeIds.has(action.id) && emitted(action).length,
      );
    } catch (error) {
      console.error("Failed to discover emitted environment contexts.", { source: source?.combatant_id, error });
      throw error;
    }
  }

  function inside(actor, setup, contextId) {
    try {
      if (!setup) return false;
      const distance = window.IRON_PIT_BROWSER_STATE?.distance;
      if (!distance) throw new Error("Environment context coverage requires browser-state distance.");
      for (const source of [...(setup.heroes || []), ...(setup.monsters || [])]) {
        if (removed(source.state)) continue;
        for (const action of activeActions(source)) {
          for (const context of emitted(action)) {
            if ((context.context_id || context.contextId) !== contextId) continue;
            if (distance(source, actor) <= (context.radius_ft || context.radiusFt)) return true;
          }
        }
      }
      return false;
    } catch (error) {
      console.error("Failed to test environment context coverage.", {
        actor: actor?.combatant_id, contextId, error,
      });
      throw error;
    }
  }

  function disadvantageSources(actor, setup, rollKind) {
    try {
      if (!setup) return 0;
      let count = 0;
      for (const reaction of reactions(actor)) {
        const kinds = reaction.disadvantage_on || reaction.disadvantageOn || [];
        if (!kinds.includes(rollKind)) continue;
        if (inside(actor, setup, reaction.context_id || reaction.contextId)) count += 1;
      }
      return count;
    } catch (error) {
      console.error("Failed to count environment-context Disadvantage.", {
        actor: actor?.combatant_id, rollKind, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS = { disadvantageSources, inside };
})();
