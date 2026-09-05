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

  function useUndeadFortitude(state, incoming, damageTypes, critical, advantageSources) {
    if (!state.template.traits?.includes("undead-fortitude")) return false;
    const resolver = U();
    if (!resolver) throw new Error("Undead Fortitude runtime is not loaded.");
    return resolver.resolve(state, incoming, damageTypes, critical, advantageSources);
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

  function restoreHitPoints(state, amount) {
    if (amount < 0) throw new Error("Healing cannot be negative.");
    if (state.is_dead || amount === 0 || state.template.traits?.includes("swarm")) return 0;
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

  function finish(state, outcome, incoming, affectedStates, advantageSources) {
    B()?.endDamageSensitive(state);
    if (!state.concentration) return outcome;
    if (!C()) throw new Error("Browser concentration runtime is not loaded.");
    C().resolveDamage(state, incoming, affectedStates, advantageSources);
    return outcome;
  }

  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = [], savingThrowAdvantageSources = 0) {
    const incoming = amount;
    if (!incoming || state.is_dead) return "damaged";
    const absorbed = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= absorbed;
    amount -= absorbed;
    if (state.current_hp === 0) {
      if (state.template.kind === "monster" || incoming >= S().effectiveMaxHp(state)) {
        markDead(state); return finish(state, "dead", incoming, affectedStates, savingThrowAdvantageSources);
      }
      state.is_stable = false;
      state.death_save_failures = Math.min(3, state.death_save_failures + (critical ? 2 : 1));
      if (state.death_save_failures >= 3) { markDead(state); return finish(state, "dead", incoming, affectedStates, savingThrowAdvantageSources); }
      markUnconscious(state); return finish(state, "unconscious", incoming, affectedStates, savingThrowAdvantageSources);
    }
    if (!amount) return finish(state, "damaged", incoming, affectedStates, savingThrowAdvantageSources);
    const before = state.current_hp;
    state.current_hp = Math.max(0, before - amount);
    if (state.current_hp > 0) return finish(state, "damaged", incoming, affectedStates, savingThrowAdvantageSources);
    if (useUndeadFortitude(state, incoming, damageTypes, critical, savingThrowAdvantageSources)) return finish(state, "undead_fortitude", incoming, affectedStates, savingThrowAdvantageSources);
    if (state.template.kind === "monster") { markDead(state); return finish(state, "dead", incoming, affectedStates, savingThrowAdvantageSources); }
    const remaining = Math.max(0, amount - before);
    if (remaining >= S().effectiveMaxHp(state)) { markDead(state); return finish(state, "dead", incoming, affectedStates, savingThrowAdvantageSources); }
    if (useRelentless(state, remaining)) return finish(state, "relentless_endurance", incoming, affectedStates, savingThrowAdvantageSources);
    markUnconscious(state);
    return finish(state, "unconscious", incoming, affectedStates, savingThrowAdvantageSources);
  }

  window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage, restoreHitPoints };
})();
