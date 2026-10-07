(() => {
  "use strict";
  function candidates(remover, target, action) {
    const grants = target.state.template.effect_tag_condition_grants || [];
    if (!grants.length) return [];
    const Q = window.IRON_PIT_BROWSER_CONDITION_RULES;
    const I = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
    if (!Q || !I) throw new Error("Effect-tag conditions require condition rules and immunity.");
    return grants.filter((grant) => (action.effectTags || []).includes(grant.effect_tag)
      && !Q.has(target.state, grant.condition_id)
      && !I.immune(target.state, grant.condition_id, remover.state.template, { sourceIsMagical: true }))
      .map((grant) => ({ target, grant }));
  }
  function validateRuntime() {
    if (!window.IRON_PIT_BROWSER_TIMED || !window.IRON_PIT_BROWSER_CONCENTRATION
        || !window.IRON_PIT_BROWSER_REPLACEMENT_FORMS) {
      throw new Error("Effect-tag conditions require timed, concentration and form runtimes.");
    }
  }
  function apply(sequence, round, remover, setup, action, effect, remaining) {
    const { target, grant } = effect;
    const hp = target.state.current_hp;
    const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
    const applied = window.IRON_PIT_BROWSER_TIMED.apply(target.state, grant.condition_id, remover.combatant_id, {
      sourceEffectId: action.id, sourceTemplate: remover.state.template, sourceIsMagical: true,
      appliedRound: round, expiresRound: round + grant.duration_rounds,
      expiryTiming: "source_turn_start", affectedStates: states,
    });
    window.IRON_PIT_BROWSER_CONCENTRATION.endIfIncapacitated(target.state, states);
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: remover.combatant_id, actor_name: remover.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      feature_id: action.id, resource_remaining: remaining,
      applied_condition_ids: applied ? [applied] : [], hp_before: hp, hp_after: target.state.current_hp,
      animation: action.animation || "effect-removal",
      description: `${remover.state.template.name} uses ${action.name}: ${grant.source_name} applies `
        + `${grant.condition_id} to ${target.state.template.name} for ${grant.duration_rounds} rounds.`,
    };
  }
  window.IRON_PIT_BROWSER_EFFECT_TAG_CONDITIONS = { candidates, validateRuntime, apply };
})();
