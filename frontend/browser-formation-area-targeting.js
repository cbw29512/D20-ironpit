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

  function lineLaneTargets(actor, setup, area) {
    try {
      if (setup?.arena_mode !== "formation" || area?.shape !== "line")
        throw new Error("Formation line requires a standard Pit line.");
      const opponents = actor.side === "heroes" ? setup.monsters : setup.heroes;
      const lanes = [[], [], []], counts = {front: 0, back: 0};
      for (const member of opponents) {
        const row = member.state.initial_formation_row || member.state.formation_row;
        if (!Object.hasOwn(counts, row))
          throw new Error("Line targeting requires assigned initial formation rows.");
        const lane = counts[row]++;
        if (lane >= 3) throw new Error("Formation row exceeds three lanes.");
        if (member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0)
          lanes[lane].push(member.combatant_id);
      }
      return lanes.reduce((best, lane) => lane.length > best.length ? lane : best, []);
    } catch (error) {
      console.error("Failed formation line targeting", {id: actor?.combatant_id, error});
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FORMATION_AREA_TARGETING = {coneFrontlineTargets, lineLaneTargets};
})();
