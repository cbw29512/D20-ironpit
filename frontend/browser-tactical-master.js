(() => {
  "use strict";

  const EFFECT_ID = "tactical-master-sap";
  const SOURCE_EFFECT_ID = "tactical-master";
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function eligible(state, attack) {
    return Boolean(state.template.tactical_master_sap)
      && (state.template.weapon_masteries || []).includes(attack.weaponId || attack.weapon_id || attack.id.replace(/^karnok-/, ""));
  }

  function apply(attacker, target, attack, round) {
    if (!eligible(attacker.state, attack) || target.state.is_dead || target.state.current_hp <= 0) return false;
    return Boolean(T().apply(target.state, EFFECT_ID, attacker.combatant_id, {
      sourceEffectId: SOURCE_EFFECT_ID,
      appliedRound: round,
      expiresRound: round + 1,
      expiryTiming: "source_turn_start",
    }));
  }

  const disadvantage = (state) => state.timed_effects.some((effect) => effect.effect_id === EFFECT_ID) ? 1 : 0;

  function consume(state) {
    const effects = state.timed_effects.filter((effect) => effect.effect_id === EFFECT_ID);
    for (const effect of [...effects]) T().removeEffect(state, effect);
    return effects.length;
  }

  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply, consume, disadvantage, eligible };
})();
