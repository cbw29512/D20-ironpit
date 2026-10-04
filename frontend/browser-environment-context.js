(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function activeTags(member, setup) {
    try {
      if (!member || !setup) return new Set();
      const tags = new Set();
      for (const source of members(setup)) {
        const activeIds = new Set((source.state.timed_effects || [])
          .filter((effect) => effect.source_id === source.combatant_id && effect.source_effect_id)
          .map((effect) => effect.source_effect_id));
        for (const action of source.state.template.timed_self_buff_actions || []) {
          const aura = action.environmentContextAura;
          if (!aura || !activeIds.has(action.id)) continue;
          if (S().distance(source, member) <= aura.radius_ft) {
            for (const tag of aura.context_tags || []) tags.add(String(tag).toLowerCase());
          }
        }
      }
      return tags;
    } catch (error) {
      console.error("Browser environment context resolution failed.", {
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function disadvantage(member, setup, kind) {
    try {
      if (!member || !setup) return 0;
      const active = activeTags(member, setup);
      let total = 0;
      for (const reaction of member.state.template.environmentContextReactions || []) {
        if (!active.has(String(reaction.contextTag || "").toLowerCase())) continue;
        if (kind === "attack_roll" && reaction.attackRollDisadvantage) total += 1;
        if (kind === "ability_check" && reaction.abilityCheckDisadvantage) total += 1;
      }
      return total;
    } catch (error) {
      console.error("Browser environment context reaction failed.", {
        combatant: member?.combatant_id, kind, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXT = { activeTags, disadvantage };
})();