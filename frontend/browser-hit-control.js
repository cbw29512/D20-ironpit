(() => {
  "use strict";
  const T = () => window.IRON_PIT_BROWSER_TIMED, V = () => window.IRON_PIT_BROWSER_SAVES;
  const baseType = (state) => String(state.template.creature_type || "").split("(", 1)[0].trim().toLowerCase();
  function eligible(control, state) {
    const types = new Set((control.excludedCreatureTypes || []).map((item) => String(item).toLowerCase()));
    const species = new Set((control.excludedSpeciesIds || []).map((item) => String(item).toLowerCase()));
    return !types.has(baseType(state)) && !species.has(String(state.template.species_id || "").toLowerCase());
  }
  function resolve(attack, attacker, target, round) {
    const control = attack.controlEffect, empty = { applied: [], saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null };
    if (!control?.conditionId || !control.initialSaveAbility || target.state.is_dead || !target.state.is_alive || !eligible(control, target.state)) return empty;
    const save = V().resolveSavingThrow(target.state, control.initialSaveAbility, control.initialSaveDc);
    if (save.succeeded) return { ...empty, saveRoll: save.roll, saveAbility: control.initialSaveAbility, saveDc: control.initialSaveDc, saveSucceeded: true };
    const timed = T().apply(target.state, control.conditionId, attacker.combatant_id, {
      sourceEffectId: attack.id, appliedRound: round, expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn),
      expiryTiming: control.expiryTiming || null, repeatSaveAbility: control.repeatSaveAbility || null,
      repeatSaveDc: control.repeatSaveDc || null, repeatSaveTiming: control.repeatSaveTiming || null,
      allowedRemovalActionIds: control.allowedRemovalActionIds || [],
    });
    return { applied: timed ? [timed] : [], saveRoll: save.roll, saveAbility: control.initialSaveAbility, saveDc: control.initialSaveDc, saveSucceeded: false };
  }
  window.IRON_PIT_BROWSER_HIT_CONTROL = { eligible, resolve };
})();
