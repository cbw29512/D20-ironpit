(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function passengers(caster, setup, action) {
    if (!action.passengerCount) return [];
    const allies = caster.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.filter((ally) => ally.combatant_id !== caster.combatant_id
      && ally.state.is_alive && !ally.state.is_dead
      && S().distance(caster, ally) <= (action.passengerRangeFt || 5))
      .sort((a, b) => a.state.current_hp - b.state.current_hp || a.combatant_id.localeCompare(b.combatant_id))
      .slice(0, action.passengerCount);
  }

  function occupied(caster, destination, setup) {
    return [...setup.heroes, ...setup.monsters].some((member) =>
      member.combatant_id !== caster.combatant_id && member.state.is_alive && !member.state.is_dead
      && member.state.position
      && G().footprintDistanceFt(
        destination, caster.state.template.size, member.state.position, member.state.template.size,
      ) === 0);
  }

  function chooseDestination(caster, setup, action) {
    if (!setup.map_definition || !caster.state.position) return null;
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const living = enemies.filter((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.position);
    if (!living.length) return null;
    const target = living.slice().sort((a, b) =>
      S().distance(caster, a) - S().distance(caster, b) || a.combatant_id.localeCompare(b.combatant_id))[0];
    if (S().distance(caster, target) <= 5) return null;
    let best = null;
    let bestKey = null;
    for (let x = 0; x < setup.map_definition.width_squares; x += 1) {
      for (let y = 0; y < setup.map_definition.height_squares; y += 1) {
        const destination = { x, y };
        if (occupied(caster, destination, setup)) continue;
        if (G().footprintDistanceFt(
          caster.state.position, caster.state.template.size, destination, caster.state.template.size,
        ) > action.range) continue;
        const distance = G().footprintDistanceFt(
          destination, caster.state.template.size, target.state.position, target.state.template.size,
        );
        const better = bestKey == null
          || distance < bestKey[0] || (distance === bestKey[0] && (x < bestKey[1] || (x === bestKey[1] && y < bestKey[2])));
        if (better) {
          best = destination;
          bestKey = [distance, x, y];
        }
      }
    }
    return best;
  }

  function choose(caster, setup, turnKey) {
    if (window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(caster, setup)) return null;
    for (const action of caster.state.template.teleport_actions || []) {
      if (!E().available(caster.state, action.actionCost)) continue;
      if (action.expendsSpellSlot && !P()?.slotSpellAvailable(caster.state, turnKey)) continue;
      if (action.resourceId && (caster.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
      const destination = chooseDestination(caster, setup, action);
      if (destination) return { action, destination };
    }
    return null;
  }

  function resolve(sequence, round, caster, setup, action, destination, turnKey) {
    if (window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(caster, setup)) {
      throw new Error(`${action.name} cannot be cast inside a Silence effect.`);
    }
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
    if (action.expendsSpellSlot) P().markSlotSpellCast(caster.state, turnKey);
    E().spend(caster.state, action.actionCost);
    if (action.resourceId) caster.state.resources[action.resourceId] -= action.resourceCost || 1;
    const travelers = [caster, ...passengers(caster, setup, action)];
    const events = [];
    if (occupied(caster, destination, setup)) {
      for (const traveler of travelers) {
        const rolls = window.IRON_PIT_DICE.rollMany(4, 6);
        const amount = rolls.reduce((sum, roll) => sum + roll, 0);
        const hpBefore = traveler.state.current_hp;
        window.IRON_PIT_BROWSER_ATTACK.applyDamage(
          traveler.state, amount, false, ["force"],
          [...setup.heroes, ...setup.monsters].map((member) => member.state), setup,
        );
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: caster.combatant_id, actor_name: caster.state.template.name,
          target_id: traveler.combatant_id, target_name: traveler.state.template.name,
          damage_roll: { notation: "4d6", rolls, modifier: 0, total: amount },
          hp_before: hpBefore, hp_after: traveler.state.current_hp,
          feature_id: action.id, animation: action.animation || "teleport",
          description: `${traveler.state.template.name} takes ${amount} force damage as ${action.name} fails in an occupied space.`,
        });
      }
      return { events, sequence };
    }
    const origin = { ...caster.state.position };
    const offsetX = destination.x - origin.x;
    const offsetY = destination.y - origin.y;
    for (const traveler of travelers) {
      if (!traveler.state.position) continue;
      traveler.state.position = { x: traveler.state.position.x + offsetX, y: traveler.state.position.y + offsetY };
    }
    events.push({
      sequence, round_number: round, event_type: "movement",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      feature_id: action.id,
      resource_remaining: action.resourceId ? caster.state.resources[action.resourceId] : null,
      grid_position_before: origin, grid_position_after: { ...destination },
      animation: action.animation || "teleport",
      description: `${caster.state.template.name} teleports with ${action.name}.`,
    });
    return { events, sequence: sequence + 1 };
  }

  window.IRON_PIT_BROWSER_TELEPORT = { choose, resolve };
})();
