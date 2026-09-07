(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function isBloodied(state) {
    return state.current_hp * 2 <= S().effectiveMaxHp(state);
  }

  function attackAdvantage(attacker, target) {
    const targetState = Number(
      attacker.state.template.traits?.includes("target-missing-hp-attack-advantage")
      && target.state.current_hp < S().effectiveMaxHp(target.state)
    );
    const attackerState = Number(
      attacker.state.template.traits?.includes("bloodied-attack-save-advantage")
      && isBloodied(attacker.state)
    );
    return targetState + attackerState;
  }

  const attack = window.IRON_PIT_BROWSER_ATTACK;
  if (!attack?.resolveAttack) throw new Error("Browser attack runtime must load before target-state modifiers.");
  const baseResolveAttack = attack.resolveAttack;
  attack.resolveAttack = function resolveTargetStateAttack(sequence, round, attacker, target, attackProfile, distance, extra = {}) {
    const advantage = (extra.advantage || 0) + attackAdvantage(attacker, target);
    return baseResolveAttack(sequence, round, attacker, target, attackProfile, distance, { ...extra, advantage });
  };

  window.IRON_PIT_BROWSER_TARGET_STATE = { attackAdvantage, isBloodied };
})();
