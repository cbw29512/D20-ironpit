(() => {
  "use strict";
  // Source parameters are printed on the immutable combatant template.
  // Fight state owns the slot spend, reaction spend and timed AC modifier.
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function active(state) {
    try {
      const defense = state.template.reaction_defense_spell;
      return !!(defense && (state.active_modifiers || []).some((item) =>
        item.kind === "armor-class" && item.source_effect_id === defense.id));
    } catch (error) {
      console.error("Reaction defense status failed", error);
      throw error;
    }
  }

  function trigger(state, sourceId, options = {}) {
    try {
      const defense = state.template.reaction_defense_spell;
      if (!defense || active(state) || !E().available(state, "reaction")) return false;
      if (options.autoHitSpellId) {
        if (!(defense.blockedAutoHitSpellIds || []).includes(options.autoHitSpellId)) return false;
      } else {
        const ac = M().effectiveArmorClass(state);
        if (!Number.isFinite(options.attackTotal) || [1, 20].includes(options.natural)
          || !(ac <= options.attackTotal && options.attackTotal < ac + defense.acBonus)) return false;
      }
      let resourceId = defense.resourceId || null;
      if (resourceId) {
        // Innate spell: daily uses are printed source parameters, not slots.
        if (!(state.resources?.[resourceId] > 0)) return false;
      } else if (Number.isInteger(defense.minimumSlotLevel)) {
        const slots = Object.keys(state.resources || {})
          .filter((id) => /^spell-slot-[1-9]$/.test(id))
          .map((id) => ({ id, level: Number(id.split("-")[2]) }))
          .filter((item) => item.level >= defense.minimumSlotLevel && state.resources[item.id] > 0)
          .sort((a, b) => a.level - b.level);
        if (!slots.length) return false;
        resourceId = slots[0].id;
      }
      // At-will innate casts have no finite resource; the Reaction still costs.
      E().spend(state, "reaction");
      if (resourceId) state.resources[resourceId] -= 1;
      M().add(state, {
        id: `${sourceId}:${defense.id}:reaction`, source_id: sourceId,
        source_effect_id: defense.id, source_name: defense.name,
        source_is_magical: true, kind: "armor-class", flat_bonus: defense.acBonus,
        expires_at_start_of_source_turn: true,
      });
      return true;
    } catch (error) {
      console.error("Reaction defense trigger failed", {name: state?.template?.name, error});
      throw error;
    }
  }

  function blocksAutoHit(state, sourceId, spellId) {
    try {
      const defense = state.template.reaction_defense_spell;
      if (!defense || !(defense.blockedAutoHitSpellIds || []).includes(spellId)) return false;
      return active(state) || trigger(state, sourceId, {autoHitSpellId: spellId});
    } catch (error) {
      console.error("Reaction defense auto-hit gate failed", {spellId, error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_REACTION_DEFENSE_SPELLS = {active, trigger, blocksAutoHit};
})();
