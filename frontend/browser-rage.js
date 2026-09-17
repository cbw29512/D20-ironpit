(() => {
  "use strict";

  const EFFECT = "rage", FRENZY_2014 = "frenzy-2014";
  const RESISTANCES = ["bludgeoning", "piercing", "slashing"], MINDLESS = ["charmed", "frightened"];
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
    spend: (state) => { state.bonus_action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const active = (state) => state.active_effect_ids.includes(EFFECT), is2014 = (state) => state.template.ruleset === "2014";
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
    const removed = endMindlessConditions(state);
    for (const type of RESISTANCES) if (!state.temporary_damage_resistances.includes(type)) state.temporary_damage_resistances.push(type);
    state.rage_started_round = round; state.rage_last_attack_round = null; state.rage_last_damage_round = null;
    state.rage_expires_round = round + 1; state.rage_max_round = round + (is2014(state) ? 9 : 100);
    if (is2014(state) && state.template.frenzy_bonus_attack_2014) {
      if (!state.active_effect_ids.includes(FRENZY_2014)) state.active_effect_ids.push(FRENZY_2014);
      state.frenzy_2014_started_round = round;
    }
    let description = `${state.template.name} enters Rage.`;
    if (state.frenzy_2014_started_round === round) description += " Frenzy is active.";
    if (removed.length) description += ` Mindless Rage ends ${removed.join(", ")}.`;
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: EFFECT, removed_condition_ids: removed,
      resource_remaining: state.resources.rage, animation: "rage", description };
  }

  function extendFromAttack(state, round) {
    if (!active(state)) return;
    state.rage_last_attack_round = round;
    state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
  }
  function noteDamage(state, round) { if (active(state) && is2014(state)) state.rage_last_damage_round = round; }

  function end(state) {
    if (!active(state)) return;
    if (is2014(state) && state.active_effect_ids.includes(FRENZY_2014)) {
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== FRENZY_2014);
      state.frenzy_2014_started_round = null;
      state.exhaustion_level_2014 = Math.min(6, (state.exhaustion_level_2014 || 0) + 1);
      if (state.exhaustion_level_2014 >= 6) {
        state.current_hp = 0; state.is_alive = false; state.is_dead = true; state.is_unconscious = false;
      }
    }
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== EFFECT);
    state.temporary_damage_resistances = state.temporary_damage_resistances.filter((type) => !RESISTANCES.includes(type));
    state.rage_expires_round = null; state.rage_max_round = null; state.rage_started_round = null;
    state.rage_last_attack_round = null; state.rage_last_damage_round = null;
  }

  function endIfIncapacitated(state) {
    if (state.template.wearing_heavy_armor || state.is_dead || Q().incapacitated(state)) end(state);
  }

  function finalize(sequence, round, member) {
    const state = member.state; let event = null;
    if (!active(state) || state.rage_expires_round == null) return { event, sequence };
    if (is2014(state)) {
      if (state.rage_max_round != null && round >= state.rage_max_round) { end(state); return { event, sequence }; }
      const maintained = state.rage_last_attack_round === round
        || (state.rage_last_damage_round != null && state.rage_last_damage_round >= round - 1);
      if (maintained) state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
      else end(state);
      return { event, sequence };
    }
    if (state.rage_max_round != null && state.rage_max_round <= round) { end(state); return { event, sequence }; }
    if (state.rage_expires_round <= round && E().available(state, "bonus_action")) {
      E().spend(state, "bonus_action"); state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
      event = { sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: state.template.name, feature_id: EFFECT, animation: "rage",
        description: `${state.template.name} extends Rage with a Bonus Action.` };
    }
    if (active(state) && state.rage_expires_round <= round) end(state);
    return { event, sequence };
  }

  window.IRON_PIT_BROWSER_RAGE = { active, damageBonus, endIfIncapacitated, enter, extendFromAttack, finalize, noteDamage };
})();