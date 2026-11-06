(() => {
  "use strict";

  // A generic failed-save execution can heal its source, but only if the
  // target actually dies after universal instant-death prevention.
  function resolve(actor, target, action, saveSucceeded, setup = null) {
    try {
      if (!action.instantDeathOnFailedSave || saveSucceeded) {
        return { died: false, healed: 0, healingRoll: null };
      }
      if (!action.requiresTargetZeroHpAlive
        || target.state.current_hp !== 0 || !target.state.is_alive || target.state.is_dead) {
        throw new Error(action.name + " requires a living creature at zero HP.");
      }
      const terminal = window.IRON_PIT_BROWSER_ZERO_HP;
      const healing = window.IRON_PIT_BROWSER_HEALING;
      if (!terminal?.applyInstantDeath || !healing?.restore) {
        throw new Error("Save finisher requires shared terminal-death and healing runtimes.");
      }
      const states = setup ? [...setup.heroes, ...setup.monsters].map(m => m.state) : [];
      terminal.applyInstantDeath(target.state, states);
      if (!target.state.is_dead) return { died: false, healed: 0, healingRoll: null };
      const rolls = Array.from(
        { length: action.healSourceOnKillDiceCount },
        () => window.IRON_PIT_DICE.roll(action.healSourceOnKillDiceSize),
      );
      const total = rolls.reduce((sum, roll) => sum + roll, 0);
      const healed = healing.restore(actor.state, total);
      return {
        died: true, healed,
        healingRoll: {
          notation: rolls.length + "d" + action.healSourceOnKillDiceSize,
          rolls, modifier: 0, total,
        },
      };
    } catch (error) {
      console.error("Save-based instant-death/healing resolution failed.", { action: action?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_FINISHER = { resolve };
})();
