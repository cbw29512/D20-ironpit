(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll, savingThrowFlat: () => 0 };
  const S = () => window.IRON_PIT_BROWSER_SAVES;

  function config(state) {
    const template = state.template || {};
    if (template.failed_save_reroll_resource_id) {
      return {
        sourceId: template.failed_save_reroll_source_id || template.failed_save_reroll_resource_id,
        resourceId: template.failed_save_reroll_resource_id,
        bonus: template.failed_save_reroll_bonus || 0,
      };
    }
    if (template.indomitable_reroll === true || (template.indomitable_bonus || 0) > 0) {
      return { sourceId: "indomitable", resourceId: "indomitable", bonus: template.indomitable_bonus || 0 };
    }
    return null;
  }

  function use(state, ability) {
    const setup = config(state);
    if (!setup) return null;
    const uses = state.resources?.[setup.resourceId] || 0;
    const saveBonus = state.template.saving_throw_bonuses?.[ability];
    if (!uses) return null;
    if (saveBonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    state.resources[setup.resourceId] -= 1;
    const roll = M().applyD20Bonus(
      state,
      "saving-throw-bonus-die",
      R().d20(saveBonus + M().savingThrowFlat(state) + setup.bonus, S().saveMode(state, ability)),
    );
    const suffix = setup.bonus ? ` +${setup.bonus}` : "";
    const label = setup.sourceId.replaceAll("-", " ").replace(/\b\w/g, (char) => char.toUpperCase());
    return { ...roll, notation: `${roll.notation} [${label}${suffix}]`, sourceId: setup.sourceId };
  }

  window.IRON_PIT_BROWSER_INDOMITABLE = { use };
})();
