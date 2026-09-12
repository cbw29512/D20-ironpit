(() => {
  "use strict";

  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const XP = () => window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL_POLICY;
  const XR = () => window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL;

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
    const selected = choices[0];
    if (selected.kind === "attack") {
      const c = selected.choice;
      const event = AR().resolve(sequence++, round, member, c.target, c.action, setup, turnKey);
      return { events: [event], sequence };
    }
    if (selected.kind === "automatic") {
      const c = selected.choice;
      const event = XR().resolve(sequence++, round, member, c.target, c.action, setup, turnKey);
      return { events: [event], sequence };
    }
    return SR().resolve(sequence, round, member, setup, selected.choice, turnKey);
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { resolve };
})();
