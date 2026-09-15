(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DT = () => window.IRON_PIT_BROWSER_DEATH_TRIGGERS || { resolvePending: (sequence) => ({ events: [], sequence }) };
  const L = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || {
    resolveCleave: (sequence) => ({ events: [], sequence }),
  };

  function flushDeathTriggers(events, sequence, round, setup) {
    const result = DT().resolvePending(sequence, round, setup);
    events.push(...result.events);
    return result.sequence;
  }

  function resolve(sequence, round, member, target, attack, distance, setup, turnKey, options = {}) {
    const event = A().resolveAttack(sequence++, round, member, target, attack, distance, {
      advantage: options.advantage || 0,
      featureId: options.featureId || null,
      setup,
      allowReckless: options.allowReckless !== false,
      turnKey,
    });
    const events = [event];
    sequence = flushDeathTriggers(events, sequence, round, setup);
    if (member.state.is_dead || member.state.turn_terminated) return { events, sequence };
    const cleave = W().resolveCleave(sequence, round, member, event, attack, setup, turnKey);
    events.push(...cleave.events); sequence = cleave.sequence;
    sequence = flushDeathTriggers(events, sequence, round, setup);
    if (member.state.template.kind !== "character" || !attack.light || member.state.is_dead || member.state.turn_terminated) return { events, sequence };
    const extra = L().resolve(sequence, round, member, setup, attack, turnKey);
    events.push(...extra.events); sequence = extra.sequence;
    sequence = flushDeathTriggers(events, sequence, round, setup);
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { resolve };
})();