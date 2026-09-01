(() => {
  "use strict";

  const MAX_SLOTS = 6;
  const CARD_WIDTH = 5;

  function areaSlotCount(radius) {
    if (radius < CARD_WIDTH || radius % CARD_WIDTH) {
      throw new Error("Iron Pit spell radii must be positive 5-foot increments.");
    }
    return Math.min(MAX_SLOTS, radius / CARD_WIDTH);
  }

  const living = (member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0;
  const sides = (caster, setup) => caster.side === "heroes"
    ? [setup.monsters, setup.heroes]
    : [setup.heroes, setup.monsters];

  function inside(member, slot, start, count, center, radius) {
    return slot >= start && slot < start + count && Math.abs(member.position_ft - center) <= radius;
  }

  function candidateCenters(caster, enemies, radius, spellRange) {
    const minimum = Math.min(...enemies.map((member) => member.position_ft)) - radius;
    const maximum = Math.max(...enemies.map((member) => member.position_ft)) + radius;
    const points = [];
    for (let point = minimum; point <= maximum; point += CARD_WIDTH) {
      if (Math.abs(caster.position_ft - point) <= spellRange) points.push(point);
    }
    return points;
  }

  function bestPlacement(caster, setup, radius, spellRange, protectedAllyIds = []) {
    const slotCount = areaSlotCount(radius);
    const [enemies, friends] = sides(caster, setup);
    const protectedIds = new Set(protectedAllyIds);
    const livingEnemies = enemies.filter(living);
    if (!livingEnemies.length) return null;
    const candidates = [];

    for (const center of candidateCenters(caster, livingEnemies, radius, spellRange)) {
      for (let start = 0; start <= MAX_SLOTS - slotCount; start += 1) {
        const enemyIds = enemies
          .map((member, slot) => ({ member, slot }))
          .filter(({ member, slot }) => living(member) && inside(member, slot, start, slotCount, center, radius))
          .map(({ member }) => member.combatant_id);
        if (!enemyIds.length) continue;

        const friendlyIds = [], protectedFriendlyIds = [];
        friends.forEach((member, slot) => {
          if (!living(member) || !inside(member, slot, start, slotCount, center, radius)) return;
          (protectedIds.has(member.combatant_id) ? protectedFriendlyIds : friendlyIds).push(member.combatant_id);
        });
        if (friendlyIds.length) continue;
        candidates.push({ startSlot: start, slotCount, centerFt: center, enemyIds, friendlyIds, protectedFriendlyIds });
      }
    }

    if (!candidates.length) return null;
    candidates.sort((a, b) => b.enemyIds.length - a.enemyIds.length
      || b.protectedFriendlyIds.length - a.protectedFriendlyIds.length
      || Math.abs(caster.position_ft - a.centerFt) - Math.abs(caster.position_ft - b.centerFt)
      || a.startSlot - b.startSlot);
    return candidates[0];
  }

  window.IRON_PIT_BROWSER_SPELL_AREA = { areaSlotCount, bestPlacement };
})();
