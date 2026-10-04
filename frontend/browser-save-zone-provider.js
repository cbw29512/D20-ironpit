(() => {
  "use strict";

  function coverage(center, enemies, radiusFt) {
    const G = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
    return enemies.filter((enemy) => enemy.state.position && G.footprintDistanceFt(
      center, "medium", enemy.state.position, enemy.state.template.size,
    ) <= radiusFt).length;
  }

  function chooseDamaging(caster, setup, turnKey) {
    const E = window.IRON_PIT_ACTION_ECONOMY;
    const P = window.IRON_PIT_BROWSER_SPELLCASTING;
    const Z = window.IRON_PIT_BROWSER_SUPPRESSION_ZONES;
    if (Z?.verbalBlocked(caster, setup) || !setup.map_definition) return null;
    const enemies = (caster.side === "heroes" ? setup.monsters : setup.heroes)
      .filter((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.position);
    if (!enemies.length) return null;
    let best = null;
    for (const action of caster.state.template.persistent_save_zone_actions || []) {
      if (!action.damageDiceCount || !E.available(caster.state, action.actionCost)) continue;
      if (action.concentration && caster.state.concentration) continue;
      if (action.expendsSpellSlot && !P?.slotSpellAvailable(caster.state, turnKey)) continue;
      if (action.resourceId && (caster.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
      for (const enemy of enemies) {
        const count = coverage(enemy.state.position, enemies, action.radiusFt || action.radius_ft || 0);
        if (!count) continue;
        const score = action.damageDiceCount * ((action.damageDiceSize || 6) + 1) / 2 * count;
        if (!best || score > best.score) best = { action, center: { ...enemy.state.position }, score };
      }
    }
    return best;
  }

  function install() {
    const selection = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
    if (!selection) throw new Error("Save-zone provider requires main-action selection.");
    selection.registerProvider({
      id: "save-zone",
      category: selection.CATEGORIES.SAVE_ZONE,
      rulesets: ["2014", "2024"],
      discover: ({ member, setup, turnKey }) => {
        const selected = chooseDamaging(member, setup, turnKey);
        return selected ? { payload: { selected, delivery: "spell", expectedDamage: selected.score } } : null;
      },
      resolve: ({ sequence, round, member, setup, turnKey }, candidate) => {
        const chosen = candidate.payload.selected;
        return window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
          sequence, round, member, setup, chosen.action, chosen.center, turnKey,
        );
      },
    });
  }

  install();
  window.IRON_PIT_BROWSER_SAVE_ZONE_PROVIDER = { chooseDamaging, install };
})();
