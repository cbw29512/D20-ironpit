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
  const RC = () => window.IRON_PIT_BROWSER_RESOURCE_CONVERSION;

  function aiMayStartReplacementForm(state, action, owner) {
    try {
      if (action?.aiUsePolicy !== "emergency_only") return true;
      if (state.replacement_form) return false;
      if ((action.hpMode || "form_pool") === "retain_owner"
          && Number(action.temporaryHpOnEnter || 0) <= Number(state.temporary_hp || 0)) return false;
      const hp = Number(state.current_hp);
      const maxHp = Number(owner.max_hp);
      const fraction = Number(action.aiEmergencyHpFraction ?? (1 / 3));
      return hp > 0 && maxHp > 0 && Number.isFinite(fraction)
        && fraction > 0 && fraction < 1 && hp <= maxHp * fraction;
    } catch (error) {
      console.error("Replacement-form AI eligibility evaluation failed.", error);
      throw error;
    }
  }


  function preferFormOverSelfHealing(member, healing, turnKey) {
    try {
      const state = member.state;
      const owner = state.replacement_form?.original_template || state.template;
      const form = (owner.replacement_form_actions || []).find((a) => a.aiUsePolicy === "emergency_only");
      if (!form || !aiMayStartReplacementForm(state, form, owner)) return false;
      if (form.actionCost !== healing.actionCost || (healing.maxTargets || 1) !== 1
          || healing.stabilizeAtZero || healing.healingFromResourcePool
          || healing.sharedHealingPool != null || healing.percentileSuccessMax != null
          || (healing.removableConditions || []).length || healing.proneReactionStand) return false;
      if (!E().available(state, form.actionCost)) return false;
      if (!RES()?.available(state, form.resourceId, form.resourceCost || 1)
          && !RC()?.restorationAction(state, form.resourceId, turnKey)) return false;
      let buffer;
      if ((form.hpMode || "form_pool") === "retain_owner") {
        buffer = Math.max(0, Number(form.temporaryHpOnEnter || 0) - Number(state.temporary_hp || 0));
      } else if ((form.hpMode || "form_pool") === "form_pool") {
        const registry = owner.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[form.formTemplateId];
        if (!source) throw new Error("Emergency replacement form source unavailable.");
        buffer = Number(source.max_hp);
      } else throw new Error("Unknown form HP mode.");
      if (!(buffer > 0)) return false;
      const maximized = window.IRON_PIT_BROWSER_HEALING_POLICY?.healingMaximized(member, member) || false;
      let expected = Number(healing.healingBonus || 0)
        + Number(healing.diceCount || 0) * (maximized
          ? Number(healing.diceSize || 6) : (Number(healing.diceSize || 6) + 1) / 2);
      if (healing.restoreToEffectiveMax) expected = Number(owner.max_hp) - Number(state.current_hp);
      else if (healing.grantsTemporaryHp) expected = Math.max(0, expected - Number(state.temporary_hp || 0));
      else expected = Math.min(Math.max(0, Number(owner.max_hp) - Number(state.current_hp)), expected);
      return buffer > expected; // Tie stays with healing; AI preference, not RAW.
    } catch (error) {
      console.error("Emergency form/healing comparison failed", {
        combatant: member?.combatant_id, healing: healing?.id, error,
      });
      throw error;
    }
  }

  function register() {
    if (!S()) throw new Error("Replacement-form provider requires browser-main-action-selection.js.");
    S().registerProvider({
      id: "replacement-form-setup", category: C().REPLACEMENT_FORM_SETUP, rulesets: ["2014", "2024"],
      discover: ({ member, setup, turnKey }) => {
        const owner = member.state.replacement_form?.original_template || member.state.template;
        const action = (owner.replacement_form_actions || [])[0];
        if (!aiMayStartReplacementForm(member.state, action, owner)) return null;
        if (member.state.replacement_form && !action?.replaceExistingForm) return null;
        if (!action || !E().available(member.state, action.actionCost)) return null;
        const resourceReady = RES()?.available(member.state, action.resourceId, action.resourceCost || 1);
        if (!resourceReady && !RC()?.restorationAction(member.state, action.resourceId, turnKey)) return null;
        // An emergency form cannot be delayed or blocked by an optional setup spell.
        if (action.setupSpellId && action.aiUsePolicy !== "emergency_only"
            && member.state.concentration?.effect_id !== action.setupSpellId) {
          const choice = SP()?.chooseById(member, setup, turnKey, action.setupSpellId) || null;
          return choice ? { payload: { kind: "setup-spell", choice } } : null;
        }
        const registry = owner.ruleset === "2014"
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
        const owner = member.state.replacement_form?.original_template || member.state.template;
        const action = (owner.replacement_form_actions || [])
          .find((item) => item.id === candidate.payload.actionId);
        if (!action) throw new Error("Replacement-form action is unavailable.");
        const registry = owner.ruleset === "2014"
          ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
        const source = registry?.[candidate.payload.formTemplateId];
        if (!source) throw new Error("Replacement-form source became unavailable.");
        if (!RFC() || !RF()) throw new Error("Replacement-form compiler/runtime is not loaded.");
        const active = RFC().compile(
          owner, source, Boolean(action.retainSpellcasting), action.retainedSpellActionIds || [],
          Boolean(action.retainCreatureType), (action.hpMode || "form_pool") === "retain_owner"
        );
        const events = [];
        if (!RES()?.available(member.state, action.resourceId, action.resourceCost || 1)) {
          const conversion = RC()?.restorationAction(member.state, action.resourceId, turnKey);
          if (!conversion) throw new Error("Replacement-form resource restoration became unavailable.");
          const restored = RC().resolve(sequence, round, member, conversion, turnKey);
          if (!restored) throw new Error("Replacement-form resource restoration failed.");
          events.push(restored);
          sequence += 1;
        }
        const originalName = member.state.template.name;
        const result = RF().enter(member.state, action, active);
        events.push({
            sequence, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: originalName,
            feature_id: action.id, resource_remaining: result.resource_remaining,
            animation: "transform",
            description: originalName + " uses " + action.name + " and enters the " + source.name + " replacement form.",
          });
        return {
          events,
          sequence: sequence + 1,
        };
      },
    });
  }

  register();
  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_PROVIDER = { register, aiMayStartReplacementForm, preferFormOverSelfHealing };
})();