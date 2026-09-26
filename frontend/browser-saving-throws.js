(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { dangerSenseAdvantage: () => 0 };
  const DG = () => window.IRON_PIT_BROWSER_DODGE || { dexSaveAdvantageSources: () => 0 }, DF = () => window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS || { saveAdvantage: () => 0, saveAdvantageSourceNames: () => [] };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll, savingThrowFlat: () => 0 }, DB = () => window.IRON_PIT_BROWSER_D20_BONUS_DICE;
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION || { saveDisadvantage: () => 0 };
  const DO = () => window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE || { apply: (_state, roll) => ({ roll, featureId: null, sourceName: null }), sourceNameForRoll: () => null };
  const FR = () => window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL || { apply: (_state, roll) => ({ roll, featureId: null, sourceName: null }) };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { autoFailStrDex: (state) => state.is_unconscious };

  function sureFootedAdvantage(state, ability, context = {}) {
    try {
      if (!state.template.traits?.includes("sure-footed")) return 0;
      if (ability !== "strength" && ability !== "dexterity") return 0;
      return context.conditionId === "prone" ? 1 : 0;
    } catch (error) {
      console.error("Failed to resolve browser Sure-Footed save Advantage.", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  function saveMode(state, ability, context = {}) {
    try {
      const advantage = (ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0)
        + B2().dangerSenseAdvantage(state, ability)
        + DG().dexSaveAdvantageSources(state, ability) + DF().saveAdvantage(state, ability, context)
        + sureFootedAdvantage(state, ability, context);
      const disadvantage = X().saveDisadvantage(state) + (DF().saveDisadvantage?.(state) || 0)
        + (context.disadvantageSources || []).length
        + (ability === "dexterity" && state.active_effect_ids.includes("restrained") ? 1 : 0);
      return R().modeFromSources(advantage, disadvantage);
    } catch (error) {
      console.error("Saving-throw saveMode failed.", { error });
      throw error;
    }
  }

  function indomitableRevision(original, replacement) {
    try {
      return {
        source_effect_id: "indomitable", kind: "full_reroll",
        original_rolls: [...original.rolls], replacement_rolls: [...replacement.rolls],
        original_modifier: original.modifier || 0, replacement_modifier: replacement.modifier || 0,
        original_selected: original.selected_roll, replacement_selected: replacement.selected_roll,
        original_total: original.total, replacement_total: replacement.total, accepted: "replacement", replaced_die_index: null,
      };
    } catch (error) {
      console.error("Saving-throw indomitableRevision failed.", { error });
      throw error;
    }
  }

  function resolveSavingThrow(state, ability, dc, context = {}) {
    try {
      if ((ability === "strength" || ability === "dexterity") && Q().autoFailStrDex(state)) {
        DF().consumeSavingThrowModifiers?.(state);
        return { roll: null, succeeded: false };
      }
      const baseBonus = state.template.saving_throw_bonuses?.[ability];
      if (baseBonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
      const modifiers = M();
      const bonus = baseBonus + (modifiers.savingThrowFlat?.(state) || 0);
      const baseRoll = R().d20(bonus, saveMode(state, ability, context));
      let roll = modifiers.applyD20Bonus?.(state, "saving-throw-bonus-die", baseRoll) || baseRoll; if ((state.active_d20_bonus_dice || []).length) { if (!Number.isInteger(context.roundNumber)) throw new Error("Active d20 bonus die requires saving-throw round context."); roll = DB().applyIfUseful(state, "saving_throw", roll, dc, context.roundNumber).roll; }
      DF().consumeSavingThrowModifiers?.(state);
      if (roll.total < dc) {
        const reroll = window.IRON_PIT_BROWSER_INDOMITABLE?.use(state, ability);
        if (reroll) roll = { ...reroll, revisions: [...(reroll.revisions || []), indomitableRevision(roll, reroll)] };
      }
      if (roll.total < dc) {
        const rerollGrants = state.template.failed_save_reroll_grants || [];
        if (rerollGrants.length && !window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL) {
          throw new Error("Failed-save reroll runtime is not loaded for a declared saving-throw capability.");
        }
        roll = FR().apply(state, roll).roll;
      }
      const d20Grants = state.template.failed_d20_test_override_grants || [];
      if (d20Grants.some((grant) => (grant.test_kinds || []).includes("saving_throw"))
        && !window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE) {
        throw new Error("Failed-D20 override runtime is not loaded for a declared saving-throw capability.");
      }
      roll = DO().apply(state, roll, roll.total < dc, "saving_throw").roll;
      return { roll, succeeded: roll.total >= dc };
    } catch (error) {
      console.error("Saving-throw resolveSavingThrow failed.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVING_THROWS = { resolveSavingThrow, saveMode };
})();
