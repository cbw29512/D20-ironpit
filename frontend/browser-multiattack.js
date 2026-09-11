(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const AU = () => window.IRON_PIT_BROWSER_AURAS || { attackAdvantageSources: () => 0 };
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const D = () => window.IRON_PIT_DICE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const FM = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT_ACTION;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const R = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const WM = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || { resolveCleave: (sequence) => ({ events: [], sequence }) };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [], forcedMovementActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [], forcedMovementActionIds: slot.forcedMovementActionIds || [] };
  const sizeAllowed = (target, maximum) => !maximum || window.IRON_PIT_BROWSER_STATE.sizeAtMost(target, maximum);

  function movementChoice(member, setup, data) {
    const allowed = new Set(data.forcedMovementActionIds);
    return (member.state.template.forced_movement_actions || []).find((action) =>
      allowed.has(action.id) && FM()?.legalTargets(member, setup, action).length) || null;
  }
  function saveEffectIsNew(member, target, action, effect) {
    if (effect.kind === "prone") return sizeAllowed(target, effect.maxTargetSize) && !target.state.active_effect_ids.includes("prone") && !I().immune(target.state, "prone");
    if (effect.kind === "grapple") return sizeAllowed(target, effect.maxTargetSize) && !(target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id);
    if (effect.kind === "condition") {
      if (!sizeAllowed(target, effect.maxTargetSize) || I().immune(target.state, effect.condition)) return false;
      if (!target.state.active_effect_ids.includes(effect.condition)) return true;
      return !(target.state.timed_effects || []).some((timed) => timed.effect_id === effect.condition && timed.source_id === member.combatant_id && timed.source_effect_id === action.id);
    }
    if (["attacks-against-advantage", "speed"].includes(effect.kind)) return !(target.state.active_modifiers || []).some((modifier) => modifier.source_id === member.combatant_id && modifier.source_effect_id === action.id);
    throw new Error(`Unsupported mixed-slot failed-save effect: ${effect.kind}.`);
  }
  function preferSaveReplacement(member, target, action) {
    if ((action.failureEffects || []).some((effect) => saveEffectIsNew(member, target, action, effect))) return true;
    return action.grappleEscapeDc != null && !(target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id);
  }

  function saveChoice(member, setup, data) {
    try {
      const allowed = new Set(data.saveActionIds);
      for (const target of F().targetOrder(member, setup)) {
        const action = (member.state.template.saving_throw_actions || []).find((item) => {
          if (!RES().available(member.state, item.resourceId, item.resourceCost || 1)) return false;
          const distance = F().saveDistance(member, target, item.range);
          return allowed.has(item.id) && V().legalAction(item, target, distance);
        });
        if (action) return { target, save: action, distance: F().saveDistance(member, target, action.range) };
      }
      return null;
    } catch (error) {
      console.error("Failed browser Multiattack save choice", { member: member.combatant_id, error });
      throw error;
    }
  }
  function attackChoice(member, setup, data, rangedBackline = false) {
    if (rangedBackline) {
      const ranged = F().chooseAttack(member, setup, data.attackIds, "ranged", true);
      if (ranged) return ranged;
    }
    if (F().isBackline(member) && F().alliedFrontlineActive(member, setup)) {
      const ranged = F().chooseAttack(member, setup, data.attackIds, "ranged");
      if (ranged) return ranged;
    }
    return F().chooseAttack(member, setup, data.attackIds, "melee")
      || F().chooseAttack(member, setup, data.attackIds, "ranged");
  }
  function slotHasLegalChoice(member, setup, slot) {
    try {
      const data = slotData(slot);
      return Boolean(movementChoice(member, setup, data) || attackChoice(member, setup, data) || saveChoice(member, setup, data));
    } catch (error) {
      console.error("Failed to prove browser Attack/Multiattack slot legality", { member: member.combatant_id, error });
      throw error;
    }
  }
  function useRangedSplit(member, setup, slots) {
    if (F().isBackline(member)) return false;
    if (!F().hasFrontlineTarget(member, setup) || !F().hasBacklineTarget(member, setup)) return false;
    if (!slots.slice(1).some((slot) => F().flexibleSlotHasBoth(member, slotData(slot).attackIds))) return false;
    return D().roll(100) >= 76;
  }

  function resolveAttackAction(sequence, round, member, setup) {
    const definition = member.state.template.attack_action, slots = definition?.slots;
    if (!slots?.length || !E().available(member.state, "action") || !F().targetOrder(member, setup).length) return { events: [], sequence };
    if (!slots.some((slot) => slotHasLegalChoice(member, setup, slot))) return { events: [], sequence };
    const events = [];
    E().spend(member.state, "action");
    let openingFeature = C()?.openingFeature?.(round, member, setup) || null;
    let lightTrigger = null, rangedSplitUsed = false;
    const rangedSplit = useRangedSplit(member, setup, slots), turnKey = `${round}:${member.combatant_id}`;

    for (let index = 0; index < slots.length; index += 1) {
      if (member.state.is_dead || member.state.is_unconscious || member.state.turn_terminated) break;
      const data = slotData(slots[index]), movement = movementChoice(member, setup, data);
      if (movement) {
        const moved = FM().resolve(sequence, round, member, setup, movement);
        events.push(...moved.events); sequence = moved.sequence;
        continue;
      }
      const splitThis = index > 0 && rangedSplit && !rangedSplitUsed && F().flexibleSlotHasBoth(member, data.attackIds);
      const choice = attackChoice(member, setup, data, splitThis), saved = saveChoice(member, setup, data);
      if (saved && (!choice || preferSaveReplacement(member, saved.target, saved.save))) {
        events.push(V().resolveAction(sequence++, round, member, saved.target, saved.save, saved.distance, { spendAction: false, setup }));
        continue;
      }
      if (choice) {
        if (splitThis && choice.attack.kind === "ranged") rangedSplitUsed = true;
        const pack = window.IRON_PIT_BROWSER_STATE.packTactics(member, choice.target, setup);
        const advantage = (pack ? 1 : 0) + AU().attackAdvantageSources(member, setup);
        const featureId = openingFeature || (pack ? "pack-tactics" : definition.id);
        const event = A().resolveAttack(sequence++, round, member, choice.target, choice.attack, choice.distance, { spendAction: false, advantage, setup, featureId, turnKey, allowReckless: true, ignoreCloseThreat: true });
        events.push(event);
        if (member.state.turn_terminated) break;
        const cleave = WM().resolveCleave(sequence, round, member, event, choice.attack, setup, turnKey);
        events.push(...cleave.events); sequence = cleave.sequence;
        if (definition.isAttackAction && !lightTrigger && choice.attack.light) lightTrigger = choice.attack;
        openingFeature = null;
      }
    }

    if (definition.isAttackAction && lightTrigger && !member.state.turn_terminated) {
      const extra = R().resolve(sequence, round, member, setup, lightTrigger, turnKey);
      events.push(...extra.events); sequence = extra.sequence;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();
