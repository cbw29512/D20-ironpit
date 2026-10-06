(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const AWB = () => window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const DE = () => window.IRON_PIT_BROWSER_DEFERRED_ATTACK_SLOT;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const MK = () => window.IRON_PIT_BROWSER_MONK_2014;
  const R = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const WM = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || { resolveCleave: (sequence) => ({ events: [], sequence }) };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function saveChoice(member, setup, data) {
    const allowed = new Set(data.saveActionIds);
    for (const target of F().targetOrder(member, setup)) {
      const action = (member.state.template.saving_throw_actions || []).find((item) => {
        const distance = F().saveDistance(member, target, item.range);
        return allowed.has(item.id) && V().legalAction(item, target, distance, member.combatant_id);
      });
      if (action) return { target, save: action, distance: F().saveDistance(member, target, action.range) };
    }
    return null;
  }
  function attackChoice(member, setup, data) {
    if (F().flexibleSlotHasBoth(member, data.attackIds)) {
      const preferred = F().isBackline(member)
        ? (F().alliedFrontlineActive(member, setup) ? "ranged" : "melee")
        : "melee";
      return F().chooseAttack(member, setup, data.attackIds, preferred);
    }
    return F().chooseAttack(member, setup, data.attackIds, "melee")
      || F().chooseAttack(member, setup, data.attackIds, "ranged");
  }
  function slotHasLegalChoice(member, setup, slot) {
    try {
      const data = slotData(slot);
      return Boolean(attackChoice(member, setup, data) || saveChoice(member, setup, data));
    } catch (error) {
      console.error("Failed to prove browser Attack/Multiattack slot legality", { member: member.combatant_id, error });
      throw error;
    }
  }
  function eventTarget(event, fallback, setup) {
    return [...setup.heroes, ...setup.monsters].find((item) => item.combatant_id === event.target_id) || fallback;
  }

  function legalChoiceAvailable(member, setup) {
    const definition = member.state.template.attack_action, slots = definition?.slots;
    return Boolean(slots?.length
      && F().targetOrder(member, setup).length
      && slots.some((slot) => slotHasLegalChoice(member, setup, slot)));
  }

  function available(member, setup) {
    return Boolean(E().available(member.state, "action") && legalChoiceAvailable(member, setup));
  }
  function meleeAvailable(member, setup) {
    return (member.state.template.attack_action?.slots || []).some((slot) =>
      Boolean(F().chooseAttack(member, setup, slotData(slot).attackIds, "melee")));
  }
  function printedSave(action) {
    return (action.damageDiceCount || 0) * ((action.damageDiceSize || 6) + 1) / 2 + (action.damageBonus || 0);
  }
  function expectedDamage(member, setup) {
    try {
      let total = 0;
      for (const slot of member.state.template.attack_action?.slots || []) {
        const data = slotData(slot);
        const chosen = F().chooseAttack(member, setup, data.attackIds, "melee")
          || F().chooseAttack(member, setup, data.attackIds, "ranged");
        if (chosen) {
          total += F().weaponMeanDamage(chosen.attack);
          continue;
        }
        const saved = saveChoice(member, setup, data);
        if (saved) total += printedSave(saved.save);
      }
      return total;
    } catch (error) {
      console.error("Failed to score browser Attack/Multiattack expected damage", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function resolveAttackAction(sequence, round, member, setup) {
    const definition = member.state.template.attack_action, slots = definition?.slots;
    if (!available(member, setup)) return { events: [], sequence };
    const events = [];
    E().spend(member.state, "action");
    const attackBuff = AWB()?.resolve(sequence, round, member) || null;
    if (attackBuff) { events.push(attackBuff); sequence += 1; }
    let openingFeature = C()?.openingFeature?.(round, member, setup) || null;
    let lightTrigger = null;
    const turnKey = `${round}:${member.combatant_id}`;

    for (let index = 0; index < slots.length; index += 1) {
      if (member.state.is_dead || member.state.is_unconscious || member.state.turn_terminated) break;
      const data = slotData(slots[index]);
      const deferred = DE()?.resolve(sequence, round, member, setup) || null;
      if (deferred) {
        events.push(deferred); sequence += 1; openingFeature = null;
        continue;
      }
      const choice = attackChoice(member, setup, data);
      if (choice) {
        if (window.IRON_PIT_BROWSER_TIMED_CONTROL?.turnAttackAllowed(member.state) === false) break;
        const pack = window.IRON_PIT_BROWSER_STATE.packTactics(member, choice.target, setup);
        const featureId = openingFeature || (pack ? "pack-tactics" : definition.id);
        const event = A().resolveAttack(sequence, round, member, choice.target, choice.attack, choice.distance, {
          spendAction: false, advantage: pack ? 1 : 0, setup, featureId, turnKey,
          allowReckless: true, ignoreCloseThreat: true,
        });
        sequence += 1;
        if (event.event_type === "saving_throw" && !event.attack_roll) {
          const chain = DMR()?.chain(sequence, round, member, event, setup, turnKey) || { events: [event], sequence };
          events.push(...chain.events); sequence = chain.sequence; openingFeature = null;
          if (member.state.is_dead || Q()?.incapacitated?.(member.state)) break;
          continue;
        }
        events.push(event);
        if (event.hit) {
          const actualTarget = eventTarget(event, choice.target, setup);
          if (MK()?.resolveStunning) {
            const stun = MK().resolveStunning(sequence, round, member, actualTarget, choice.attack);
            if (stun) { events.push(stun); sequence += 1; }
          }
        }
        const chain = DMR()?.chain(sequence, round, member, event, setup, turnKey) || { events: [event], sequence };
        events.push(...chain.events.slice(1)); sequence = chain.sequence;
        if (member.state.turn_terminated || member.state.is_dead || Q()?.incapacitated?.(member.state)) break;
        const cleave = WM().resolveCleave(sequence, round, member, event, choice.attack, setup, turnKey);
        events.push(...cleave.events); sequence = cleave.sequence;
        if (member.state.is_dead || Q()?.incapacitated?.(member.state)) break;
        if (definition.isAttackAction && !lightTrigger && choice.attack.light) lightTrigger = choice.attack;
        openingFeature = null;
        continue;
      }
      const saved = saveChoice(member, setup, data);
      if (saved) {
        const event = V().resolveAction(sequence, round, member, saved.target, saved.save, saved.distance, {
          spendAction: false, setup,
        });
        sequence += 1;
        const chain = DMR()?.chain(sequence, round, member, event, setup, turnKey) || { events: [event], sequence };
        events.push(...chain.events); sequence = chain.sequence;
        if (member.state.is_dead || Q()?.incapacitated?.(member.state)) break;
      }
    }

    if (definition.isAttackAction && lightTrigger && !member.state.turn_terminated
      && !member.state.is_dead && !Q()?.incapacitated?.(member.state)) {
      const extra = R().resolve(sequence, round, member, setup, lightTrigger, turnKey);
      events.push(...extra.events); sequence = extra.sequence;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = {
    available, legalChoiceAvailable, meleeAvailable, expectedDamage, resolveAttackAction,
  };
})();