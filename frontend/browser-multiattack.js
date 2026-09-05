(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const D = () => window.IRON_PIT_DICE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const R = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const WM = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || { resolveCleave: (sequence) => ({ events: [], sequence }) };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] } : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function resourceAvailable(state, action) {
    if (!action.resourceId) return true;
    const service = V();
    if (!service?.resourceAvailable) throw new Error("Browser action-resource service is not loaded.");
    return service.resourceAvailable(state, action);
  }
  function consumeResource(state, action) {
    if (!action.resourceId) return null;
    const service = V();
    if (!service?.consumeResource) throw new Error("Browser action-resource service is not loaded.");
    return service.consumeResource(state, action);
  }
  function availableAttackIds(member, ids) {
    const profiles = member.state.template.attacks || [];
    return ids.filter((id) => {
      const attack = profiles.find((item) => item.id === id);
      return attack && resourceAvailable(member.state, attack);
    });
  }
  function saveChoice(member, setup, data) {
    if (!data.saveActionIds.length) return null;
    const service = V();
    if (!service?.resourceAvailable || !service?.legalAction) throw new Error("Browser save-action service is not loaded.");
    const allowed = new Set(data.saveActionIds);
    for (const target of F().targetOrder(member, setup)) {
      const action = (member.state.template.saving_throw_actions || []).find((item) => {
        const distance = F().saveDistance(member, target, item.range);
        return allowed.has(item.id) && service.resourceAvailable(member.state, item) && service.legalAction(item, target, distance);
      });
      if (action) return { target, save: action, distance: F().saveDistance(member, target, action.range) };
    }
    return null;
  }
  function attackChoice(member, setup, data, rangedBackline = false) {
    const ids = availableAttackIds(member, data.attackIds);
    if (rangedBackline) { const ranged = F().chooseAttack(member, setup, ids, "ranged", true); if (ranged) return ranged; }
    if (F().isBackline(member) && F().alliedFrontlineActive(member, setup)) {
      const ranged = F().chooseAttack(member, setup, ids, "ranged"); if (ranged) return ranged;
    }
    return F().chooseAttack(member, setup, ids, "melee") || F().chooseAttack(member, setup, ids, "ranged");
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
    const events = []; E().spend(member.state, "action");
    let openingFeature = C()?.openingFeature?.(round, member, setup) || null, lightTrigger = null, rangedSplitUsed = false;
    const rangedSplit = useRangedSplit(member, setup, slots), turnKey = `${round}:${member.combatant_id}`;

    slots.forEach((slot, index) => {
      if (member.state.is_dead || Q().incapacitated(member.state)) return;
      const data = slotData(slot), splitThis = index > 0 && rangedSplit && !rangedSplitUsed && F().flexibleSlotHasBoth(member, data.attackIds);
      const choice = attackChoice(member, setup, data, splitThis);
      if (choice) {
        if (splitThis && choice.attack.kind === "ranged") rangedSplitUsed = true;
        const pack = window.IRON_PIT_BROWSER_STATE.packTactics(member, setup);
        const featureId = openingFeature || (pack ? "pack-tactics" : definition.id);
        const event = A().resolveAttack(sequence++, round, member, choice.target, choice.attack, choice.distance, {
          spendAction: false, advantage: pack ? 1 : 0, setup, featureId, turnKey, allowReckless: true, ignoreCloseThreat: true,
        });
        consumeResource(member.state, choice.attack); events.push(event);
        const cleave = WM().resolveCleave(sequence, round, member, event, choice.attack, setup, turnKey);
        events.push(...cleave.events); sequence = cleave.sequence;
        if (definition.isAttackAction && !lightTrigger && choice.attack.light) lightTrigger = choice.attack;
        openingFeature = null; return;
      }
      const saved = saveChoice(member, setup, data);
      if (saved) events.push(V().resolveAction(sequence++, round, member, saved.target, saved.save, saved.distance, { spendAction: false }));
    });

    if (definition.isAttackAction && lightTrigger) {
      const extra = R().resolve(sequence, round, member, setup, lightTrigger, turnKey); events.push(...extra.events); sequence = extra.sequence;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();
