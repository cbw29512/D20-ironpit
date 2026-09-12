(() => {
  "use strict";

  function deathSaveRoll(state, dice) {
    const advantage = state.template.death_save_advantage === true;
    const rolls = advantage ? [dice.roll(20), dice.roll(20)] : [dice.roll(20)];
    return {
      rolls,
      selected: Math.max(...rolls),
      mode: advantage ? "advantage" : "normal",
      recoveryMinimum: state.template.death_save_recovery_minimum || 20,
    };
  }

  function startTurnHealing(state) {
    const amount = state.template.bloodied_start_turn_healing || 0;
    const maximum = state.template.max_hp + (state.max_hp_bonus || 0);
    if (!amount || state.is_dead || state.current_hp <= 0 || state.current_hp * 2 > maximum) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(maximum, state.current_hp + amount);
    return state.current_hp - before;
  }

  window.IRON_PIT_BROWSER_PROGRESSION_RECOVERY = { deathSaveRoll, startTurnHealing };
})();
