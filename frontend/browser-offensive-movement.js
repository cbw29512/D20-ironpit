(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const O = () => window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function chooseIntent(member, setup, turnKey) {
    try {
      if (!E().available(member.state, "action")) return null;
      const candidates = [];
      let legalNow = false;
      for (const target of F().targetOrder(member, setup)) {
        const distance = S().distance(member, target);
        for (const option of O().rangesForTarget(member, target, turnKey)) {
          if (distance <= option.range) {
            legalNow = true;
            continue;
          }
          candidates.push({
            needed: distance - option.range,
            distance,
            targetId: target.combatant_id,
            family: option.family,
            range: option.range,
          });
        }
      }
      if (legalNow || !candidates.length) return null;
      candidates.sort((a, b) => a.needed - b.needed || a.distance - b.distance
        || a.targetId.localeCompare(b.targetId) || a.family.localeCompare(b.family) || b.range - a.range);
      const best = candidates[0];
      return { targetId: best.targetId, desiredDistanceFt: best.range, family: best.family };
    } catch (error) {
      console.error("Failed browser offensive movement intent", { member: member.combatant_id, error });
      throw error;
    }
  }

  function move(sequence, round, member, setup, turnKey) {
    try {
      if (!setup.map_definition) return { events: [], sequence };
      const intent = chooseIntent(member, setup, turnKey);
      if (!intent) return { events: [], sequence };
      const target = [...setup.heroes, ...setup.monsters]
        .find((candidate) => candidate.combatant_id === intent.targetId);
      if (!target) throw new Error(`Missing offensive movement target ${intent.targetId}.`);
      const result = R().moveToward(
        sequence, round, member, target, setup, intent.desiredDistanceFt, "speed", { turnKey },
      );
      return { events: result.events, sequence: result.sequence };
    } catch (error) {
      console.error("Failed browser movement-to-offense execution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT = { chooseIntent, move };
})();