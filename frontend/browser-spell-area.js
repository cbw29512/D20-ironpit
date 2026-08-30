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

  function bestPlacement(caster, setup, radius, spellRange, protectedAllyIds = []) {
    const slotCount = areaSlotCount(radius);
    const [enemies, friends] = sides(caster, setup);
    const protectedIds = new Set(protectedAllyIds);
    const anchors = enemies.filter(living);
    const candidates = [];

    for (const anchor of anchors) {
      const center = anchor.position_ft;
      if (Math.abs(caster.position_ft - center) > spellRange) continue;
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
        if (enemyIds.length <= friendlyIds.length) continue;
        candidates.push({ startSlot: start, slotCount, centerFt: center, enemyIds, friendlyIds, protectedFriendlyIds });
      }
    }

    if (!candidates.length) return null;
    candidates.sort((a, b) => {
      const aNet = a.enemyIds.length - a.friendlyIds.length;
      const bNet = b.enemyIds.length - b.friendlyIds.length;
      return bNet - aNet
        || b.enemyIds.length - a.enemyIds.length
        || a.friendlyIds.length - b.friendlyIds.length
        || a.startSlot - b.startSlot;
    });
    return candidates[0];
  }

  window.IRON_PIT_BROWSER_SPELL_AREA = { areaSlotCount, bestPlacement };
})();
