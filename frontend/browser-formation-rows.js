(() => {
  "use strict";

  const F = () => window.IRON_PIT_BROWSER_FORMATION;

  function hasMeleeWeapon(template) {
    return (template?.attacks || []).some((attack) => attack.kind === "melee");
  }

  function hasRangedOrSpellOffense(template) {
    return F().usesBackline(template) || F().hasRangedWeaponOffense(template);
  }

  function isBackline(member) {
    try {
      const row = member.state.formation_row;
      if (row === "front") return false;
      if (row === "back") return true;
      const formation = F();
      if (typeof formation?.isBackline === "function") return Boolean(formation.isBackline(member));
      if (typeof formation?.usesBackline === "function") return Boolean(formation.usesBackline(member.state.template));
      return false;
    } catch (error) {
      console.error("Failed browser backline check", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function assignFormationRows(members) {
    try {
      if (members.length > 6) throw new Error("Iron Pit supports at most six combatants per side.");
      const priority = (member) => {
        const template = member.state.template;
        if (F().usesBackline(template)) return 2;
        return F().hasRangedWeaponOffense(template) && hasMeleeWeapon(template) ? 1 : 0;
      };
      const ranked = members.map((member, index) => ({ member, index }))
        .sort((a, b) => priority(a.member) - priority(b.member) || a.index - b.index);
      const frontIndices = new Set(ranked.filter((item) => priority(item.member) < 2)
        .slice(0, 3).map((item) => item.index));
      const backIndices = new Set(ranked.filter((item) =>
        !frontIndices.has(item.index) && priority(item.member) === 2)
        .slice(0, 3).map((item) => item.index));
      for (const { index } of ranked) {
        if (frontIndices.has(index) || backIndices.has(index)) continue;
        if (frontIndices.size < 3) frontIndices.add(index);
        else backIndices.add(index);
      }
      members.forEach((member, index) => {
        const row = frontIndices.has(index) ? "front" : "back";
        member.state.formation_row = row;
        member.state.initial_formation_row = row;
      });
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

  window.IRON_PIT_BROWSER_FORMATION_ROWS = {
    assignFormationRows, syncFormationRows, hasMeleeWeapon, hasRangedOrSpellOffense, isBackline,
  };
})();
