(() => {
  "use strict";

  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTIONS;

  function choose(member, setup, turnKey) {
    const attack = AP()?.choose(member, setup, turnKey) || null;
    const save = SP()?.choose(member, setup, turnKey) || null;
    if (!attack && !save) return null;
    const useAttack = !save || (attack && (attack.expectedDamage > save.expectedDamage
      || (attack.expectedDamage === save.expectedDamage && attack.action.level <= save.action.level)));
    return useAttack ? { kind: "attack", choice: attack } : { kind: "save", choice: save };
  }

  function resolveChoice(sequence, round, member, setup, turnKey, selected) {
    if (!selected) return { events: [], sequence };
    if (selected.kind === "attack") {
      const event = AR().resolve(sequence++, round, member, selected.choice.target, selected.choice.action, setup, turnKey);
      const reactions = DR().resolveAfterDamage(sequence, round, member, event, setup, turnKey);
      return { events: [event, ...reactions.events], sequence: reactions.sequence };
    }
    if (selected.kind === "save") return SR().resolve(sequence, round, member, setup, selected.choice, turnKey);
    throw new Error(`Unknown spell-offense choice kind: ${String(selected.kind)}.`);
  }

  function resolve(sequence, round, member, setup, turnKey) {
    return resolveChoice(sequence, round, member, setup, turnKey, choose(member, setup, turnKey));
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { choose, resolve, resolveChoice };
})();
