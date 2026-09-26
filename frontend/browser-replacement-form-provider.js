(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const C = () => S().CATEGORIES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;
  const RFC = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function register() {
    if (!S()) throw new Error("Replacement-form provider requires browser-main-action-selection.js.");
    S().registerProvider({
      id: "replacement-form-setup", category: C().REPLACEMENT_FORM_SETUP, rulesets: ["2014", "2024"],
      discover: ({ member, setup, turnKey }) => {
        if (member.state.replacement_form || !E().available(member.state, "action")) return null;
        const action = (member.state.template.replacement_form_actions || [])[0];
        if (!action) return null;
        if (!RES()?.available(member.state, action.resourceId, action.resourceCost || 1)) return null;
        if (action.setupSpellId && member.state.concentration?.effect_id !== action.setupSpellId) {
          const choice = SP()?.chooseById(member, setup, turnKey, action.setupSpellId) || null;
          return choice ? { payload: { kind: "setup-spell", choice } } : null;
        }
        const registry = member.state.template.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[action.formTemplateId];
        if (!source) throw new Error("Replacement-form source " + action.formTemplateId + " is unavailable.");
        return { payload: { kind: "transform", actionId: action.id, formTemplateId: action.formTemplateId } };
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) => {
        if (candidate.payload.kind === "setup-spell") {
          if (!SR()) throw new Error("Replacement-form setup spell requires browser-spell-resolution.js.");
          return SR().resolve(sequence, round, member, setup, candidate.payload.choice, turnKey);
        }
        if (candidate.payload.kind !== "transform") throw new Error("Unknown replacement-form setup candidate.");
        const action = (member.state.template.replacement_form_actions || [])
          .find((item) => item.id === candidate.payload.actionId);
        if (!action) throw new Error("Replacement-form action is unavailable.");
        const registry = member.state.template.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[candidate.payload.formTemplateId];
        if (!source) throw new Error("Replacement-form source became unavailable.");
        if (!RFC() || !RF()) throw new Error("Replacement-form compiler/runtime is not loaded.");
        const active = RFC().compile(member.state.template, source, Boolean(action.retainSpellcasting));
        const originalName = member.state.template.name;
        const result = RF().enter(member.state, action, active);
        return {
          events: [{
            sequence, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: originalName,
            feature_id: action.id, resource_remaining: result.resource_remaining,
            animation: "transform",
            description: originalName + " uses " + action.name + " and enters the " + source.name + " replacement form.",
          }],
          sequence: sequence + 1,
        };
      },
    });
  }

  register();
  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_PROVIDER = { register };
})();