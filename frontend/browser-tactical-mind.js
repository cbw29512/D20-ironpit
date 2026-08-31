(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function available(state) {
    return state.template.archetype?.toLowerCase() === "fighter"
      && Number(state.template.level || 0) >= 2
      && (state.resources["second-wind"] || 0) > 0;
  }

  function apply(state, failedCheck, dc) {
    if (failedCheck.total >= dc || !available(state)) {
      return { roll: failedCheck, used: false, succeeded: failedCheck.total >= dc, resource_remaining: null };
    }
    const bonus = D().roll(10);
    const roll = {
      ...failedCheck,
      notation: `${failedCheck.notation}+1d10`,
      rolls: [...failedCheck.rolls, bonus],
      total: failedCheck.total + bonus,
    };
    const succeeded = roll.total >= dc;
    if (succeeded) state.resources["second-wind"] -= 1;
    return {
      roll,
      used: true,
      succeeded,
      resource_remaining: state.resources["second-wind"],
    };
  }

  window.IRON_PIT_BROWSER_TACTICAL_MIND = { apply, available };
})();
