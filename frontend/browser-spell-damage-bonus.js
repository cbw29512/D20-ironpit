(() => {
  "use strict";

  function matches(state, spellId, damageType, excludedSourceIds = []) {
    try {
      const excluded = new Set(excludedSourceIds || []);
      const scores = state?.template?.ability_scores;
      const grants = state?.template?.spell_damage_bonus_grants || [];
      if (grants.length && !scores) throw new Error("Spell damage bonus requires character ability scores.");
      const sources = [];
      let total = 0;
      for (const grant of grants) {
        if (excluded.has(grant.source_id)) continue;
        const spellMatch = (grant.eligible_spell_ids || []).includes(spellId);
        const typeMatch = damageType != null && (grant.eligible_damage_types || []).includes(damageType);
        if (!spellMatch && !typeMatch) continue;
        const score = scores?.[grant.ability];
        if (!Number.isInteger(score)) throw new Error(`Missing ability score for ${grant.source_name}.`);
        const amount = Math.floor((score - 10) / 2);
        total += amount;
        sources.push({ sourceId: grant.source_id, sourceName: grant.source_name, amount });
      }
      return { total, sources };
    } catch (error) {
      console.error("Failed browser spell damage bonus lookup.", {
        combatant: state?.template?.name, spellId, damageType, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_DAMAGE_BONUS = { matches };
})();
