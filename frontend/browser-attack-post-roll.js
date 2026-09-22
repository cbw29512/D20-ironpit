(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MISS_TO_HIT
    || { resolve: (_state, hit) => ({ hit: Boolean(hit), used: false }) };
  const D = () => window.IRON_PIT_BROWSER_D20_OVERRIDE
    || { apply: (_state, roll) => ({ roll, used: false }) };
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(attacker, target, attack, roll, baseTargetAc, turnKey, offTurn = false) {
    let resolvedRoll = roll;
    let natural = resolvedRoll.selected_roll;
    let naturalOne = natural === 1;
    const initialHit = !naturalOne && (natural === 20 || resolvedRoll.total >= baseTargetAc);

    const parry = window.IRON_PIT_BROWSER_REACTIONS?.parryHit?.(
      target.state, attack, resolvedRoll, initialHit, baseTargetAc,
    ) || { hit: initialHit, used: false };
    let hit = parry.hit;
    const targetAc = baseTargetAc
      + (parry.used ? target.state.template.parry_reaction.ac_bonus : 0);

    const missToHit = M().resolve(attacker.state, hit, turnKey);
    hit = missToHit.hit;

    let d20Override = { roll: resolvedRoll, used: false };
    if (!hit) {
      d20Override = D().apply(attacker.state, resolvedRoll, targetAc);
      resolvedRoll = d20Override.roll;
      natural = resolvedRoll.selected_roll;
      naturalOne = natural === 1;
      hit = !naturalOne && (natural === 20 || resolvedRoll.total >= targetAc);
    }

    const naturalOneEndsTurn = naturalOne && !offTurn && !hit;
    if (naturalOneEndsTurn) {
      S().terminateTurn(attacker.state, "iron-pit-natural-1-attack");
    }
    return {
      roll: resolvedRoll, hit, targetAc, natural,
      parry, missToHit, d20Override, naturalOneEndsTurn,
    };
  }

  window.IRON_PIT_BROWSER_ATTACK_POST_ROLL = { resolve };
})();
