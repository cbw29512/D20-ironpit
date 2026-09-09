(() => {
  "use strict";

  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { dangerSenseAdvantage: () => 0 };
  const D = () => window.IRON_PIT_DICE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { autoFailStrDex: (state) => state.is_unconscious };
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const U = () => window.IRON_PIT_BROWSER_RESOURCES;

  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];

  function saveMode(state, ability, magicalEffect = false) {
    let advantage = (ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0)
      + B2().dangerSenseAdvantage(state, ability);
    if (magicalEffect && state.template.traits?.includes("magic-resistance")) advantage += 1;
    const disadvantage = ability === "dexterity" && state.active_effect_ids.includes("restrained") ? 1 : 0;
    return R().modeFromSources(advantage, disadvantage);
  }

  function evasionApplies(state, action) {
    return action.saveAbility === "dexterity" && action.successDamage === "half"
      && state.template.traits?.includes("evasion");
  }

  function revision(original, replacement) {
    return {
      source_effect_id: "indomitable", kind: "full_reroll",
      original_rolls: [...original.rolls], replacement_rolls: [...replacement.rolls],
      original_modifier: original.modifier || 0, replacement_modifier: replacement.modifier || 0,
      original_selected: original.selected_roll, replacement_selected: replacement.selected_roll,
      original_total: original.total, replacement_total: replacement.total,
      accepted: "replacement", replaced_die_index: null,
    };
  }

  function resolveSavingThrow(state, ability, dc, magicalEffect = false) {
    if ((ability === "strength" || ability === "dexterity") && Q().autoFailStrDex(state)) return { roll: null, succeeded: false };
    const bonus = state.template.saving_throw_bonuses?.[ability];
    if (bonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    let roll = M().applyD20Bonus(state, "saving-throw-bonus-die", R().d20(bonus, saveMode(state, ability, magicalEffect)));
    if (roll.total < dc) {
      const reroll = window.IRON_PIT_BROWSER_INDOMITABLE?.use(state, ability);
      if (reroll) roll = { ...reroll, revisions: [...(reroll.revisions || []), revision(roll, reroll)] };
    }
    return { roll, succeeded: roll.total >= dc };
  }

  function legalAction(action, target, distance) {
    return distance <= action.range && (!action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize));
  }

  const resourceAvailable = (actor, action) => U().attackAvailable(actor.state, action);

  function damageRolls(action, count, shared) {
    if (shared == null) return D().rollMany(count, action.damageDiceSize);
    if (!Array.isArray(shared) || shared.length !== count) throw new Error(`${action.name} shared damage roll count is invalid.`);
    if (shared.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > action.damageDiceSize)) throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
    return [...shared];
  }

  function failureControl(action) {
    if (action.failureControl) return action.failureControl;
    if (!action.grappleEscapeDc) return null;
    return {
      maxTargetSize: action.targetMaxSize || null,
      grappleEscapeDc: action.grappleEscapeDc,
      restrainsWhileGrappled: Boolean(action.restrainsWhileGrappled),
    };
  }

  window.IRON_PIT_BROWSER_SAVE_HELPERS = {
    damageRolls, evasionApplies, failureControl, legalAction, resourceAvailable, resolveSavingThrow, saveMode, states,
  };
})();
