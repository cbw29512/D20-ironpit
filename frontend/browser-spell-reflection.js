(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function target(reflector, caster, setup) {
    const profile = reflector.state.template.spell_reflection_reaction;
    if (!profile || !E().available(reflector.state, "reaction")) return null;
    const legal = [...setup.heroes, ...setup.monsters].filter((member) =>
      member !== reflector && member.state.is_alive && !member.state.is_dead
      && S().distance(reflector, member) <= profile.range_ft);
    if (legal.includes(caster)) return caster;
    legal.sort((a, b) => S().distance(reflector, a) - S().distance(reflector, b)
      || a.combatant_id.localeCompare(b.combatant_id));
    return legal[0] || null;
  }

  function spend(reflector) {
    if (!E().available(reflector.state, "reaction")) throw new Error("Spell Reflection reaction is unavailable.");
    E().spend(reflector.state, "reaction");
  }

  window.IRON_PIT_BROWSER_SPELL_REFLECTION = { target, spend };
})();
