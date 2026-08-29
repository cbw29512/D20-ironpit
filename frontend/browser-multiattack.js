(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  const slotData = (slot) => Array.isArray(slot)
    ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function allowedAttack(member, ids, distance) {
    const allowed = new Set(ids);
    const profiles = member.state.template.attacks.filter((attack) => allowed.has(attack.id));
    const melee = profiles.find((attack) => attack.kind === "melee" && distance <= (attack.reach || 5));
    if (melee) return melee;
    return profiles.find((attack) => attack.kind === "ranged" && distance <= attack.long) || null;
  }

  function allowedSave(member, target, ids, distance) {
    const allowed = new Set(ids);
    return member.state.template.saving_throw_actions?.find(
      (action) => allowed.has(action.id) && V().legalAction(action, target, distance),
    ) || null;
  }

  function slotChoice(member, target, slot) {
    const data = slotData(slot), distance = S().distance(member, target);
    const attack = allowedAttack(member, data.attackIds, distance);
    return { attack, save: attack ? null : allowedSave(member, target, data.saveActionIds, distance), data };
  }

  function desiredDistance(member, data) {
    if (data.attackIds.length) {
      const profiles = member.state.template.attacks.filter((attack) => data.attackIds.includes(attack.id));
      const melee = profiles.filter((attack) => attack.kind === "melee").map((attack) => attack.reach || 5);
      if (melee.length) return Math.max(...melee);
      const ranged = profiles.map((attack) => attack.normal).filter(Number.isFinite);
      if (ranged.length) return Math.max(...ranged);
    }
    const saves = member.state.template.saving_throw_actions?.filter((action) => data.saveActionIds.includes(action.id)) || [];
    if (saves.length) return Math.max(...saves.map((action) => action.range));
    throw new Error(`Unknown Multiattack slot on ${member.state.template.name}.`);
  }

  function movementEvent(sequence, round, member, target, movement) {
    return {
      sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      distance_before_ft: movement.before, distance_after_ft: movement.after, movement_ft: movement.moved,
      animation: "advance", description: `${member.state.template.name} advances ${movement.moved} feet between Multiattack steps.`,
    };
  }

  function resolveAttackAction(sequence, round, member, setup) {
    const slots = member.state.template.attack_action?.slots;
    if (!slots?.length || !member.state.action_available) return { events: [], sequence };
    const events = [];
    member.state.action_available = false;
    for (const slot of slots) {
      const target = S().nearestTarget(member, setup);
      if (!target) break;
      let choice = slotChoice(member, target, slot);
      if (!choice.attack && !choice.save) {
        const movement = S().moveToward(member, target, desiredDistance(member, choice.data));
        if (movement) events.push(movementEvent(sequence++, round, member, target, movement));
        choice = slotChoice(member, target, slot);
      }
      if (choice.attack) {
        const pack = S().packTactics(member, setup);
        events.push(A().resolveAttack(sequence++, round, member, target, choice.attack, S().distance(member, target), {
          spendAction: false,
          advantage: pack ? 1 : 0,
          featureId: pack ? "pack-tactics" : member.state.template.attack_action.id,
        }));
      } else if (choice.save) {
        events.push(V().resolveAction(sequence++, round, member, target, choice.save, S().distance(member, target), {
          spendAction: false,
        }));
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();
