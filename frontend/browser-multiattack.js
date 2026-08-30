(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const W = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT || {
    moveToward: (q, r, m, t, _s, d) => ({ events: [], sequence: q, movement: S().moveToward(m, t, d) }),
  };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function allowedAttack(member, ids, distance) {
    const allowed = new Set(ids), profiles = member.state.template.attacks.filter((a) => allowed.has(a.id));
    return profiles.find((a) => a.kind === "melee" && distance <= (a.reach || 5))
      || profiles.find((a) => a.kind === "ranged" && distance <= a.long) || null;
  }
  function slotChoice(member, target, slot) {
    const data = slotData(slot), distance = S().distance(member, target), attack = allowedAttack(member, data.attackIds, distance);
    const allowed = new Set(data.saveActionIds);
    const save = attack ? null : member.state.template.saving_throw_actions?.find((a) => allowed.has(a.id) && V().legalAction(a, target, distance)) || null;
    return { attack, save, data };
  }
  function desiredDistance(member, data) {
    if (data.attackIds.length) {
      const profiles = member.state.template.attacks.filter((a) => data.attackIds.includes(a.id));
      const melee = profiles.filter((a) => a.kind === "melee").map((a) => a.reach || 5);
      if (melee.length) return Math.max(...melee);
      const ranged = profiles.map((a) => a.normal).filter(Number.isFinite); if (ranged.length) return Math.max(...ranged);
    }
    const saves = member.state.template.saving_throw_actions?.filter((a) => data.saveActionIds.includes(a.id)) || [];
    if (saves.length) return Math.max(...saves.map((a) => a.range));
    throw new Error(`Unknown Multiattack slot on ${member.state.template.name}.`);
  }
  function movementEvent(sequence, round, member, target, movement) {
    return { sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      distance_before_ft: movement.before, distance_after_ft: movement.after, movement_ft: movement.moved,
      animation: "advance", description: `${member.state.template.name} advances ${movement.moved} feet between Multiattack steps.` };
  }
  function resolveAttackAction(sequence, round, member, setup) {
    const slots = member.state.template.attack_action?.slots;
    if (!slots?.length || !E().available(member.state, "action")) return { events: [], sequence };
    const events = []; E().spend(member.state, "action");
    for (const slot of slots) {
      if (member.state.is_dead || member.state.is_unconscious) break;
      const target = S().nearestTarget(member, setup); if (!target) break;
      let choice = slotChoice(member, target, slot);
      if (!choice.attack && !choice.save) {
        const moved = W().moveToward(sequence, round, member, target, setup, desiredDistance(member, choice.data));
        events.push(...moved.events); sequence = moved.sequence;
        if (moved.movement) events.push(movementEvent(sequence++, round, member, target, moved.movement));
        if (member.state.is_dead || member.state.is_unconscious) break;
        choice = slotChoice(member, target, slot);
      }
      if (choice.attack) {
        const pack = S().packTactics(member, setup);
        events.push(A().resolveAttack(sequence++, round, member, target, choice.attack, S().distance(member, target), {
          spendAction: false, advantage: pack ? 1 : 0, setup,
          featureId: pack ? "pack-tactics" : member.state.template.attack_action.id,
        }));
      } else if (choice.save) {
        events.push(V().resolveAction(sequence++, round, member, target, choice.save, S().distance(member, target), { spendAction: false }));
      }
    }
    return { events, sequence };
  }
  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();
