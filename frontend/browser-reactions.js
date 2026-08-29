(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const PROVOKING = new Set(["speed", "action", "bonus_action", "reaction"]);

  function meleeDepartureAttack(member, before, after) {
    return (member.state.template.attacks || []).find((attack) =>
      attack.kind === "melee" && before <= (attack.reach || 5) && after > (attack.reach || 5),
    ) || null;
  }

  function resolveOpportunityAttack(sequence, round, reactor, mover, setup, before, after, movementSource, options = {}) {
    if (reactor.side === mover.side || options.canSee === false || options.disengaged === true) return null;
    if (!PROVOKING.has(movementSource) || !E().available(reactor.state, "reaction")) return null;
    const attack = meleeDepartureAttack(reactor, before, after);
    if (!attack) return null;
    E().spend(reactor.state, "reaction");
    const pack = S().packTactics(reactor, setup);
    return A().resolveAttack(sequence, round, reactor, mover, attack, before, {
      spendAction: false,
      advantage: pack ? 1 : 0,
      featureId: "opportunity-attack",
    });
  }

  window.IRON_PIT_BROWSER_REACTIONS = { resolveOpportunityAttack };
})();
