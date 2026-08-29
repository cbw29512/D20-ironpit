(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function allowedAttack(member, ids, distance) {
    const allowed = new Set(ids);
    const profiles = member.state.template.attacks.filter((attack) => allowed.has(attack.id));
    const melee = profiles.find((attack) => attack.kind === "melee" && distance <= (attack.reach || 5));
    if (melee) return melee;
    return profiles.find((attack) => attack.kind === "ranged" && distance <= attack.long) || null;
  }

  function movementEvent(sequence, round, member, target, movement) {
    return {
      sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      distance_before_ft: movement.before, distance_after_ft: movement.after, movement_ft: movement.moved,
      animation: "advance", description: `${member.state.template.name} advances ${movement.moved} feet between attacks.`,
    };
  }

  function resolveAttackAction(sequence, round, member, setup) {
    const slots = member.state.template.attack_action?.slots;
    if (!slots?.length || !member.state.action_available) return { events: [], sequence };
    const events = [];
    member.state.action_available = false;
    for (const ids of slots) {
      const target = S().nearestTarget(member, setup);
      if (!target) break;
      let attack = allowedAttack(member, ids, S().distance(member, target));
      if (!attack) {
        const profile = member.state.template.attacks.find((item) => ids.includes(item.id));
        if (!profile) throw new Error(`Unknown attack slot on ${member.state.template.name}.`);
        const desired = profile.kind === "melee" ? (profile.reach || 5) : profile.normal;
        const movement = S().moveToward(member, target, desired);
        if (movement) events.push(movementEvent(sequence++, round, member, target, movement));
        attack = allowedAttack(member, ids, S().distance(member, target));
      }
      if (!attack) continue;
      const pack = S().packTactics(member, setup);
      events.push(A().resolveAttack(sequence++, round, member, target, attack, S().distance(member, target), {
        spendAction: false,
        advantage: pack ? 1 : 0,
        featureId: pack ? "pack-tactics" : member.state.template.attack_action.id,
      }));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTIATTACK = { resolveAttackAction };
})();
