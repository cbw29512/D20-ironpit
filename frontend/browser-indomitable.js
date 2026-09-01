(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll };
  const S = () => window.IRON_PIT_BROWSER_SAVES;

  function use(state, ability) {
    const bonus = state.template.indomitable_bonus || 0;
    const uses = state.resources?.indomitable || 0;
    const saveBonus = state.template.saving_throw_bonuses?.[ability];
    if (!bonus || !uses) return null;
    if (saveBonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    state.resources.indomitable -= 1;
    const roll = M().applyD20Bonus(
      state,
      "saving-throw-bonus-die",
      R().d20(saveBonus + bonus, S().saveMode(state, ability)),
    );
    return { ...roll, notation: `${roll.notation} [Indomitable +${bonus}]` };
  }

  window.IRON_PIT_BROWSER_INDOMITABLE = { use };
})();
