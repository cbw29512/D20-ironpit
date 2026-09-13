(() => {
  "use strict";
  function sources(attack, target, sourceId = null) {
    try {
      let total = 0;
      const effectiveMaxHp = target.template.max_hp + (target.max_hp_bonus || 0);
      for (const spec of attack.conditionalAttackAdvantage || []) {
        if (spec.trigger === "target_not_full_hp") { total += target.current_hp < effectiveMaxHp ? 1 : 0; continue; }
        if (spec.trigger === "target_grappled_by_source") {
          if (!sourceId) throw new Error("Source-owned grapple Advantage requires a source combatant id.");
          total += (target.grapple_sources || []).some((item) => item.source_id === sourceId) ? 1 : 0;
          continue;
        }
        throw new Error(`Unsupported conditional attack Advantage trigger: ${spec.trigger}`);
      }
      return total;
    } catch (error) { console.error("Conditional attack Advantage resolution failed.", error); throw error; }
  }
  window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE = { sources };
})();
