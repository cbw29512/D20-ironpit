(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;

  function targetCanGain(state, action) {
    const current = state.resources[action.targetResourceId];
    const maximum = state.template.resources?.[action.targetResourceId];
    if (!Number.isInteger(current) || !Number.isInteger(maximum)) {
      throw new Error(`Resource conversion target ${action.targetResourceId} is missing.`);
    }
    return action.targetAllowsOverflow || current < maximum;
  }

  function available(state, action) {
    try {
      if (!E()?.available(state, action.actionCost)) return false;
      if (!R()?.available(state, action.sourceResourceId, action.sourceCost)) return false;
      return targetCanGain(state, action);
    } catch (error) {
      console.error("Browser resource conversion availability failed", {
        actionId: action?.id, combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function gain(state, action) {
    const current = state.resources[action.targetResourceId];
    const maximum = state.template.resources[action.targetResourceId];
    const gained = current + action.targetGain;
    state.resources[action.targetResourceId] = action.targetAllowsOverflow
      ? gained
      : Math.min(gained, maximum);
    return state.resources[action.targetResourceId];
  }

  function resolve(sequence, round, member, action) {
    try {
      const state = member.state;
      if (!available(state, action)) return null;
      E().spend(state, action.actionCost);
      const sourceRemaining = R().spend(state, action.sourceResourceId, action.sourceCost);
      const targetRemaining = gain(state, action);
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: member.combatant_id,
        actor_name: state.template.name,
        feature_id: action.id,
        resource_remaining: sourceRemaining,
        animation: "resource-conversion",
        description: `${state.template.name} uses ${action.name}, spending ${action.sourceCost} ${action.sourceResourceId} and gaining ${action.targetGain} ${action.targetResourceId} (${targetRemaining} available).`,
      };
    } catch (error) {
      console.error("Browser resource conversion resolution failed", {
        actionId: action?.id, combatant: member?.state?.template?.name, error,
      });
      throw error;
    }
  }

  function allSpellSlotsEmpty(state) {
    const slotIds = Object.keys(state.resources).filter((id) => id.startsWith("spell-slot-"));
    return slotIds.length > 0 && slotIds.every((id) => state.resources[id] <= 0);
  }

  function automaticAction(state) {
    try {
      const actions = state.template.resource_conversion_actions || [];
      return actions
        .filter((action) => action.automation === "when-all-spell-slots-empty")
        .filter((action) => allSpellSlotsEmpty(state) && available(state, action))
        .sort((a, b) => (b.priority || 0) - (a.priority || 0))[0] || null;
    } catch (error) {
      console.error("Browser automatic resource conversion selection failed", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Resource conversion hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "resource-conversion")) return;
    hooks.registerAbility(phase, {
      id: "resource-conversion",
      priority: 30,
      rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
      resolve: ({ sequence, round, member }) => {
        const action = automaticAction(member.state);
        if (!action) return null;
        const event = resolve(sequence, round, member, action);
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_RESOURCE_CONVERSION = {
    allSpellSlotsEmpty, automaticAction, available, installAbilityHooks, resolve,
  };
})();
