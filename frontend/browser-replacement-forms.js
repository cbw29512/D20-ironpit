(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;

  function enter(state, action, activeTemplate) {
    try {
      if (state.replacement_form) throw new Error(state.template.name + " is already transformed.");
      if (!action || !activeTemplate) throw new Error("Replacement form action and compiled template are required.");
      if (activeTemplate.kind !== state.template.kind) throw new Error("Replacement form must preserve combatant lifecycle kind.");
      E().spend(state, action.actionCost);
      const remaining = R().spend(state, action.resourceId, action.resourceCost || 1);
      const originalTemplate = state.template;
      state.replacement_form = {
        source_id: action.id, source_name: action.name, original_template: originalTemplate,
        form_template: activeTemplate, original_hp: state.current_hp,
        form_hp: activeTemplate.max_hp, form_max_hp: activeTemplate.max_hp,
        resource_id: action.resourceId || null, resource_cost: action.resourceCost || 1,
        voluntary_revert_action: action.voluntaryRevertAction || "bonus_action",
      };
      state.template = activeTemplate;
      return { source_id: action.id, form_name: activeTemplate.name, resource_remaining: remaining, reverted: false };
    } catch (error) {
      console.error("Browser replacement form entry failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function revert(state, spendVoluntaryAction = false) {
    try {
      const active = state.replacement_form;
      if (!active) throw new Error(state.template.name + " is not transformed.");
      if (spendVoluntaryAction) E().spend(state, active.voluntary_revert_action);
      const result = { source_id: active.source_id, form_name: active.form_template.name, resource_remaining: null, reverted: true };
      state.template = active.original_template;
      state.replacement_form = null;
      return result;
    } catch (error) {
      console.error("Browser replacement form reversion failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function applyDamage(state, amount) {
    try {
      if (amount < 0) throw new Error("Replacement-form damage cannot be negative.");
      const active = state.replacement_form;
      if (!active || amount === 0) return { excess: amount, reverted: false };
      const absorbed = Math.min(active.form_hp, amount);
      active.form_hp -= absorbed;
      const excess = amount - absorbed;
      if (active.form_hp > 0) return { excess: 0, reverted: false };
      revert(state, false);
      return { excess, reverted: true };
    } catch (error) {
      console.error("Browser replacement form damage failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORMS = { applyDamage, enter, revert };
})();