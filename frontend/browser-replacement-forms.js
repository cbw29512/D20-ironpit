(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;

  function mergeBonuses(owner = {}, form = {}) {
    const keys = new Set([...Object.keys(owner || {}), ...Object.keys(form || {})]);
    return Object.fromEntries([...keys].map((key) => [key, Math.max(owner?.[key] ?? -99, form?.[key] ?? -99)]));
  }

  function compileActiveTemplate(owner, form, retainSpellcasting = false, retainedSpellActionIds = []) {
    try {
      if (!owner || owner.kind !== "character") throw new Error("Replacement-form owner must be a character.");
      if (!form || form.kind !== "monster") throw new Error("Replacement-form source must be a monster/beast template.");
      const active = structuredClone(form);
      Object.assign(active, {
        id: owner.id + "--form-" + form.id,
        name: owner.name,
        archetype: owner.archetype,
        level: owner.level,
        kind: owner.kind,
        ruleset: owner.ruleset,
        saving_throw_bonuses: mergeBonuses(owner.saving_throw_bonuses, form.saving_throw_bonuses),
        skill_bonuses: mergeBonuses(owner.skill_bonuses, form.skill_bonuses),
        resources: structuredClone(owner.resources || {}),
        unlimited_resources: structuredClone(owner.unlimited_resources || []),
        replacement_form_actions: structuredClone(owner.replacement_form_actions || []),
        source: (owner.source || "") + "; replacement form: " + (form.source || form.name),
      });
      const allowed = new Set(retainedSpellActionIds || []);
      const keep = (actions) => structuredClone((actions || []).filter((action) => allowed.has(action.id)));
      if (retainSpellcasting) {
        active.spell_save_actions = keep(owner.spell_save_actions);
        active.spell_attack_actions = keep(owner.spell_attack_actions);
        active.persistent_spell_attack_actions = keep(owner.persistent_spell_attack_actions);
        active.defensive_spell_actions = keep(owner.defensive_spell_actions);
        active.healingActions = keep(owner.healingActions);
        active.condition_removal_actions = keep(owner.condition_removal_actions);
        active.effect_removal_actions = keep(owner.effect_removal_actions);
      } else {
        active.spell_save_actions = [];
        active.spell_attack_actions = [];
        active.persistent_spell_attack_actions = [];
        active.defensive_spell_actions = [];
        active.healingActions = [];
        active.condition_removal_actions = [];
        active.effect_removal_actions = [];
      }
      return active;
    } catch (error) {
      console.error("Browser replacement form compilation failed", { owner: owner?.id, form: form?.id, error });
      throw error;
    }
  }

  function formRegistry(ruleset) {
    if (ruleset === "2014") return window.IRON_PIT_BROWSER_MONSTERS_2014 || {};
    return window.IRON_PIT_BROWSER_MONSTERS || {};
  }

  function resolveAction(state, action) {
    try {
      const source = formRegistry(state.template.ruleset)[action.formTemplateId];
      if (!source) throw new Error("Unknown replacement form template: " + action.formTemplateId);
      const activeTemplate = compileActiveTemplate(state.template, source, Boolean(action.retainSpellcasting), action.retainedSpellActionIds || []);
      return enter(state, action, activeTemplate);
    } catch (error) {
      console.error("Browser replacement form action failed", { combatant: state?.template?.name, action: action?.id, error });
      throw error;
    }
  }

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

  window.IRON_PIT_BROWSER_REPLACEMENT_FORMS = { applyDamage, compileActiveTemplate, enter, resolveAction, revert };
})();