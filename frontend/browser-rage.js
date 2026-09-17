(() => {
  "use strict";

  const EFFECT = "rage", FRENZY_2014 = "frenzy-2014";
  const RESISTANCES = ["bludgeoning", "piercing", "slashing"], MINDLESS = ["charmed", "frightened"];
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
    spend: (state) => { state.bonus_action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;
  const active = (state) => state.active_effect_ids.includes(EFFECT);
  const is2014 = (state) => state.template.ruleset === "2014";
  const damageBonus = (state, attack) => active(state) && attack.rageEligible ? (state.template.rage_damage_bonus || 0) : 0;

  function endMindlessConditions(state) {
    if (!state.template.mindless_rage || is2014(state)) return [];
    const removed = MINDLESS.filter((id) => state.active_effect_ids.includes(id));
    if (!removed.length) return [];
    state.timed_effects = state.timed_effects.filter((effect) => !removed.includes(effect.effect_id));
    state.active_effect_ids = state.active_effect_ids.filter((id) => !removed.includes(id));
    return removed;
  }

  function enter(sequence, round, member) {
    const state = member.state;
    if (state.template.wearing_heavy_armor || !(state.template.rage_damage_bonus > 0) || active(state)) return null;
    if (!(state.resources.rage > 0) || !E().available(state, "bonus_action")) return null;
    state.resources.rage -= 1; E().spend(state, "bonus_action"); state.active_effect_ids.push(EFFECT);
    const frenzy2014 = is2014(state) && state.template.frenzy;
    if (frenzy2014) state.active_effect_ids.push(FRENZY_2014);
    const removed = endMindlessConditions(state);
    for (const type of RESISTANCES) if (!state.temporary_damage_resistances.includes(type)) state.temporary_damage_resistances.push(type);
    state.rage_expires_round = round + 1; state.rage_max_round = round + (is2014(state) ? 10 : 100);
    let description = `${state.template.name} enters Rage.`;
    if (frenzy2014) description += " The Berserker enters a Frenzy.";
    if (removed.length) description += ` Mindless Rage ends ${removed.join(", ")}.`;
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: EFFECT, removed_condition_ids: removed,
      resource_remaining: state.resources.rage, animation: "rage", description };
  }

  function extendFromAttack(state, round) {
    if (!active(state)) return;
    state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
  }

  function end(state) {
    if (!active(state)) return null;
    const frenzied = state.active_effect_ids.includes(FRENZY_2014);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== EFFECT && id !== FRENZY_2014);
    state.temporary_damage_resistances = state.temporary_damage_resistances.filter((type) => !RESISTANCES.includes(type));
    state.rage_expires_round = null; state.rage_max_round = null;
    return frenzied ? X().gain(state) : null;
  }

  function endIfIncapacitated(state) {
    if (state.template.wearing_heavy_armor || state.is_dead || Q().incapacitated(state)) end(state);
  }

  function finalize(sequence, round, member) {
    const state = member.state; let event = null;
    if (!is2014(state) && active(state) && state.rage_expires_round !== null && state.rage_expires_round <= round
        && (!state.rage_max_round || state.rage_max_round > round) && E().available(state, "bonus_action")) {
      E().spend(state, "bonus_action");
      state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
      event = { sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: state.template.name, feature_id: EFFECT, animation: "rage",
        description: `${state.template.name} extends Rage with a Bonus Action.` };
    }
    if (active(state) && state.rage_expires_round !== null && state.rage_expires_round <= round) {
      const exhaustion = end(state);
      if (exhaustion !== null) event = { sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: state.template.name, feature_id: "exhaustion", animation: "condition",
        description: `${state.template.name}'s Frenzy ends and causes Exhaustion level ${exhaustion}.` };
    }
    return { event, sequence };
  }

  window.IRON_PIT_BROWSER_RAGE = { active, damageBonus, end, endIfIncapacitated, enter, extendFromAttack, finalize };
})();
