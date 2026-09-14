(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const F = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;

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
      ...failedCheck, notation: `${failedCheck.notation}+1d10`,
      rolls: [...failedCheck.rolls, bonus], total: failedCheck.total + bonus,
    };
    const succeeded = roll.total >= dc;
    if (succeeded) state.resources["second-wind"] -= 1;
    return { roll, used: true, succeeded, resource_remaining: state.resources["second-wind"] };
  }

  function abilityModifier(state, ability) {
    const direct = state.template.ability_modifiers?.[ability];
    if (Number.isInteger(direct)) return direct;
    const attack = (state.template.attacks || []).find((item) => item.attackAbility === ability && Number.isInteger(item.attackAbilityModifier));
    if (attack) return attack.attackAbilityModifier;
    throw new Error(`${state.template.name} lacks a certified ${ability} ability modifier.`);
  }

  function abilityCheck(state, ability) {
    const advantage = ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0;
    const disadvantage = (state.active_effect_ids.includes("poisoned") || state.active_effect_ids.includes("frightened") ? 1 : 0)
      + (T()?.abilityCheckDisadvantage?.(state) || 0) + (ability === "strength" ? (T()?.strengthD20Disadvantage?.(state) || 0) : 0);
    return R().d20(abilityModifier(state, ability), R().modeFromSources(advantage, disadvantage));
  }

  function applyContestedMovement(event, source, target, attack, setup) {
    const effect = attack.onHitContestedMovement;
    if (!event.hit || !effect || !setup || !target.state.is_alive || target.state.is_dead) return;
    if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) return;
    if (!F() || !R()) throw new Error("Contested movement dependencies are not loaded.");
    const sourceRoll = abilityCheck(source.state, effect.sourceAbility);
    let targetRoll = abilityCheck(target.state, effect.targetAbility);
    let succeeded = targetRoll.total >= sourceRoll.total, tactical = null;
    if (!succeeded) {
      tactical = apply(target.state, targetRoll, sourceRoll.total);
      targetRoll = tactical.roll; succeeded = tactical.succeeded;
    }
    let moved = 0;
    if (!succeeded) moved = effect.direction === "away_from_source"
      ? F().pushAway(source, target, effect.distanceFt, setup)
      : F().pullToward(source, target, effect.distanceFt, setup);
    event.ability_check_roll = targetRoll; event.check_ability = effect.targetAbility;
    event.check_dc = sourceRoll.total; event.check_succeeded = succeeded;
    if (moved) event.movement_ft = (event.movement_ft || 0) + moved;
    const tacticalText = tactical?.used ? " after using Tactical Mind" : "";
    const outcome = succeeded ? "resists" : `is moved ${moved} feet`;
    event.description += ` ${target.state.template.name} ${outcome}${tacticalText} in the opposed ${effect.targetAbility} check (${targetRoll.total} vs. ${sourceRoll.total}).`;
  }

  window.IRON_PIT_BROWSER_TACTICAL_MIND = { apply, available };
  window.IRON_PIT_BROWSER_CONTESTED_MOVEMENT = { apply: applyContestedMovement };
})();
