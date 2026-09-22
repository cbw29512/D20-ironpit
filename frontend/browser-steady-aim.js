(() => {
  "use strict";

  const EFFECT = "stationary-attack-advantage";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function choice(member, setup) {
    try {
      const state = member.state;
      if (!state.template.stationary_bonus_action_next_attack_advantage) return null;
      if (!E()?.available(state, "bonus_action")) return null;
      const speed = M()?.effectiveSpeed(state);
      if (!Number.isFinite(speed) || state.movement_remaining_ft !== speed) return null;
      const selected = F()?.chooseStandardAttack(member, setup);
      if (!selected) return null;
      if (M().nextAttackAgainstAdvantage(state, selected.target.combatant_id) > 0) return null;
      return selected;
    } catch (error) {
      console.error("Failed stationary attack advantage choice", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, featureId = "steady-aim") {
    try {
      const selected = choice(member, setup);
      if (!selected) return null;
      const state = member.state;
      E().spend(state, "bonus_action");
      state.movement_remaining_ft = 0;
      M().add(state, {
        id: `${member.combatant_id}:${EFFECT}:${selected.target.combatant_id}`,
        source_id: member.combatant_id,
        source_effect_id: featureId,
        kind: "next-attack-against-advantage",
        flat_bonus: 0,
        target_id: selected.target.combatant_id,
        expires_source_turn_end_round: round,
      });
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: state.template.name,
        target_id: selected.target.combatant_id, target_name: selected.target.state.template.name,
        feature_id: featureId, animation: "focus",
        description: `${state.template.name} gives up movement to focus on ${selected.target.state.template.name}.`,
      };
    } catch (error) {
      console.error("Failed stationary attack advantage resolution", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Stationary attack advantage requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "steady-aim")) return;
    hooks.registerAbility(phase, {
      id: "steady-aim", priority: 25, rulesets: ["2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "afterEscape",
      resolve: ({ sequence, round, member, setup }) => {
        const event = resolve(sequence, round, member, setup, "steady-aim");
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_STATIONARY_ATTACK_ADVANTAGE = {
    choice, resolve, installAbilityHooks,
  };
})();