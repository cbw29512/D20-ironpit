(() => {
  "use strict";

  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;

  function resolve(sequence, round, member, setup, turnKey) {
    const attack = AP()?.choose(member, setup, turnKey) || null;
    const save = SP()?.choose(member, setup, turnKey) || null;
    if (!attack && !save) return { events: [], sequence };
    const useAttack = !save || (attack && (attack.expectedDamage > save.expectedDamage
      || (attack.expectedDamage === save.expectedDamage && attack.action.level <= save.action.level)));
    if (useAttack) {
      const event = AR().resolve(sequence++, round, member, attack.target, attack.action, setup, turnKey);
      return { events: [event], sequence };
    }
    return SR().resolve(sequence, round, member, setup, save, turnKey);
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { resolve };
})();
