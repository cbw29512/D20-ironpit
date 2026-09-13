(() => {
  "use strict";

  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const DT = () => window.IRON_PIT_BROWSER_DEATH_TRIGGERS || { resolvePending: (sequence) => ({ events: [], sequence }) };
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const XP = () => window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL_POLICY;
  const XR = () => window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL;

  function flush(events, sequence, round, setup) {
    const result = DT().resolvePending(sequence, round, setup); events.push(...result.events); return result.sequence;
  }

  function resolve(sequence, round, member, setup, turnKey) {
    const attack = AP()?.choose(member, setup, turnKey) || null;
    const save = SP()?.choose(member, setup, turnKey) || null;
    const automatic = XP()?.choose(member, setup, turnKey) || null;
    const choices = [];
    if (attack) choices.push({ kind: "attack", expected: attack.expectedDamage, level: attack.action.level, choice: attack });
    if (save) choices.push({ kind: "save", expected: save.expectedDamage, level: save.slotLevel ?? save.action.level, choice: save });
    if (automatic) choices.push({ kind: "automatic", expected: automatic.expectedDamage, level: automatic.slotLevel, choice: automatic });
    if (!choices.length) return { events: [], sequence };
    choices.sort((a, b) => b.expected - a.expected || a.level - b.level || a.kind.localeCompare(b.kind));
    const selected = choices[0], events = [];
    if (selected.kind === "attack") {
      const c = selected.choice;
      events.push(AR().resolve(sequence++, round, member, c.target, c.action, setup, turnKey));
      return { events, sequence: flush(events, sequence, round, setup) };
    }
    if (selected.kind === "automatic") {
      const c = selected.choice;
      events.push(XR().resolve(sequence++, round, member, c.target, c.action, setup, turnKey));
      return { events, sequence: flush(events, sequence, round, setup) };
    }
    const resolved = SR().resolve(sequence, round, member, setup, selected.choice, turnKey);
    resolved.sequence = flush(resolved.events, resolved.sequence, round, setup);
    return resolved;
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { resolve };
})();
