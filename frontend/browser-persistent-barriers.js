(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const S = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const B = () => window.IRON_PIT_BROWSER_GRID_BARRIERS;

  function edgeVertices(edge) {
    const a = edge.first, b = edge.second;
    if (Math.abs(a.x - b.x) + Math.abs(a.y - b.y) !== 1) {
      throw new Error("Barrier edges must separate orthogonally adjacent cells.");
    }
    if (a.y === b.y) {
      const x = Math.max(a.x, b.x);
      return [[x, a.y], [x, a.y + 1]];
    }
    const y = Math.max(a.y, b.y);
    return [[a.x, y], [a.x + 1, y]];
  }

  function straightSection(edges, expectedEdges) {
    if (!Array.isArray(edges) || edges.length !== expectedEdges) return false;
    const segments = edges.map(edgeVertices);
    const horizontal = segments.map(([a, b]) => a[1] === b[1]);
    if (new Set(horizontal).size !== 1) return false;
    const axis = horizontal[0] ? segments.map(([a]) => a[1]) : segments.map(([a]) => a[0]);
    if (new Set(axis).size !== 1) return false;
    const vertices = new Map();
    for (const [a, b] of segments) {
      const ak = a.join(","), bk = b.join(",");
      if (!vertices.has(ak)) vertices.set(ak, new Set());
      if (!vertices.has(bk)) vertices.set(bk, new Set());
      vertices.get(ak).add(bk); vertices.get(bk).add(ak);
    }
    return vertices.size === edges.length + 1
      && [...vertices.values()].filter((items) => items.size === 1).length === 2;
  }

  function connected(sectionEdges) {
    const segments = sectionEdges.flatMap((edges) => edges.map(edgeVertices));
    if (!segments.length) return false;
    const graph = new Map();
    for (const [a, b] of segments) {
      const ak = a.join(","), bk = b.join(",");
      if (!graph.has(ak)) graph.set(ak, new Set());
      if (!graph.has(bk)) graph.set(bk, new Set());
      graph.get(ak).add(bk); graph.get(bk).add(ak);
    }
    const seen = new Set(), queue = [segments[0][0].join(",")];
    while (queue.length) {
      const key = queue.shift();
      if (seen.has(key)) continue;
      seen.add(key);
      queue.push(...(graph.get(key) || []));
    }
    return seen.size === graph.size;
  }

  function validate(action, sectionEdges, caster, setup) {
    if (!setup.map_definition || !caster.state.position) {
      throw new Error("Persistent barriers require the authoritative grid.");
    }
    const support = setup.map_definition.support_materials || [];
    if (action.requiredSupportMaterial && !support.includes(action.requiredSupportMaterial)) {
      throw new Error(`${action.name} requires ${action.requiredSupportMaterial} support on this map.`);
    }
    if (sectionEdges.length < action.minSections || sectionEdges.length > action.maxSections) {
      throw new Error(`${action.name} has an illegal section count.`);
    }
    const expected = action.sectionLengthFt / 5, keys = new Set();
    const geometry = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
    const casterCells = geometry.occupiedCells(caster.state.position, caster.state.template.size);
    const members = [...setup.heroes, ...setup.monsters];
    for (const edges of sectionEdges) {
      if (!straightSection(edges, expected)) throw new Error(`${action.name} has an illegal panel shape.`);
      for (const edge of edges) {
        const key = B().edgeKey(edge.first, edge.second);
        if (keys.has(key)) throw new Error(`${action.name} cannot reuse an edge.`);
        keys.add(key);
        for (const cell of [edge.first, edge.second]) {
          if (cell.x < 0 || cell.y < 0
            || cell.x >= setup.map_definition.width_squares
            || cell.y >= setup.map_definition.height_squares) {
            throw new Error(`${action.name} edge lies outside the map.`);
          }
        }
        const distanceFt = Math.min(...casterCells.map(([x, y]) => Math.min(
          Math.max(Math.abs((edge.first.x - x) * 5), Math.abs((edge.first.y - y) * 5)),
          Math.max(Math.abs((edge.second.x - x) * 5), Math.abs((edge.second.y - y) * 5)),
        )));
        if (distanceFt > action.castRangeFt) throw new Error(`${action.name} edge exceeds cast range.`);
        for (const member of members) {
          if (!member.state.position) continue;
          const cells = new Set(
            geometry.occupiedCells(member.state.position, member.state.template.size)
              .map(([x, y]) => `${x},${y}`),
          );
          if (cells.has(`${edge.first.x},${edge.first.y}`)
            && cells.has(`${edge.second.x},${edge.second.y}`)) {
            throw new Error(`${action.name} would cut through a creature space.`);
          }
        }
      }
    }
    if (action.sectionsMustBeContiguous && !connected(sectionEdges)) {
      throw new Error(`${action.name} sections must be contiguous.`);
    }
  }

  function alternateGrant(caster, action) {
    return (caster.state.template.alternate_spell_cast_grants || [])
      .find((grant) => grant.spell_id === action.id
        && (caster.state.resources?.[grant.resource_id] || 0) >= (grant.resource_cost || 1)) || null;
  }

  function cast(sequence, round, caster, setup, action, sectionEdges, turnKey, useAlternate = false) {
    validate(action, sectionEdges, caster, setup);
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} unavailable.`);
    const expendsSpellSlot = !useAlternate && action.level > 0;
    if (!S().spellCastAvailable(caster.state, turnKey, action.level, action.actionCost, { expendsSpellSlot })) {
      throw new Error(`${action.name} is not legal under the active edition's per-turn casting rule.`);
    }
    let resourceRemaining = null;
    if (useAlternate) {
      const grant = alternateGrant(caster, action);
      if (!grant || grant.cast_level !== action.level) throw new Error("No matching alternate barrier cast.");
      const cost = grant.resource_cost || 1;
      caster.state.resources[grant.resource_id] -= cost;
      resourceRemaining = caster.state.resources[grant.resource_id];
    } else {
      const resourceId = `spell-slot-${action.level}`;
      if ((caster.state.resources?.[resourceId] || 0) < 1) throw new Error(`No level ${action.level} spell slot remains.`);
      caster.state.resources[resourceId] -= 1;
      resourceRemaining = caster.state.resources[resourceId];
    }
    S().markSpellCast(caster.state, turnKey, action.level, action.actionCost, { expendsSpellSlot });
    E().spend(caster.state, action.actionCost);
    const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
    if (action.concentration) {
      C().start(caster.state, caster.combatant_id, action.id, round, states, round + action.durationRounds, action.level);
      B().cleanup(setup, round);
    }
    if (!Array.isArray(setup.persistent_barriers)) setup.persistent_barriers = [];
    const barrierId = `${caster.combatant_id}:${action.id}:${round}:${setup.persistent_barriers.length + 1}`;
    setup.persistent_barriers.push({
      barrier_id: barrierId, source_id: caster.combatant_id, source_side: caster.side,
      action_id: action.id, action_name: action.name, concentration: Boolean(action.concentration),
      applied_round: round, expires_round: round + action.durationRounds,
      permanent_after_full_duration: Boolean(action.permanentAfterFullDuration),
      blocks_movement: action.blocksMovement !== false,
      blocks_line_of_sight: action.blocksLineOfSight !== false,
      sections: sectionEdges.map((edges, index) => ({
        section_id: `${barrierId}:section-${index + 1}`, edges: edges.map((edge) => ({ first: {...edge.first}, second: {...edge.second} })),
        current_hp: action.hitPointsPerSection, armor_class: action.armorClass,
        damage_immunities: [...(action.damageImmunities || [])], destroyed: false,
      })),
      animation: action.animation || "persistent-barrier",
    });
    return {
      event: {
        sequence, round_number: round, event_type: "feature",
        actor_id: caster.combatant_id, actor_name: caster.state.template.name,
        feature_id: action.id, resource_remaining: resourceRemaining,
        animation: action.animation || "persistent-barrier",
        description: `${caster.state.template.name} creates ${action.name} with ${sectionEdges.length} barrier sections.`,
      },
      sequence: sequence + 1,
    };
  }

  function damage(setup, barrierId, sectionId, amount, damageType) {
    if (!Number.isInteger(amount) || amount < 0) throw new Error("Barrier damage must be nonnegative.");
    const barrier = (setup.persistent_barriers || []).find((item) => item.barrier_id === barrierId);
    const section = barrier?.sections?.find((item) => item.section_id === sectionId);
    if (!section) throw new Error("Unknown barrier section.");
    const before = section.current_hp, immune = (section.damage_immunities || []).includes(damageType);
    const applied = immune || section.destroyed ? 0 : Math.min(amount, section.current_hp);
    section.current_hp = Math.max(0, section.current_hp - applied);
    if (section.current_hp === 0) section.destroyed = true;
    return { hpBefore: before, hpAfter: section.current_hp, appliedDamage: applied, immune, destroyed: section.destroyed };
  }

  window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS = { cast, damage, validate };
})();
