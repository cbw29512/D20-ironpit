(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const L = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || { resolveCleave: (sequence) => ({ events: [], sequence }) };

  function resolve(sequence, round, member, target, attack, distance, setup, turnKey, options = {}) {
    if (!V().resourceAvailable(member.state, attack)) throw new Error(`${attack.name} has no remaining resource use.`);
    const event = A().resolveAttack(sequence++, round, member, target, attack, distance, {
      advantage: options.advantage || 0, featureId: options.featureId || null, setup,
      allowReckless: options.allowReckless !== false, turnKey,
    });
    V().consumeResource(member.state, attack);
    const events = [event];
    const cleave = W().resolveCleave(sequence, round, member, event, attack, setup, turnKey);
    events.push(...cleave.events); sequence = cleave.sequence;
    if (member.state.template.kind !== "character" || !attack.light) return { events, sequence };
    const extra = L().resolve(sequence, round, member, setup, attack, turnKey);
    events.push(...extra.events);
    return { events, sequence: extra.sequence };
  }

  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { resolve };
})();
