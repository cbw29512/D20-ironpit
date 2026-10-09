(() => {
  "use strict";

  // Single-target, source-grounded failed-save danger for the form AI only.
  // Never convert conditions into invented damage or alter combat state.
  const severe = new Set(["incapacitated", "paralyzed", "petrified", "stunned", "unconscious"]);
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
  const P = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const H = () => window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const E = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function formMitigates(member, setup, form) {
    try {
      if (!setup || form?.aiUsePolicy !== "emergency_only") return false;
      const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
      const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
      const alive = (actor) => actor.state.is_alive !== false && !actor.state.is_dead
        && actor.state.current_hp > 0;
      if (allies.filter(alive).length !== 1) return false;
      const owner = member.state.replacement_form?.original_template || member.state.template;
      for (const enemy of enemies.filter((actor) => alive(actor) && !E().incapacitated(actor.state))) {
        const distance = S().distance(enemy, member);
        const actions = [];
        for (const action of enemy.state.template.saving_throw_actions || []) {
          if (action.actionCost === "reaction" || (action.maxTargets || 1) !== 1
            || action.area || distance > (action.range || 0)
            || (action.resourceId && !R().available(enemy.state, action.resourceId, action.resourceCost || 1))
            || !V().legalAction(action, member, distance, enemy.combatant_id)
            || (action.requiresTargetSight && !E().canSee(enemy.state, member.state, distance))) continue;
          actions.push([action, Boolean(action.magicalEffect)]);
        }
        for (const action of enemy.state.template.spell_save_actions || []) {
          if (action.actionCost === "reaction" || (action.castRounds || 1) !== 1
            || action.repeatOnly || action.area || action.areaRadius
            || (action.targetCount || 1) !== 1 || action.targetCountPerSlotAbove
            || (action.concentration && enemy.state.concentration)
            || !C().legalSlotLevels(enemy.state, "forecast:" + enemy.combatant_id, action.level).length
            || !H().legalSingleTargets(enemy, setup, action).some((target) => target.combatant_id === member.combatant_id)) continue;
          actions.push([action, true]);
        }
        for (const [action, magical] of actions) {
          const condition = action.failedSaveTimedEffect?.effectId;
          if (!severe.has(condition) || I().immune(member.state, condition, enemy.state.template, { sourceIsMagical: magical })) continue;
          const exposed = 1 - O().saveSuccess(member, action);
          if (exposed < 0.5) continue;
          const registry = owner.ruleset === "2014"
            ? window.IRON_PIT_BROWSER_MONSTERS_2014 : window.IRON_PIT_BROWSER_MONSTERS;
          const source = registry?.[form.formTemplateId];
          if (!source) throw new Error("Protection preview requires the source replacement form.");
          const compiled = P().compile(
            owner, source, Boolean(form.retainSpellcasting), form.retainedSpellActionIds || [],
            Boolean(form.retainCreatureType), (form.hpMode || "form_pool") === "retain_owner",
          );
          const shaped = { ...member, state: { ...member.state, template: compiled } };
          const protectedRisk = I().immune(shaped.state, condition, enemy.state.template, { sourceIsMagical: magical })
            ? 0 : 1 - O().saveSuccess(shaped, action);
          if (exposed - protectedRisk >= 0.25) return true;
        }
      }
      return false;
    } catch (error) {
      console.error("Form defense against failed-save conditions could not be scored.", { id: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_CONDITION_THREAT = { formMitigates };
})();
