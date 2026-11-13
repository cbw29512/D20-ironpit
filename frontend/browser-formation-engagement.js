(() => {
  "use strict";
  // Standard Iron Pit: state is fight-local formation_row, not x/y or feet.
  // Cards retain immutable printed reach/range; engagement is not movement.
  const active = member => Boolean(member?.state?.is_alive
    && !member.state.is_dead && member.state.current_hp > 0);
  const enabled = setup => setup?.arena_mode === "formation";

  function effectiveRow(member, setup) {
    try {
      let row = member?.state?.formation_row;
      if (!["front", "back"].includes(row)) {
        row = window.IRON_PIT_BROWSER_FORMATION?.usesBackline?.(member.state.template)
          ? "back" : "front";
      }
      if (row === "front") return "front";
      const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
      return allies.some(ally => ally.state.formation_row === "front" && active(ally))
        ? "back" : "front";
    } catch (error) {
      console.error("Failed effective formation role.", {id: member?.combatant_id, error});
      throw error;
    }
  }

  function weaponTargetAllowed(member, target, attack, setup) {
    try {
      if (!enabled(setup)) return true;
      if (!active(target)) return false;
      if (attack.kind === "melee") {
        return effectiveRow(member, setup) === "front"
          && effectiveRow(target, setup) === "front";
      }
      // Backline uses real ranged profiles; promoted ranged-only combatants
      // do not acquire an invented melee attack or damage profile.
      return attack.kind === "ranged";
    } catch (error) {
      console.error("Failed formation weapon target.", {id: member?.combatant_id, error});
      throw error;
    }
  }

  function engagementDistance(attack) {
    // Compatibility value for the existing roll/condition pipeline:
    // never derived from the battlefield's display coordinates.
    try {
      if (attack.kind === "melee") return Math.min(5, attack.reach || 5);
      if (attack.kind !== "ranged" || !(attack.normal > 0)) {
        throw new Error(`Missing ranged profile for ${attack.name || attack.id}.`);
      }
      return attack.normal;
    } catch (error) {
      console.error("Failed formation attack context.", {id: attack?.id, error});
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT = {
    enabled, effectiveRow, weaponTargetAllowed, engagementDistance,
  };
})();
