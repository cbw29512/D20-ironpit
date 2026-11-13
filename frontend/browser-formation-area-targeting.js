(() => {
  "use strict";
  // Source-owned cone shape; standard Pit uses formation exposure, not display.
  function coneFrontlineTargets(actor, setup, area) {
    try {
      if (setup?.arena_mode !== "formation" || area?.shape !== "cone")
        throw new Error("Formation cone requires a standard Pit cone.");
      const ranks = window.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT;
      if (!ranks) throw new Error("Shared formation engagement runtime missing.");
      const foes = actor.side === "heroes" ? setup.monsters : setup.heroes;
      return foes.filter(target => target.state.is_alive && !target.state.is_dead
        && target.state.current_hp > 0 && ranks.effectiveRow(target, setup) === "front")
        .map(target => target.combatant_id);
    } catch (error) {
      console.error("Failed standard Pit cone targeting", {id: actor?.combatant_id, error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_FORMATION_AREA_TARGETING = {coneFrontlineTargets};
})();
