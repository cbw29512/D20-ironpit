(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_HEALING_POLICY;
  const G = () => window.IRON_PIT_BROWSER_GROUP_HEALING;
  const R = () => window.IRON_PIT_BROWSER_HEALING_RESOLUTION;

  function restore(state, amount) {
    if (state.is_dead || amount <= 0 || P().swarm(state)) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(S().effectiveMaxHp(state), before + amount);
    const healed = state.current_hp - before;
    if (healed > 0) {
      state.is_alive = true;
      state.is_unconscious = false;
      state.is_stable = false;
      state.death_save_successes = 0;
      state.death_save_failures = 0;
    }
    return healed;
  }

  function selfRider(sequence, round, healer, action, healedOther) {
    const rule = healer.state.template.slot_healing_other_self_rider;
    if (!rule || !healedOther || !P().slotHeal(action)) return null;
    const slotLevel = Number(action.resourceId.split("-").at(-1));
    const amount = (rule.flat_bonus || 0) + (rule.per_slot_level || 0) * slotLevel;
    const before = healer.state.current_hp;
    const healed = restore(healer.state, amount);
    if (!healed) return null;
    return {
      sequence, round_number: round, event_type: "healing",
      actor_id: healer.combatant_id, actor_name: healer.state.template.name,
      target_id: healer.combatant_id, target_name: healer.state.template.name,
      hp_before: before, hp_after: healer.state.current_hp,
      death_save_successes: healer.state.death_save_successes,
      death_save_failures: healer.state.death_save_failures,
      is_stable: healer.state.is_stable, is_dead: healer.state.is_dead,
      feature_id: rule.source_id, animation: "healing",
      description: `${healer.state.template.name} restores ${healed} HP from ${rule.source_id.replaceAll("-", " ")}.`,
    };
  }

  function resolve(sequence, round, healer, target, action, turnKey = null) {
    const runtime = R();
    if (!runtime) throw new Error("Browser healing resolution runtime is not loaded.");
    return runtime.resolve(sequence, round, healer, target, action, turnKey, restore);
  }

  window.IRON_PIT_BROWSER_HEALING = {
    bloodied: (...args) => P().bloodied(...args),
    chooseAction: (...args) => P().chooseAction(...args),
    chooseTarget: (...args) => P().chooseTarget(...args),
    groupTargets: (...args) => P().groupTargets(...args),
    resolve,
    resolveGroup: (...args) => G().resolveGroup(...args),
    restore,
    selfRider,
  };
})();
