(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const U = () => window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const B = () => window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT;
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;
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

  function applyProne(state) {
    if (!I().immune(state, PRONE) && !state.active_effect_ids.includes(PRONE)) state.active_effect_ids.push(PRONE);
  }

  function markUnconscious(state) {
    state.is_alive = true;
    state.is_unconscious = true;
    state.is_stable = false;
    endDodge(state);
    applyProne(state);
    RF()?.revertIfIncapacitated(state);
  }

  function stabilizeAtZero(state, interceptZeroHp = false) {
    if (state.is_dead && !interceptZeroHp) return "dead";
    state.current_hp = 0;
    state.is_alive = true;
    state.is_dead = false;
    state.is_unconscious = true;
    state.is_stable = true;
    state.death_save_successes = 0;
    state.death_save_failures = 0;
    endDodge(state);
    applyProne(state);
    RF()?.revertIfIncapacitated(state);
    return "unconscious";
  }

  function delayRegenDeath(state) {
    const trait = state.template.regeneration;
    return Boolean(trait && trait.survives_zero_until_turn && !state.is_dead);
  }

  function noteRegenTypes(state, damageTypes) {
    if (!state.template.regeneration || !damageTypes?.length) return;
    const remembered = new Set(state.damage_types_taken_since_regen || []);
    for (const item of damageTypes) remembered.add(String(item));
    state.damage_types_taken_since_regen = [...remembered].sort();
  }

  function markDead(state) {
    if (delayRegenDeath(state)) { markUnconscious(state); return; }
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    state.is_stable = false;
    endDodge(state);
    RF()?.revertIfIncapacitated(state);
  }

  function finish(state, outcome, incoming, affectedStates, setup = null) {
    B()?.endDamageSensitive(state);
    if (incoming > 0 && state.damage_share_source_id) {
      if (!setup) throw new Error("Damage share requires encounter setup.");
      window.IRON_PIT_BROWSER_DAMAGE_SHARE.resolveForState(state, incoming, setup);
    }
    if (!state.concentration) return outcome;
    if (!C()) throw new Error("Browser concentration runtime is not loaded.");
    C().resolveDamage(state, incoming, affectedStates);
    return outcome;
  }

  function applyInstantDeath(state, affectedStates = []) {
    if (state.is_dead || !state.is_alive) return "unchanged";
    if (Z()?.consumeInstantDeath(state)) return "zero_hp_replacement";
    markDead(state);
    if (state.concentration && C()) C().endIfIncapacitated(state, affectedStates);
    return "dead";
  }

  function reduceToZero(state, affectedStates = []) {
    try {
      if (state.is_dead || state.current_hp === 0) return "unchanged";
      state.current_hp = 0;
      let outcome = null;
      if (state.template.kind === "monster") {
        markDead(state); outcome = state.is_dead ? "dead" : "unconscious";
      } else if (state.template.effect_bound_survival_save) {
        if (!U()) throw new Error("Effect-bound survival save runtime is not loaded.");
        if (U().resolveEffectBound(state)) outcome = "survival_save";
      }
      if (!outcome && useRelentless(state, 0)) outcome = "relentless_endurance";
      if (!outcome) { markUnconscious(state); outcome = "unconscious"; }
      if ((state.is_dead || state.is_unconscious) && C()) C().endIfIncapacitated(state, affectedStates);
      return outcome;
    } catch (error) {
      console.error("Browser zero-HP reduction failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function noteTurnDamage(state, incoming, damageTypes = [], damageComponents = []) {
    try {
      if (!(incoming > 0)) return;
      state.damage_taken_this_turn_by_type ||= {};
      let remaining = incoming;
      for (const part of damageComponents || []) {
        const applied = Math.max(0, Number(part.applied_total || 0));
        const credited = Math.min(applied, remaining);
        if (credited) {
          const key = String(part.damage_type);
          state.damage_taken_this_turn_by_type[key] = (state.damage_taken_this_turn_by_type[key] || 0) + credited;
          remaining -= credited;
        }
        if (remaining <= 0) return;
      }
      if (remaining > 0 && (damageTypes || []).length === 1) {
        const key = String(damageTypes[0]);
        state.damage_taken_this_turn_by_type[key] = (state.damage_taken_this_turn_by_type[key] || 0) + remaining;
      }
    } catch (error) {
      console.error("Failed browser per-turn typed damage tracking.", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = [], setup = null, damageComponents = []) {
    const incoming = amount;
    if (!incoming || state.is_dead) return "damaged";
    noteRegenTypes(state, damageTypes);
    noteTurnDamage(state, incoming, damageTypes, damageComponents);
    const absorbed = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= absorbed;
    amount -= absorbed;
    if (amount && state.replacement_form) {
      if (!RF()) throw new Error("Replacement-form runtime is not loaded.");
      amount = RF().applyDamage(state, amount).excess;
    }
    if (state.current_hp === 0) {
      if (state.template.kind === "monster" || incoming >= S().effectiveMaxHp(state)) {
        markDead(state);
        return finish(state, state.is_dead ? "dead" : "unconscious", incoming, affectedStates, setup);
      }
      state.is_stable = false;
      state.death_save_failures = Math.min(3, state.death_save_failures + (critical ? 2 : 1));
      if (state.death_save_failures >= 3) { markDead(state); return finish(state, "dead", incoming, affectedStates, setup); }
      markUnconscious(state); return finish(state, "unconscious", incoming, affectedStates, setup);
    }
    if (!amount) return finish(state, "damaged", incoming, affectedStates, setup);
    const before = state.current_hp;
    state.current_hp = Math.max(0, before - amount);
    if (state.current_hp > 0) return finish(state, "damaged", incoming, affectedStates, setup);
    if (Z()?.consumeZero(state)) return finish(state, "zero_hp_replacement", incoming, affectedStates, setup);
    if (useUndeadFortitude(state, incoming, damageTypes, critical)) return finish(state, "undead_fortitude", incoming, affectedStates, setup);
    if (state.template.kind === "monster") {
      markDead(state);
      return finish(state, state.is_dead ? "dead" : "unconscious", incoming, affectedStates, setup);
    }
    const remaining = Math.max(0, amount - before);
    if (remaining >= S().effectiveMaxHp(state)) { markDead(state); return finish(state, "dead", incoming, affectedStates, setup); }
    if (state.template.effect_bound_survival_save) {
      if (!U()) throw new Error("Effect-bound survival save runtime is not loaded.");
      if (U().resolveEffectBound(state)) return finish(state, "survival_save", incoming, affectedStates, setup);
    }
    if (useRelentless(state, remaining)) return finish(state, "relentless_endurance", incoming, affectedStates, setup);
    markUnconscious(state);
    return finish(state, "unconscious", incoming, affectedStates, setup);
  }

  window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage, applyInstantDeath, reduceToZero, stabilizeAtZero };
})();
