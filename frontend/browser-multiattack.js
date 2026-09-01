(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };
  const W = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT || {
    moveToward: (q, r, m, t, _s, d) => ({ events: [], sequence: q, movement: S().moveToward(m, t, d) }),
  };
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function targetAllowed(member, target, attack) {
    if (!attack.forbidSelfGrappledTarget) return true;
    return !target.state.grapple_sources.some((source) => source.source_id === member.combatant_id);
  }
  function allowedAttack(member, target, ids, distance) {
    const allowed = new Set(ids), profiles = member.state.template.attacks.filter((a) => allowed.has(a.id) && targetAllowed(member, target, a));
    return profiles.find((a) => a.kind === "melee" && distance <= (a.reach || 5))
      || profiles.find((a) => a.kind === "ranged" && distance <= a.long) || null;
  }
  function slotChoice(member, target, slot) {
    const data = slotData(slot), distance = S().distance(member, target), attack = allowedAttack(member, target, data.attackIds, distance);
    const allowed = new Set(data.saveActionIds);
    const save = attack ? null : member.state.template.saving_throw_actions?.find((a) => allowed.has(a.id) && V().legalAction(a, target, distance)) || null;
    return { attack, save, data };
  }
  function staticSlotAllows(member, target, data) {
    const attacks = member.state.template.attacks.filter((a) => data.attackIds.includes(a.id) && targetAllowed(member, target, a));
    if (attacks.length) return true;
    return (member.state.template.saving_throw_actions || []).some((action) =>
      data.saveActionIds.includes(action.id) && (!action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize)),
    );
  }
  function slotTarget(member, setup, slot) {
    const data = slotData(slot), preferred = S().nearestTarget(member, setup);
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    let eligible = enemies.filter((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0);
    if (!eligible.length) eligible = enemies.filter((target) => target.state.template.kind === "character"
      && target.state.is_alive && !target.state.is_dead && target.state.current_hp === 0);
    eligible.sort((a, b) => S().distance(member, a) - S().distance(member, b));
    const ordered = preferred ? [preferred, ...eligible.filter((target) => target !== preferred)] : eligible;
    return ordered.find((target) => staticSlotAllows(member, target, data)) || null;
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
    let openingFeature = C()?.openingFeature?.(round, member, setup) || null;
    const turnKey = `${round}:${member.combatant_id}`;
    for (const slot of slots) {
      if (member.state.is_dead || member.state.is_unconscious) break;
      const target = slotTarget(member, setup, slot); if (!target) continue;
      let choice = slotChoice(member, target, slot);
      if (!choice.attack && !choice.save) {
        const moved = W().moveToward(sequence, round, member, target, setup, desiredDistance(member, choice.data));
        events.push(...moved.events); sequence = moved.sequence;
        if (moved.movement) events.push(movementEvent(sequence++, round, member, target, moved.movement));
        if (member.state.is_dead || member.state.is_unconscious) break;
        choice = slotChoice(member, target, slot);
      }
      if (choice.attack) {
        const pack = S().packTactics(member, setup), featureId = openingFeature || (pack ? "pack-tactics" : member.state.template.attack_action.id);
        events.push(A().resolveAttack(sequence++, round, member, target, choice.attack, S().distance(member, target), {
          spendAction: false, advantage: pack ? 1 : 0, setup, featureId, turnKey, allowReckless: true,
        }));
        openingFeature = null;
      } else if (choice.save) {
        events.push(V().resolveAction(sequence++, round, member, target, choice.save, S().distance(member, target), { spendAction: false }));
      }
    }
    return { events, sequence };
  }
  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction, slotTarget, targetAllowed };
})();
