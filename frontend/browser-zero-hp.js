(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const U = () => window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const B = () => window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const DODGE = "dodge";
  const PRONE = "prone";

  function useRelentless(state, remaining) {
    if (!state.template.traits?.includes("relentless-endurance")) return false;
    if ((state.resources["relentless-endurance"] || 0) < 1 || remaining >= S().effectiveMaxHp(state)) return false;
    state.resources["relentless-endurance"] -= 1;
    state.current_hp = 1;
    state.is_alive = true;
    state.is_unconscious = false;
    state.is_stable = false;
    return true;
  }

  function useUndeadFortitude(state, incoming, damageTypes, critical) {
    if (!state.template.traits?.includes("undead-fortitude")) return false;
    const resolver = U();
    if (!resolver) throw new Error("Undead Fortitude runtime is not loaded.");
    return resolver.resolve(state, incoming, damageTypes, critical);
  }

  function endDodge(state) { state.active_effect_ids = state.active_effect_ids.filter((id) => id !== DODGE); }

  function markUnconscious(state) {
    state.is_alive = true;
    state.is_unconscious = true;
    state.is_stable = false;
    endDodge(state);
    if (!I().immune(state, PRONE) && !state.active_effect_ids.includes(PRONE)) state.active_effect_ids.push(PRONE);
  }

  function markDead(state) {
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    state.is_stable = false;
    endDodge(state);
  }

  function applyMaxHpReduction(state, amount) {
    if (amount < 0) throw new Error("Maximum-HP reduction cannot be negative.");
    if (!amount || state.is_dead) return 0;
    const before = S().effectiveMaxHp(state);
    state.max_hp_reduction = Math.min(state.template.max_hp + (state.max_hp_bonus || 0), (state.max_hp_reduction || 0) + amount);
    const after = S().effectiveMaxHp(state);
    state.current_hp = Math.min(state.current_hp, after);
    if (!after) markDead(state);
    return before - after;
  }

  function finish(state, outcome, incoming, affectedStates) {
    B()?.endDamageSensitive(state);
    if (!state.concentration) return outcome;
    if (!C()) throw new Error("Browser concentration runtime is not loaded.");
    C().resolveDamage(state, incoming, affectedStates);
    return outcome;
  }

  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = []) {
    const incoming = amount;
    if (!incoming || state.is_dead) return "damaged";
    const absorbed = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= absorbed;
    amount -= absorbed;
    if (state.current_hp === 0) {
      if (state.template.kind === "monster" || incoming >= S().effectiveMaxHp(state)) {
        markDead(state); return finish(state, "dead", incoming, affectedStates);
      }
      state.is_stable = false;
      state.death_save_failures = Math.min(3, state.death_save_failures + (critical ? 2 : 1));
      if (state.death_save_failures >= 3) { markDead(state); return finish(state, "dead", incoming, affectedStates); }
      markUnconscious(state); return finish(state, "unconscious", incoming, affectedStates);
    }
    if (!amount) return finish(state, "damaged", incoming, affectedStates);
    const before = state.current_hp;
    state.current_hp = Math.max(0, before - amount);
    if (state.current_hp > 0) return finish(state, "damaged", incoming, affectedStates);
    if (useUndeadFortitude(state, incoming, damageTypes, critical)) return finish(state, "undead_fortitude", incoming, affectedStates);
    if (state.template.kind === "monster") { markDead(state); return finish(state, "dead", incoming, affectedStates); }
    const remaining = Math.max(0, amount - before);
    if (remaining >= S().effectiveMaxHp(state)) { markDead(state); return finish(state, "dead", incoming, affectedStates); }
    if (useRelentless(state, remaining)) return finish(state, "relentless_endurance", incoming, affectedStates);
    markUnconscious(state);
    return finish(state, "unconscious", incoming, affectedStates);
  }

  window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage, applyMaxHpReduction };
})();
