(() => {
  "use strict";

  function choose(member, setup, spell) {
    try {
      const allowed = spell.selectableResistanceTypes || [];
      if (!allowed.length) return null;
      const scores = window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE?.scores
        ? (() => {
          const original = member.state.template.selectable_damage_resistance;
          member.state.template.selectable_damage_resistance = { allowed_damage_types: allowed };
          try {
            return window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE.scores(member, setup);
          } finally {
            if (original) member.state.template.selectable_damage_resistance = original;
            else delete member.state.template.selectable_damage_resistance;
          }
        })()
        : Object.fromEntries(allowed.map((type) => [type, 0]));
      return allowed.reduce((best, type, index) => {
        if (best == null) return type;
        const current = scores[type] || 0;
        const prior = scores[best] || 0;
        if (current !== prior) return current > prior ? type : best;
        return index < allowed.indexOf(best) ? type : best;
      }, null);
    } catch (error) {
      console.error("Failed to choose selectable spell resistance.", { spell: spell?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SELECTABLE_SPELL_RESISTANCE = { choose };
})();
