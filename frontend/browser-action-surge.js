(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function available(state, turnKey) {
    return (state.resources["action-surge"] || 0) > 0
      && !state.action_available
      && !state.is_dead
      && !Q().incapacitated(state)
      && state.feature_last_turn_keys["action-surge"] !== turnKey;
  }

  function use(sequence, round, member, turnKey) {
    if (!available(member.state, turnKey)) throw new Error("Action Surge is unavailable.");
    member.state.resources["action-surge"] -= 1;
    member.state.action_available = true;
    member.state.feature_last_turn_keys["action-surge"] = turnKey;
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, feature_id: "action-surge",
      resource_remaining: member.state.resources["action-surge"], animation: "action-surge",
      description: `${member.state.template.name} uses Action Surge and gains one additional Action.`,
    };
  }

  function legalAttack(member, distance) {
    const attacks = member.state.template.attacks || [];
    return attacks.find((attack) => attack.kind === "melee" && distance <= (attack.reach || 5))
      || attacks.find((attack) => attack.kind === "ranged" && distance <= attack.long)
      || null;
  }

  function resolveAttack(sequence, round, member, setup, turnKey) {
    if (!available(member.state, turnKey)) return null;
    const target = S().nearestTarget(member, setup);
    if (!target) return null;
    const distance = S().distance(member, target), attack = legalAttack(member, distance);
    if (!attack) return null;
    const events = [use(sequence++, round, member, turnKey)];
    if (member.state.template.attack_action) {
      const multi = M().resolveAttackAction(sequence, round, member, setup);
      events.push(...multi.events);
      return { events, sequence: multi.sequence };
    }
    const pack = S().packTactics(member, setup);
    const standard = U().resolve(sequence, round, member, target, attack, distance, setup, turnKey, {
      advantage: pack ? 1 : 0, featureId: "action-surge",
    });
    events.push(...standard.events);
    return { events, sequence: standard.sequence };
  }

  window.IRON_PIT_BROWSER_ACTION_SURGE = { available, resolveAttack, use };
})();
