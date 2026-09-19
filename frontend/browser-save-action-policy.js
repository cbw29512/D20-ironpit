(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function choose(member, setup) {
    try {
      for (const target of F().targetOrder(member, setup)) {
        for (const action of member.state.template.saving_throw_actions || []) {
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance)) return { target, action, distance };
        }
      }
      return null;
    } catch (error) {
      console.error("Failed browser single-target save-action choice", {
        member: member?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_ACTION_POLICY = { choose };
})();
