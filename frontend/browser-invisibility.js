(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { has: (state, id) => state.active_effect_ids.includes(id) };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];

  function canUse(state) {
    try {
      const profile = state.template.invisibilityAction;
      return Boolean(profile && E().available(state, profile.actionCost || "action") && !Q().has(state, "invisible"));
    } catch (error) {
      console.error("Browser invisibility legality failed.", error);
      throw error;
    }
  }

  function take(sequence, round, member, setup) {
    try {
      const profile = member.state.template.invisibilityAction;
      if (!profile || !canUse(member.state)) throw new Error("Invisibility action is not legal.");
      const affected = states(setup);
      if (profile.concentration) C().start(member.state, member.combatant_id, profile.id, round, affected);
      const applied = T().apply(member.state, "invisible", member.combatant_id, {
        sourceEffectId: profile.id, appliedRound: round,
      });
      if (!applied) throw new Error("Invisibility could not be applied.");
      E().spend(member.state, profile.actionCost || "action");
      return {
        sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: member.state.template.name, target_id: member.combatant_id,
        target_name: member.state.template.name, applied_condition_ids: ["invisible"], feature_id: profile.id,
        concentration_started_effect_id: profile.concentration ? profile.id : null, animation: "invisibility",
        description: `${member.state.template.name} uses ${profile.name} and becomes Invisible.`,
      };
    } catch (error) {
      console.error("Browser invisibility action failed.", error);
      throw error;
    }
  }

  function breakAfterAttack(state, setup) {
    try {
      const profile = state.template.invisibilityAction;
      if (!profile?.endsOnAttack || !Q().has(state, "invisible")) return false;
      const effect = state.timed_effects.find((item) => item.effect_id === "invisible" && item.source_effect_id === profile.id);
      if (!effect) return false;
      const affected = states(setup);
      if (state.concentration?.effect_id === profile.id) return C().end(state, affected);
      T().removeGroup(state, effect);
      return true;
    } catch (error) {
      console.error("Browser attack-triggered invisibility cleanup failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_INVISIBILITY = { breakAfterAttack, canUse, take };
})();