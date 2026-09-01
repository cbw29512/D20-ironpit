(() => {
  "use strict";

  const EFFECT = "rage";
  const RESISTANCES = ["bludgeoning", "piercing", "slashing"];
  const MINDLESS = ["charmed", "frightened"];
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
    spend: (state) => { state.bonus_action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const active = (state) => state.active_effect_ids.includes(EFFECT);
  const damageBonus = (state, attack) => active(state) && attack.rageEligible ? (state.template.rage_damage_bonus || 0) : 0;

  function endMindlessConditions(state) {
    if (!state.template.mindless_rage) return [];
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
    state.rage_expires_round = round + 1; state.rage_max_round = round + 100;
    let description = `${state.template.name} enters Rage.`;
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
    if (!active(state)) return;
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== EFFECT);
    state.temporary_damage_resistances = state.temporary_damage_resistances.filter((type) => !RESISTANCES.includes(type));
    state.rage_expires_round = null; state.rage_max_round = null;
  }

  function endIfIncapacitated(state) {
    if (state.template.wearing_heavy_armor || state.is_dead || Q().incapacitated(state)) end(state);
  }

  function finalize(sequence, round, member) {
    const state = member.state; let event = null;
    if (active(state) && state.rage_expires_round !== null && state.rage_expires_round <= round
        && (!state.rage_max_round || state.rage_max_round > round) && E().available(state, "bonus_action")) {
      E().spend(state, "bonus_action");
      state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
      event = { sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: state.template.name, feature_id: EFFECT, animation: "rage",
        description: `${state.template.name} extends Rage with a Bonus Action.` };
    }
    if (active(state) && state.rage_expires_round !== null && state.rage_expires_round <= round) end(state);
    return { event, sequence };
  }

  window.IRON_PIT_BROWSER_RAGE = { active, damageBonus, endIfIncapacitated, enter, extendFromAttack, finalize };
})();
