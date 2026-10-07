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
  const MC = window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES;
  if (!MC) throw new Error("Multiattack requires browser-multiattack-choices.js.");

  function eventTarget(event, fallback, setup) {
    return [...setup.heroes, ...setup.monsters].find((item) => item.combatant_id === event.target_id) || fallback;
  }

  function resolveAttackAction(sequence, round, member, setup) {
    try {
      const definition = member.state.template.attack_action;
      if (!E().available(member.state, "action")) return { events: [], sequence };
      const selected = MC.selectSequence(member, setup);
      if (!selected) return { events: [], sequence };
      const { slots, mode, variant } = selected;
      const events = [];
      E().spend(member.state, "action");
      const attackBuff = AWB()?.resolve(sequence, round, member) || null;
      if (attackBuff) { events.push(attackBuff); sequence += 1; }
      let openingFeature = C()?.openingFeature?.(round, member, setup) || null;
      let lightTrigger = null, previousAttack = null;
      const turnKey = `${round}:${member.combatant_id}`;

      for (let index = 0; index < slots.length; index += 1) {
        if (member.state.is_dead || member.state.is_unconscious || member.state.turn_terminated) break;
        const data = MC.slotData(slots[index]);
        const followup = MC.followupTarget(data, previousAttack?.event_type === "attack" ? previousAttack.hit : null, previousAttack?.target_id);
        previousAttack = null;
        if (!followup.eligible) continue;
        const deferred = DE()?.resolve(sequence, round, member, setup) || null;
        if (deferred) {
          events.push(deferred); sequence += 1; openingFeature = null;
          continue;
        }
        const choice = F().chooseSlotAttack(member, setup, data.attackIds, mode, followup.targetId);
        if (choice) {
          if (window.IRON_PIT_BROWSER_TIMED_CONTROL?.turnAttackAllowed(member.state) === false) break;
          const pack = window.IRON_PIT_BROWSER_STATE.packTactics(member, choice.target, setup);
          const featureId = openingFeature || (pack ? "pack-tactics" : variant.id);
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
          events.push(event); previousAttack = event;
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
        const saved = MC.saveChoice(member, setup, data);
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
    } catch (error) {
      console.error("Browser Multiattack resolution failed", { id: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = {
    available: MC.available, legalChoiceAvailable: MC.legalChoiceAvailable,
    meleeAvailable: MC.meleeAvailable, expectedDamage: MC.expectedDamage, resolveAttackAction,
  };
})();
