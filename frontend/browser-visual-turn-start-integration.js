(() => {
  "use strict";
  const hooks = () => window.IRON_PIT_BROWSER_ABILITY_HOOKS;
  const policy = () => window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY;
  const conditions = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const timed = () => window.IRON_PIT_BROWSER_TIMED;
  const saves = () => window.IRON_PIT_BROWSER_SAVING_THROWS;
  const state = () => window.IRON_PIT_BROWSER_STATE;
  const immune = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;

  function resolve(ctx) {
    const { member: target, setup, round } = ctx;
    const events = [];
    let sequence = ctx.sequence;
    const sources = [...setup.heroes, ...setup.monsters].filter(
      actor => actor.combatant_id !== target.combatant_id &&
        actor.state.template.visualTurnStartRule
    );
    // Consume the already resolved RAW initiative sequence and its tie breaks.
    // Initiative order decides the explicit Iron Pit eye-aversion exception.
    const turnOrder = ctx.initiative?.turn_order;
    if (sources.length && (!Array.isArray(turnOrder) || !turnOrder.length)) {
      throw new Error("A visual turn-start source requires resolved initiative order.");
    }
    sources.sort((a, b) => turnOrder.indexOf(a.combatant_id) - turnOrder.indexOf(b.combatant_id));
    for (const source of sources) {
      const rule = source.state.template.visualTurnStartRule;
      const distance = state().distance(source, target);
      const facts = {
        distanceFt: distance,
        sourceActive: source.state.current_hp > 0 &&
          (rule.requiresSourceNotIncapacitated === false || !conditions().incapacitated(source.state)),
        targetActive: target.state.current_hp > 0 && !target.state.is_dead,
        sourceSeesTarget: conditions().canSee(source.state, target.state, distance),
        targetSeesSource: conditions().canSee(target.state, source.state, distance),
        targetImmune: immune().immune(target.state, rule.failedSaveTimedEffect?.effectId || rule.terminalDebuff || "petrified"),
        sourceTrueFormVisible: source.state.true_form_visible !== false,
        targetTypeAllowed: !(rule.requiredTargetCreatureTypes || []).length ||
          (rule.requiredTargetCreatureTypes || []).some(type =>
            (target.state.template.creature_type || "").toLowerCase().split(" (", 1)[0] === type.toLowerCase()),
        sourcePrecedesTarget: policy().initiativePrecedes(turnOrder, source.combatant_id, target.combatant_id),
      };
      if (rule.failedSaveTimedEffect) {
        if (window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.isImmune(target, { id: rule.sourceId }, source.combatant_id)) continue;
        const existing = (target.state.timed_effects || []).some(e =>
          e.source_id === source.combatant_id && e.source_effect_id === rule.sourceId &&
          e.effect_id === rule.failedSaveTimedEffect.effectId);
        if (existing) continue; // The existing timed effect owns its repeat-save lifecycle.
      }
      const decision = policy().decide(rule, facts);
      if (decision === "ineligible") continue;
      if (decision === "averted") {
        const windows = target.state.visual_aversion_windows || [];
        target.state.visual_aversion_windows = window.IRON_PIT_BROWSER_VISUAL_SOURCE_AVERSION.record(
          windows, target.combatant_id, source.combatant_id, target.state.turns_started,
        );
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: target.combatant_id, target_id: source.combatant_id,
          feature_id: rule.sourceId, animation: "condition",
          description: `${target.state.template.name} averts its eyes from ${source.state.template.name}.`,
        });
        continue;
      }
      const save = saves().resolveSavingThrow(target.state, rule.saveAbility || "constitution", rule.saveDc,
        { encounterRoller: target, setup, roundNumber: round });
      if (rule.failedSaveTimedEffect) {
        let applied = [];
        if (save.succeeded) {
          window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.grantImmunity(
            target.state, rule.sourceId, source.combatant_id, round,
            { sourceTemplate: source.state.template },
          );
        } else {
          const effect = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS.apply(
            source, target, { id: rule.sourceId, magicalEffect: false },
            rule.failedSaveTimedEffect, round, setup,
          );
          if (effect) applied = Array.isArray(effect) ? effect : [effect];
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: source.combatant_id, target_id: target.combatant_id,
          feature_id: rule.sourceId, save_ability: rule.saveAbility || "wisdom",
          save_dc: rule.saveDc, saving_throw_roll: save.roll, save_succeeded: save.succeeded,
          applied_condition_ids: applied, animation: "condition",
          description: target.state.template.name + (save.succeeded ? " resists " : " fails ") + rule.sourceName + ".",
        });
        if (target.state.is_dead) break;
        continue;
      }
      const current = (target.state.timed_effects || []).find(
        e => e.source_id === source.combatant_id && e.source_effect_id === rule.sourceId &&
          e.effect_id === (rule.initialDebuff || "restrained")
      );
      // The universal save resolver may turn a failed die total into success
      // via a feature. Honor that adjudicated outcome, not only the raw die.
      if (!save.succeeded && !Number.isInteger(save.roll?.total)) {
        throw new Error("A failed visual save requires its resolved roll total.");
      }
      const next = policy().resolveStage(rule, save.succeeded ? rule.saveDc : save.roll.total,
        current ? current.effect_id : null);
      if (current) timed().removeEffect(target.state, current);
      if (next !== "clear") {
        timed().apply(target.state, next, source.combatant_id, {
          sourceEffectId: rule.sourceId, sourceTemplate: source.state.template,
          appliedRound: round, setup,
        });
      }
      events.push({
        sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, target_id: target.combatant_id,
        feature_id: rule.sourceId, save_ability: rule.saveAbility || "constitution",
        save_dc: rule.saveDc, saving_throw_roll: save.roll, save_succeeded: save.succeeded,
        applied_condition_ids: next === "clear" ? [] : [next], animation: "condition",
        description: `${target.state.template.name} ${save.succeeded ? "resists" : "fails"} ${rule.sourceName} (${next}).`,
      });
      if (target.state.is_dead) break;
    }
    return { events, sequence, claimed: false };
  }

  function installAbilityHooks() {
    hooks().registerAbility(hooks().PHASES.TURN_START, {
      id: "universal-visual-turn-start", rulesets: ["2014", "2024"],
      priority: 20, appliesTo: (_, ctx) => [...ctx.setup.heroes, ...ctx.setup.monsters]
        .some(actor => actor.state.template.visualTurnStartRule),
      resolve,
    });
  }
  window.IRON_PIT_BROWSER_VISUAL_TURN_START_INTEGRATION = { resolve, installAbilityHooks };
})();
