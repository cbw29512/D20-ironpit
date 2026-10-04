(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;

  function hasMeleeWeapon(template) {
    return (template?.attacks || []).some((attack) => attack.kind === "melee");
  }

  function hasRangedOrSpellOffense(template) {
    return F().usesBackline(template) || F().hasRangedWeaponOffense(template);
  }

  function assignFormationRows(members) {
    try {
      const mixed = [];
      for (const member of members) {
        const template = member.state.template;
        if (F().usesBackline(template)) member.state.formation_row = "back";
        else if (F().hasRangedWeaponOffense(template) && hasMeleeWeapon(template)) mixed.push(member);
        else member.state.formation_row = "front";
      }
      mixed.forEach((member, index) => {
        member.state.formation_row = index === 0 ? "front" : "back";
      });
      for (const member of members) member.state.initial_formation_row = member.state.formation_row;
    } catch (error) {
      console.error("Failed to assign browser formation rows", { error });
      throw error;
    }
  }

  function syncFormationRows(setup) {
    try {
      const promoted = [];
      for (const side of [setup.heroes, setup.monsters]) {
        for (const member of side) {
          const state = member.state;
          if (!state.is_alive || state.is_dead || state.current_hp <= 0 || state.formation_row !== "back") continue;
          if (hasRangedOrSpellOffense(state.template)) continue;
          const hasFront = side.some((ally) => ally.combatant_id !== member.combatant_id
            && ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0
            && ally.state.formation_row === "front");
          if (hasFront) continue;
          state.formation_row = "front";
          promoted.push(member);
        }
      }
      return promoted;
    } catch (error) {
      console.error("Failed to sync browser formation rows", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FORMATION_ROWS = { assignFormationRows, syncFormationRows, hasMeleeWeapon, hasRangedOrSpellOffense };
})();
