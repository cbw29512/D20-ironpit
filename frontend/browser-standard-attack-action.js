(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTIONS;
  const L = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || {
    resolveCleave: (sequence) => ({ events: [], sequence }),
  };

  function resolve(sequence, round, member, target, attack, distance, setup, turnKey, options = {}) {
    const chain = DR().resolveAttackChain(sequence, round, member, target, attack, distance, setup, {
      advantage: options.advantage || 0,
      featureId: options.featureId || null,
      allowReckless: options.allowReckless !== false,
      turnKey,
    });
    const events = [...chain.events], event = events[0];
    sequence = chain.sequence;
    if (event.event_type === "saving_throw" && !event.attack_roll) return { events, sequence };
    if (member.state.turn_terminated || member.state.is_dead || member.state.is_unconscious) return { events, sequence };
    const cleave = W().resolveCleave(sequence, round, member, event, attack, setup, turnKey);
    events.push(...cleave.events); sequence = cleave.sequence;
    if (member.state.template.kind !== "character" || !attack.light || member.state.turn_terminated) return { events, sequence };
    const extra = L().resolve(sequence, round, member, setup, attack, turnKey);
    events.push(...extra.events);
    return { events, sequence: extra.sequence };
  }

  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { resolve };
})();