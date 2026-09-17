(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const has = (state, id) => Boolean(state?.active_effect_ids?.includes(id));

  function canUncannyDodge(attacker, defender) {
    return Boolean(
      defender?.template?.uncanny_dodge
      && !has(defender, "blinded")
      && !has(attacker, "invisible")
      && E().available(defender, "reaction")
    );
  }

  function applyUncannyDodge(attacker, defender, components) {
    if (!components?.length || !canUncannyDodge(attacker, defender)) {
      return { components, used: false };
    }
    E().spend(defender, "reaction");
    return {
      components: components.map((item) => ({ ...item, total: Math.floor(item.total / 2) })),
      used: true,
    };
  }

  function evasionDamage(state, ability, succeeded, successDamage, total) {
    const enabled = Boolean(state?.template?.evasion);
    if (!enabled || ability !== "dexterity" || successDamage !== "half") {
      return succeeded && successDamage === "half" ? Math.floor(total / 2) : total;
    }
    return succeeded ? 0 : Math.floor(total / 2);
  }

  window.IRON_PIT_BROWSER_ROGUE_DEFENSES = {
    applyUncannyDodge, canUncannyDodge, evasionDamage,
  };
})();
