(() => {
  "use strict";
  // Cards provide the save/material/resource. This policy supplies legal
  // square-line placement and normal source-neutral save/damage execution.
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const B = () => window.IRON_PIT_BROWSER_PERSISTENT_BARRIERS;
  const G = () => window.IRON_PIT_BROWSER_GRID_BARRIERS;

  function* layouts(action, center, width, height) {
    const length = action.sectionLengthFt / 5;
    for (const axis of ["x", "y"]) {
      for (let count = action.minSections; count <= action.maxSections; count += 1) {
        const total = length * count;
        for (let before = 0; before < total; before += 1) {
          for (const side of [-1, 1]) {
            const coordinates = [];
            for (let offset = 0; offset < total; offset += 1) {
              const x = center.x + (axis === "x" ? offset - before : 0);
              const y = center.y + (axis === "y" ? offset - before : 0);
              const nx = x + (axis === "y" ? side : 0);
              const ny = y + (axis === "x" ? side : 0);
              coordinates.push({ x, y, nx, ny });
            }
            if (!coordinates.every(({x,y,nx,ny}) =>
              x >= 0 && y >= 0 && nx >= 0 && ny >= 0
              && x < width && nx < width && y < height && ny < height)) continue;
            const edges = coordinates.map(({x,y,nx,ny}) => ({
              first: {x,y}, second: {x:nx,y:ny},
            }));
            const sections = [];
            for (let start = 0; start < edges.length; start += length) {
              sections.push(edges.slice(start, start + length));
            }
            yield { sections, cells: new Set(coordinates.map(({x,y}) => `${x},${y}`)) };
          }
        }
      }
    }
  }

  function choose(actor, setup) {
    try {
      if (!E()?.available(actor.state, "action") || !setup.map_definition
        || !actor.state.position) return null;
      const opponents = actor.side === "heroes" ? setup.monsters : setup.heroes;
      const friendly = actor.side === "heroes" ? setup.heroes : setup.monsters;
      const alive = (member) => member.state?.position && member.state.is_alive !== false
        && !member.state.is_dead && member.state.current_hp > 0;
      const living = opponents.filter(alive), all = [...opponents, ...friendly];
      if (!living.length) return null;
      const walls = setup.persistent_barriers || [];
      const used = new Set(walls.flatMap((wall) => (wall.sections || [])
        .filter((section) => !section.destroyed)
        .flatMap((section) => (section.edges || [])
          .map((edge) => G().edgeKey(edge.first, edge.second)))));
      let best = null;
      for (const action of actor.state.template.persistent_barrier_actions || []) {
        const save = action.onCreationSave;
        if (!save?.damageDiceCount || action.actionCost !== "action"
          || (action.resourceId && (actor.state.resources?.[action.resourceId] ?? 0)
            < (action.resourceCost || 1))) continue;
        for (const foe of living) {
          for (const {sections, cells} of layouts(action, foe.state.position,
            setup.map_definition.width_squares, setup.map_definition.height_squares)) {
            if (sections.flat().some((edge) => used.has(G().edgeKey(edge.first, edge.second)))) continue;
            try { B().validate(action, sections, actor, setup); }
            catch (error) {
              if (error instanceof Error && /illegal|out|cut through|exceeds|requir|reuse|cannot|wall/i.test(error.message)) continue;
              throw error;
            }
            const affectedIds = all.filter((member) => alive(member)
              && cells.has(`${member.state.position.x},${member.state.position.y}`))
              .map((member) => member.combatant_id);
            const enemiesHit = living.filter((member) => affectedIds.includes(member.combatant_id)).length;
            const alliesHit = affectedIds.length - enemiesHit;
            const average = save.damageDiceCount * ((save.damageDiceSize || 6) + 1) / 2;
            const expectedDamage = average * (enemiesHit - 2 * alliesHit);
            if (enemiesHit < 1 || expectedDamage <= 0) continue;
            const item = {action, sections, affectedIds, expectedDamage};
            if (!best || expectedDamage > best.expectedDamage
              || (expectedDamage === best.expectedDamage && sections.length < best.sections.length)) best = item;
          }
        }
      }
      return best;
    } catch (error) {
      console.error("Universal offensive barrier placement failed", {actor:actor?.combatant_id,error});
      throw error;
    }
  }

  function resolve(sequence, round, actor, setup, turnKey, choice) {
    try {
      const placed = B().cast(sequence, round, actor, setup, choice.action, choice.sections, turnKey);
      placed.event.description += " Arena forced displacement is logged without moving targets.";
      const events = [placed.event], members = [...setup.heroes, ...setup.monsters];
      sequence = placed.sequence;
      const saveRuntime = window.IRON_PIT_BROWSER_SAVES;
      const reactions = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
      const distance = window.IRON_PIT_BROWSER_FORMATION?.saveDistance;
      if (!saveRuntime?.resolveAction || !reactions?.chain || !distance) {
        throw new Error("Offensive barriers require shared save/damage reaction/formation runtimes.");
      }
      for (const id of choice.affectedIds) {
        const target = members.find((member) => member.combatant_id === id);
        if (!target || target.state.is_dead || target.state.is_alive === false) continue;
        const event = saveRuntime.resolveAction(
          sequence, round, actor, target, choice.action.onCreationSave,
          distance(actor, target, choice.action.onCreationSave.range),
          { spendAction: false, checkResource: false, spendResource: false, setup },
        );
        const result = reactions.chain(sequence + 1, round, actor, event, setup);
        events.push(...result.events);
        sequence = result.sequence;
      }
      return {events, sequence};
    } catch (error) {
      console.error("Offensive barrier save resolution failed", {actor:actor?.combatant_id,error});
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BARRIER_OFFENSE = {choose,resolve};
})();