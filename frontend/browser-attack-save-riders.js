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
      target, attacker.combatant_id, attack.id, rider.failureEffects || [], { round, range: attack.reach || distance },
    );
    return { targetEligible: true, saveRoll: save.roll, saveAbility: rider.saveAbility, saveDc: rider.dc, saveSucceeded: save.succeeded, applied };
  }

  function targetForEvent(target, setup, event) {
    if (target.combatant_id === event.target_id || !setup) return target;
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === event.target_id) || target;
  }

  function install() {
    const api = window.IRON_PIT_BROWSER_ATTACK;
    if (!api || api.__hitSaveRidersInstalled) return false;
    const base = api.resolveAttack;
    api.resolveAttack = function (...args) {
      const [, round, attacker, target, attack, distance, extra = {}] = args;
      const event = base(...args);
      if (!event.hit || !attack.onHitSavingThrow) return event;
      const actualTarget = targetForEvent(target, extra.setup, event);
      const outcome = resolve(attacker, actualTarget, attack, round, distance, extra.setup || null);
      if (!outcome) return event;
      if (!outcome.targetEligible) {
        event.description += ` ${actualTarget.state.template.name} is ineligible for the attached saving throw effect.`;
        return event;
      }
      event.saving_throw_roll = outcome.saveRoll;
      event.save_ability = outcome.saveAbility;
      event.save_dc = outcome.saveDc;
      event.save_succeeded = outcome.saveSucceeded;
      event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), ...outcome.applied])];
      event.description += ` ${actualTarget.state.template.name} ${outcome.saveSucceeded ? "succeeds" : "fails"} the DC ${outcome.saveDc} ${outcome.saveAbility} hit-effect save.`;
      return event;
    };
    api.__hitSaveRidersInstalled = true;
    return true;
  }

  window.IRON_PIT_BROWSER_ATTACK_SAVE_RIDERS = { eligible, install, resolve };
})();
