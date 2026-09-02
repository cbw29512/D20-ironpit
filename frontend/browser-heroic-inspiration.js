(() => {
  "use strict";

  const standaloneHit = (natural, modifier, targetAc) => natural !== 1 && (natural === 20 || natural + modifier >= targetAc);

  function grant(state) {
    if (!state.template.heroic_warrior || state.heroic_inspiration) return false;
    state.heroic_inspiration = true;
    return true;
  }

  function rerollIndex(roll, targetAc) {
    if (!Number.isInteger(roll.selected_roll)) throw new Error("Heroic Inspiration requires a selected d20 roll.");
    if (standaloneHit(roll.selected_roll, roll.modifier, targetAc)) return null;
    if (roll.mode === "normal") {
      if (roll.rolls.length !== 1) throw new Error("Normal d20 roll must contain exactly one die.");
      return 0;
    }
    if (!Array.isArray(roll.rolls) || roll.rolls.length !== 2) throw new Error("Advantage or Disadvantage d20 roll must contain exactly two dice.");
    if (roll.mode === "advantage") return roll.rolls[0] <= roll.rolls[1] ? 0 : 1;
    if (roll.mode === "disadvantage") {
      const lower = roll.rolls[0] <= roll.rolls[1] ? 0 : 1, other = 1 - lower;
      return standaloneHit(roll.rolls[other], roll.modifier, targetAc) ? lower : null;
    }
    throw new Error(`Unsupported d20 roll mode for Heroic Inspiration: ${roll.mode}.`);
  }

  function rerollFailedAttack(state, roll, targetAc) {
    if (!state.heroic_inspiration) return { roll, used: false };
    const index = rerollIndex(roll, targetAc);
    if (index === null) return { roll, used: false };
    const rerolled = [...roll.rolls];
    rerolled[index] = window.IRON_PIT_DICE.roll(20);
    const selected = roll.mode === "advantage" ? Math.max(...rerolled)
      : roll.mode === "disadvantage" ? Math.min(...rerolled) : rerolled[0];
    state.heroic_inspiration = false;
    return {
      used: true,
      roll: { ...roll, rolls: rerolled, selected_roll: selected, total: selected + roll.modifier,
        notation: `${roll.notation} [Heroic Inspiration]` },
    };
  }

  window.IRON_PIT_BROWSER_HEROIC_INSPIRATION = { grant, rerollFailedAttack, standaloneHit };
})();
