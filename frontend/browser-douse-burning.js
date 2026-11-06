// Universal douse for source-proven burning. No range invented.
window.IRON_PIT_BROWSER_DOUSE_BURNING = {
  douse(target, actorId, roundNumber) {
    if (!target || !Array.isArray(target.timedEffects)) return [];
    const before = target.timedEffects.length;
    target.timedEffects = target.timedEffects.filter(e => e.effectId !== "burning");
    if (Array.isArray(target.activeEffectIds)) {
      target.activeEffectIds = target.activeEffectIds.filter(id => id !== "burning");
    }
    if (target.timedEffects.length === before) return [];
    return [{
      eventType: "feature",
      roundNumber,
      actorId,
      actorName: "douse",
      targetId: target.id || null,
      featureId: "douse-burning",
      animation: "none",
      description: "A creature takes an action to douse the fire.",
    }];
  },
};
