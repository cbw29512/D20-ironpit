(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_AURAS || { savingThrowAdvantageSources: () => 0 };
  const F = () => window.IRON_PIT_BROWSER_SAVE_FAILURE_EFFECTS;
  const S = () => window.IRON_PIT_BROWSER_SAVES;

  function eligible(state, filter = {}) {
    const creatureType = String(state.template.creature_type || "").toLowerCase();
    const tags = new Set((state.template.creature_tags || []).map((item) => String(item).toLowerCase()));
    const excludedTypes = new Set((filter.excludedCreatureTypes || []).map((item) => String(item).toLowerCase()));
    const excludedTags = new Set((filter.excludedTags || []).map((item) => String(item).toLowerCase()));
    if (excludedTypes.has(creatureType)) return false;
    return ![...excludedTags].some((tag) => tags.has(tag));
  }

  function resolve(attacker, target, attack, round, distance, setup = null) {
    const rider = attack.onHitSavingThrow;
    if (!rider || target.state.is_dead || !target.state.is_alive) return null;
    if (!eligible(target.state, rider.targetFilter)) {
      return { targetEligible: false, saveRoll: null, saveAbility: rider.saveAbility, saveDc: rider.dc, saveSucceeded: null, applied: [] };
    }
    if (!S() || !F()) throw new Error("Browser attack save-rider dependencies are not loaded.");
    const save = S().resolveSavingThrow(
      target.state, rider.saveAbility, rider.dc, Boolean(rider.magicalEffect),
      A().savingThrowAdvantageSources(target, setup),
    );
    const applied = save.succeeded ? [] : F().apply(
      target, attacker.combatant_id, attack.id, rider.failureEffects || [], { round, range: attack.reach || 0 },
    );
    return { targetEligible: true, saveRoll: save.roll, saveAbility: rider.saveAbility, saveDc: rider.dc, saveSucceeded: save.succeeded, applied };
  }

  window.IRON_PIT_BROWSER_ATTACK_SAVE_RIDERS = { eligible, resolve };
})();
