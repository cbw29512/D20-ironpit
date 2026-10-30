(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_HEALING;

  function resolve(target, amount, type, adjusted) {
    try {
      if (amount < 0) throw new Error("Damage cannot be negative.");
      if (!(target.template.damage_absorption_types || []).includes(type)) {
        return { applied: adjusted, healed: 0 };
      }
      const healing = H();
      if (!healing?.restore) {
        throw new Error("Browser healing runtime is required for damage absorption.");
      }
      return { applied: 0, healed: healing.restore(target, amount) };
    } catch (error) {
      console.error("Browser damage absorption failed.", {
        name: target?.template?.name, type, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_ABSORPTION = { resolve };
})();
