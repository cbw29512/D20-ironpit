(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const U = () => window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const B = () => window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_REGENERATION;
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
    state.is_alive = true; state.is_unconscious = true; state.is_stable = false; endDodge(state);
    if (!I().immune(state, PRONE) && !state.active_effect_ids.includes(PRONE)) state.active_effect_ids.push(PRONE);
  }

  function activateReplacement(state) {
    const rule = state.zero_hp_replacement;
    if (!rule || rule.triggered) return false;
    if (!rule.target_member || !rule.setup || !rule.source_template || !rule.source_side) {
      throw new Error("Zero-HP replacement is missing source/encounter context.");
    }
    rule.triggered = true;
    const target = rule.target_member, setup = rule.setup, previous = target.state;
    const replacement = S().buildState(rule.source_template);
    replacement.current_hp = Math.min(rule.replacement_hp, replacement.template.max_hp);
    replacement.position = previous.position;
    replacement.initiative_roll = previous.initiative_roll;
    replacement.initiative_total = previous.initiative_total;
    replacement.turn_serial = previous.turn_serial;
    target.state = replacement;
    if (target.side !== rule.source_side) {
      const oldGroup = target.side === "heroes" ? setup.heroes : setup.monsters;
      const newGroup = rule.source_side === "heroes" ? setup.heroes : setup.monsters;
      const index = oldGroup.findIndex((member) => member.combatant_id === target.combatant_id);
      if (index >= 0) oldGroup.splice(index, 1);
      if (!newGroup.some((member) => member.combatant_id === target.combatant_id)) newGroup.push(target);
      target.side = rule.source_side;
    }
    return true;
  }

  function applyReplacementEffect(target, source, sourceEffectId, effect, setup) {
    if (!target || !source || !setup) throw new Error("Zero-HP replacement requires target, source, and setup.");
    target.state.zero_hp_replacement = {
      effect_id: effect.effectId, source_id: source.combatant_id, source_effect_id: sourceEffectId,
      replacement_mode: effect.replacementMode, control_mode: effect.controlMode,
      replacement_hp: effect.replacementHp, triggered: false, source_template: source.state.template,
      source_side: source.side, target_member: target, setup,
    };
    if (!target.state.active_effect_ids.includes(effect.effectId)) target.state.active_effect_ids.push(effect.effectId);
    return effect.effectId;
  }

  function markDead(state) {
    state.current_hp = 0;
    if (R()?.defersDeath(state)) { state.is_alive = true; state.is_dead = false; return false; }
    state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false; endDodge(state);
    return true;
  }

  function finish(state, outcome, incoming, affectedStates) {
    B()?.endDamageSensitive(state);
    if (!state.concentration) return outcome;
    if (!C()) throw new Error("Browser concentration runtime is not loaded.");
    C().resolveDamage(state, incoming, affectedStates);
    return outcome;
  }

  function loseHitPoints(state, amount, affectedStates = []) {
    try {
      if (!Number.isInteger(amount) || amount < 0) throw new Error("Hit Point loss must be a nonnegative integer.");
      if (!amount || state.is_dead || state.current_hp === 0) return 0;
      const before = state.current_hp;
      state.current_hp = Math.max(0, before - amount);
      const lost = before - state.current_hp;
      if (state.current_hp > 0) return lost;
      if (activateReplacement(state)) return lost;
      if (useRelentless(state, 0)) return lost;
      if (state.template.kind === "monster") markDead(state);
      else markUnconscious(state);
      C()?.endIfIncapacitated(state, affectedStates);
      return lost;
    } catch (error) {
      console.error("Failed browser direct Hit Point loss.", { name: state?.template?.name, error });
      throw error;
    }
  }

  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = []) {
    const incoming = amount;
    if (!incoming || state.is_dead) return "damaged";
    R()?.noteDamageTypes(state, damageTypes);
    const absorbed = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= absorbed; amount -= absorbed;
    if (state.current_hp === 0) {
      if (state.template.kind === "monster" || incoming >= S().effectiveMaxHp(state)) {
        return finish(state, markDead(state) ? "dead" : "damaged", incoming, affectedStates);
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
    if (activateReplacement(state)) return "zero_hp_replacement";
    if (useUndeadFortitude(state, incoming, damageTypes, critical)) return finish(state, "undead_fortitude", incoming, affectedStates);
    if (state.template.kind === "monster") return finish(state, markDead(state) ? "dead" : "damaged", incoming, affectedStates);
    const remaining = Math.max(0, amount - before);
    if (remaining >= S().effectiveMaxHp(state)) { markDead(state); return finish(state, "dead", incoming, affectedStates); }
    if (useRelentless(state, remaining)) return finish(state, "relentless_endurance", incoming, affectedStates);
    markUnconscious(state);
    return finish(state, "unconscious", incoming, affectedStates);
  }

  window.IRON_PIT_BROWSER_ZERO_HP = { applyDamage, applyReplacementEffect, loseHitPoints };
})();