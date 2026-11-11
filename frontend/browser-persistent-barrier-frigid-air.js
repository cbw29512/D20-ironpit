(() => {
  "use strict";
  // One crossed *destroyed* edge is a finished movement-through-air event.
  // Source card supplies DC/dice/name; shared save runtime resolves the damage.
  const G = () => window.IRON_PIT_BROWSER_GRID_BARRIERS;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;

  function resolveCrossing(sequence, round, mover, setup, before, after, turnKey) {
    try {
      if (Math.abs(before.x - after.x) + Math.abs(before.y - after.y) !== 1) {
        throw new Error("Barrier air crossing requires one legal grid step.");
      }
      const key = G().edgeKey(before, after);
      const members = [...setup.heroes, ...setup.monsters];
      const events = [];
      for (const wall of setup.persistent_barriers || []) {
        if (round >= wall.expires_round) continue;
        if (!(wall.sections || []).some((section) =>
          !section.destroyed && section.current_hp > 0)) continue;
        const owner = members.find((member) => member.combatant_id === wall.source_id);
        if (!owner) throw new Error("Persistent barrier source has left the fight.");
        if ((wall.ends_on_source_death && owner.state.is_dead)
          || (wall.ends_on_source_incapacitated && E().isIncapacitated(owner.state))) continue;
        for (const section of wall.sections) {
          const save = section.destroyed_section_crossing_save;
          if (!section.destroyed || !save || !(section.edges || []).some((edge) =>
            G().edgeKey(edge.first, edge.second) === key)) continue;
          if (!S()?.resolveAction || !D()?.chain) {
            throw new Error("Destroyed wall crossing requires shared save and damage reactions.");
          }
          // The local air occupies the breached edge. Range zero is relative
          // to that edge, not the original caster's current position.
          const event = S().resolveAction(sequence, round, owner, mover, save, 0, {
            spendAction: false, checkResource: false, spendResource: false, setup,
          });
          const result = D().chain(sequence + 1, round, owner, event, setup, turnKey);
          events.push(...result.events);
          sequence = result.sequence;
        }
      }
      return {events, sequence};
    } catch (error) {
      console.error("Destroyed persistent barrier air crossing failed", {
        mover: mover?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BARRIER_AIR_CROSSING = {resolveCrossing};
})();