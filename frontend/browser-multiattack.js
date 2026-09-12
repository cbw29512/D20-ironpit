(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const D = () => window.IRON_PIT_DICE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const WM = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || { resolveCleave: (sequence) => ({ events: [], sequence }) };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function areaChoice(member, setup, data) {
    return AS()?.choice(member, setup, false, data.saveActionIds) || null;
  }
  function saveChoice(member, setup, data) {
    const allowed = new Set(data.saveActionIds);
    for (const target of F().targetOrder(member, setup)) {
      const action = (member.state.template.saving_throw_actions || []).find((item) => {
        const distance = F().saveDistance(member, target, item.range);
        return !item.area && allowed.has(item.id) && V().legalAction(item, target, distance);
      });
      if (action) return { target, save: action, distance: F().saveDistance(member, target, action.range) };
    }
    return null;
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
      return Boolean(attackChoice(member, setup, data) || areaChoice(member, setup, data) || saveChoice(member, setup, data));
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
    if (!slots?.length || !E().available(member.state, "action") || !F().targetOrder(member, setup).length) {
      return { events: [], sequence };
    }
    if (!slots.some((slot) => slotHasLegalChoice(member, setup, slot))) return { events: [], sequence };
    const events = [];
    E().spend(member.state, "action");
    let openingFeature = C()?.openingFeature?.(round, member, setup) || null;
    let lightTrigger = null, rangedSplitUsed = false;
    const rangedSplit = useRangedSplit(member, setup, slots);
    const turnKey = `${round}:${member.combatant_id}`;

    for (let index = 0; index < slots.length; index += 1) {
      if (member.state.is_dead || member.state.is_unconscious || member.state.turn_terminated) break;
      const data = slotData(slots[index]);
      const splitThis = index > 0 && rangedSplit && !rangedSplitUsed && F().flexibleSlotHasBoth(member, data.attackIds);
      const choice = attackChoice(member, setup, data, splitThis);
      if (choice) {
        if (splitThis && choice.attack.kind === "ranged") rangedSplitUsed = true;
        const pack = window.IRON_PIT_BROWSER_STATE.packTactics(member, choice.target, setup);
        const featureId = openingFeature || (pack ? "pack-tactics" : definition.id);
        const event = A().resolveAttack(sequence++, round, member, choice.target, choice.attack, choice.distance, {
          spendAction: false, advantage: pack ? 1 : 0, setup, featureId, turnKey,
          allowReckless: true, ignoreCloseThreat: true,
        });
        events.push(event);
        if (member.state.turn_terminated) break;
        const cleave = WM().resolveCleave(sequence, round, member, event, choice.attack, setup, turnKey);
        events.push(...cleave.events); sequence = cleave.sequence;
        if (definition.isAttackAction && !lightTrigger && choice.attack.light) lightTrigger = choice.attack;
        openingFeature = null;
        continue;
      }
      const area = areaChoice(member, setup, data);
      if (area) {
        const resolved = AS().resolve(sequence, round, member, setup, false, { allowedIds: data.saveActionIds, spendAction: false });
        if (resolved) { events.push(...resolved.events); sequence = resolved.sequence; continue; }
      }
      const saved = saveChoice(member, setup, data);
      if (saved) events.push(V().resolveAction(sequence++, round, member, saved.target, saved.save, saved.distance, { spendAction: false }));
    }

    if (definition.isAttackAction && lightTrigger && !member.state.turn_terminated) {
      const extra = R().resolve(sequence, round, member, setup, lightTrigger, turnKey);
      events.push(...extra.events); sequence = extra.sequence;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();