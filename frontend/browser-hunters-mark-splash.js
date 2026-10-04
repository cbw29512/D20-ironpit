(() => {
  "use strict";

  const MARK_SOURCES = new Set(["hunter's mark", "hunters-mark"]);
  const SPLASH_KEY = "superior-hunters-prey";

  function members(setup) {
    return [...(setup?.heroes || []), ...(setup?.monsters || [])];
  }

  function markComponent(components) {
    return (components || []).find((item) =>
      MARK_SOURCES.has(String(item.source || "").toLowerCase()) && (item.applied_total || item.total) > 0,
    ) || null;
  }

  function resolve(attacker, attackerId, primaryId, components, turnKey, setup) {
    try {
      const rangeFt = attacker.template?.hunters_mark_splash_range_ft
        || attacker.template?.progression_features?.hunters_mark_splash_range_ft
        || 0;
      if (rangeFt <= 0 || !setup || !turnKey) return null;
      attacker.feature_last_turn_keys ||= {};
      if (attacker.feature_last_turn_keys[SPLASH_KEY] === turnKey) return null;
      const mark = markComponent(components);
      if (!mark) return null;
      const source = members(setup).find((item) => item.state === attacker)
        || members(setup).find((item) => item.combatant_id === attackerId);
      const primary = members(setup).find((item) => item.combatant_id === primaryId);
      const distance = window.IRON_PIT_BROWSER_STATE?.distance;
      if (!source || !primary || !distance) return null;
      const splashTarget = members(setup).find((item) =>
        item.combatant_id !== source.combatant_id
        && item.combatant_id !== primaryId
        && item.side !== source.side
        && item.state.current_hp > 0
        && !item.state.is_dead
        && distance(source, item) <= rangeFt,
      );
      if (!splashTarget) return null;
      attacker.feature_last_turn_keys[SPLASH_KEY] = turnKey;
      const applied = window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(
        splashTarget.state, mark.applied_total || mark.total, mark.damage_type,
      );
      window.IRON_PIT_BROWSER_ATTACK.applyDamage(
        splashTarget.state, applied, false, [mark.damage_type],
        members(setup).map((item) => item.state), setup,
      );
      return { targetId: splashTarget.combatant_id, applied };
    } catch (error) {
      console.error("Hunter's Mark splash failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_HUNTERS_MARK_SPLASH = { resolve };
})();
