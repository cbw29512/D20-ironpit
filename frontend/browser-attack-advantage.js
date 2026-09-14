(() => {
  "use strict";
  const round1Lead = (attacker, target, round) => round === 1
    && Number.isFinite(attacker?.initiative_total) && Number.isFinite(target?.initiative_total)
    && attacker.initiative_total > target.initiative_total;
  const hasAssassinate = (state) => state?.template?.traits?.includes("assassinate");
  const assassinateCritical = (attacker, target) => Boolean(hasAssassinate(attacker) && target?.active_effect_ids?.includes("surprised"));
  function sources(attack, target, attackerId = null, attacker = null, round = null) {
    try {
      let total = hasAssassinate(attacker) && round1Lead(attacker, target, round) ? 1 : 0;
      const effectiveMaxHp = Math.max(0, target.template.max_hp + (target.max_hp_bonus || 0) - (target.max_hp_reduction || 0));
      for (const spec of attack.conditionalAttackAdvantage || []) {
        if (spec.trigger === "target_not_full_hp") { total += target.current_hp < effectiveMaxHp ? 1 : 0; continue; }
        if (spec.trigger === "target_grappled_by_self") {
          total += (target.grapple_sources || []).some((source) => source.source_id === attackerId) ? 1 : 0;
          continue;
        }
        if (spec.trigger === "round1_initiative_lead") {
          if (!attacker) throw new Error("Opening initiative Advantage requires attacker state.");
          total += round1Lead(attacker, target, round) ? 1 : 0;
          continue;
        }
        throw new Error(`Unsupported conditional attack Advantage trigger: ${spec.trigger}`);
      }
      return total;
    } catch (error) { console.error("Conditional attack Advantage resolution failed.", error); throw error; }
  }
  window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE = { assassinateCritical, round1Lead, sources };
})();