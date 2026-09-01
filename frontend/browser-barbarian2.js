(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const EFFECT_ID = "reckless-attack";

  function active(state) {
    return Boolean(state?.active_effect_ids?.includes(EFFECT_ID));
  }

  function dangerSenseAdvantage(state, ability) {
    return Number(Boolean(state?.template?.danger_sense) && ability === "dexterity" && !Q().incapacitated(state));
  }

  function activate(member, attack, round) {
    if (!member?.state?.template?.reckless_attack || attack?.attackAbility !== "strength" || active(member.state)) return false;
    const applied = T()?.apply(member.state, EFFECT_ID, member.combatant_id, {
      sourceEffectId: EFFECT_ID, appliedRound: round, expiresRound: round + 1, expiryTiming: "source_turn_start",
    });
    if (applied !== EFFECT_ID) throw new Error("Reckless Attack effect could not be applied.");
    return true;
  }

  function attackAdvantage(state, attack) {
    return Number(active(state) && attack?.attackAbility === "strength");
  }

  function attacksAgainstAdvantage(state) {
    return Number(active(state));
  }

  window.IRON_PIT_BROWSER_BARBARIAN2 = {
    active, activate, attackAdvantage, attacksAgainstAdvantage, dangerSenseAdvantage,
  };
})();
