(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function applyCondition(target, sourceId, sourceEffectId, control, round, affectedStates) {
    const id = control?.conditionId;
    if (!id || I().immune(target.state, id)) return null;
    if (id === "prone") {
      if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
      return "prone";
    }
    return T()?.apply(target.state, id, sourceId, {
      sourceEffectId, appliedRound: round,
      expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn),
      expiryTiming: control.expiryTiming || null,
      repeatSaveAbility: control.repeatSaveAbility || null,
      repeatSaveDc: control.repeatSaveDc || null,
      repeatSaveTiming: control.repeatSaveTiming || null,
      allowedRemovalActionIds: control.allowedRemovalActionIds || [],
      affectedStates,
    }) || null;
  }

  function applyPersistent(target, sourceId, sourceEffectId, control, rangeFt, round = null, affectedStates = []) {
    if (!control || target.state.is_dead || !target.state.is_alive) return [];
    if (control.maxTargetSize && !S().sizeAtMost(target, control.maxTargetSize)) return [];
    const applied = [];
    if (control.grappleEscapeDc) applied.push(...G().apply(
      target.state, sourceId, control.grappleEscapeDc, rangeFt, Boolean(control.restrainsWhileGrappled),
    ));
    const condition = applyCondition(target, sourceId, sourceEffectId, control, round, affectedStates);
    if (condition) applied.push(condition);
    return [...new Set(applied)];
  }

  function applyMovement(source, target, control, event = null) {
    if (!control || target.state.is_dead || !target.state.is_alive) return null;
    const result = F()?.apply(source, target, control) || null;
    if (!result || !event) return result;
    event.distance_before_ft = result.beforeDistanceFt;
    event.distance_after_ft = result.afterDistanceFt;
    event.movement_ft = result.movedFt;
    const verb = result.direction === "push" ? "pushed" : "pulled";
    event.description += result.movedFt
      ? ` ${target.state.template.name} is ${verb} ${result.movedFt} feet.`
      : ` ${target.state.template.name} cannot be ${verb} farther in the Pit.`;
    return result;
  }

  window.IRON_PIT_BROWSER_CONTROL = { applyMovement, applyPersistent };
})();
