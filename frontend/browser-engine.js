(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TURN;
  const L = () => window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
  const P = () => window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION, B = () => window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS;
  const AT = () => window.IRON_PIT_BROWSER_ATTACHMENTS;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const M = () => window.IRON_PIT_BROWSER_ARENA_MAP;
  const G = () => window.IRON_PIT_BROWSER_GRID_PLACEMENT;
  const I = () => window.IRON_PIT_BROWSER_INITIATIVE;
  const heroes = () => window.IRON_PIT_BROWSER_HEROES;
  const monsters = () => window.IRON_PIT_BROWSER_MONSTERS;

  function cloneTemplate(template) { return structuredClone(template); }
  function placeStandardGrid(heroMembers, monsterMembers) {
    if (!M()?.buildStandardMap || !M()?.buildHeroDeploymentZone || !M()?.buildMonsterDeploymentZone || !G()?.packZone || !G()?.apply) throw new Error("Authoritative Iron Pit grid deployment modules are not loaded.");
    const mapDefinition = M().buildStandardMap();
    G().apply(heroMembers, G().packZone(mapDefinition, M().buildHeroDeploymentZone(), heroMembers));
    G().apply(monsterMembers, G().packZone(mapDefinition, M().buildMonsterDeploymentZone(), monsterMembers));
    return mapDefinition;
  }
  function buildSetup(selection) {
    const heroMembers = selection.hero_ids.map((id, index) => {
      if (!heroes()[id]) throw new Error(`Unknown certified hero: ${id}`);
      const template = cloneTemplate(heroes()[id]);
      return { combatant_id: `hero-${index + 1}:${id}`, side: "heroes", position_ft: F().startingPosition(template, "heroes"), state: S().buildState(template) };
    });
    const monsterMembers = selection.monster_ids.map((id, index) => {
      if (!monsters()[id]) throw new Error(`Unknown certified monster: ${id}`);
      const template = cloneTemplate(monsters()[id]);
      return { combatant_id: `monster-${index + 1}:${id}`, side: "monsters", position_ft: F().startingPosition(template, "monsters"), state: S().buildState(template) };
    });
    const mapDefinition = placeStandardGrid(heroMembers, monsterMembers);
    return { heroes: heroMembers, monsters: monsterMembers,
      hero_total_levels: heroMembers.reduce((sum, item) => sum + item.state.template.level, 0),
      monster_total_cr: totalCr(monsterMembers.map((item) => item.state.template.challenge_rating)), map_definition: mapDefinition };
  }
  function crNumber(value) { const text = String(value || "0"); if (!text.includes("/")) return Number(text) || 0; const [a, b] = text.split("/").map(Number); return a / b; }
  function totalCr(values) { const quarters = Math.round(values.reduce((sum, value) => sum + crNumber(value), 0) * 4); if (quarters % 4 === 0) return String(quarters / 4); const divisor = quarters % 2 === 0 ? 2 : 4; return `${quarters / (4 / divisor)}/${divisor}`; }
  function defeatedMember(member) { const state = member.state; if (state.template.kind === "character") return state.is_dead || !state.is_alive; return state.current_hp <= 0 || state.is_dead || !state.is_alive; }
  function outcome(setup) { const defeated = (side) => side.every(defeatedMember), heroesDead = defeated(setup.heroes), monstersDead = defeated(setup.monsters); if (heroesDead && monstersDead) return "draw"; if (monstersDead) return "heroes_win"; if (heroesDead) return "monsters_win"; return "active"; }
  function lifecycle(sequence, round, member, setup, targetTiming, sourceTiming) {
    const target = L().resolveTargetTiming(sequence, round, member, targetTiming);
    const source = L().resolveSourceTiming(target.sequence, round, member, setup, sourceTiming);
    if (sourceTiming === "source_turn_end") window.IRON_PIT_BROWSER_MODIFIERS?.expireSourceTurn([...setup.heroes, ...setup.monsters].map((entry) => entry.state), member.combatant_id, round);
    return { events: [...target.events, ...source.events], sequence: source.sequence };
  }
  function runEncounter(selection) {
    if (!selection.hero_ids?.length || !selection.monster_ids?.length || selection.hero_ids.length > 6 || selection.monster_ids.length > 6) throw new Error("Iron Pit requires 1-6 cards per side.");
    const setup = buildSetup(selection), prep = P()?.prepare(setup, 1) || { events: [], sequence: 1 }, init = I().resolve(setup);
    const members = [...setup.heroes, ...setup.monsters], states = members.map((member) => member.state), byId = new Map(members.map((member) => [member.combatant_id, member]));
    const events = [...prep.events, ...I().events(init, setup, prep.sequence)]; let sequence = events.length + 1, resolvedRound = 0;
    for (let round = 1; round <= 100; round += 1) {
      resolvedRound = round;
      for (const id of init.turn_order) {
        const current = outcome(setup); if (current !== "active") return finish(setup, init, events, current, round, sequence);
        const member = byId.get(id); B()?.cleanupDisabledSources(setup); window.IRON_PIT_BROWSER_MODIFIERS?.expireSourceTurnStart(states, member.combatant_id);
        S().refreshStartOfTurn(member.state); C()?.endIfExpired(member.state, round, states);
        const attachment = AT()?.startTurn(sequence, round, member, setup) || { events: [], sequence };
        events.push(...attachment.events); sequence = attachment.sequence;
        const start = lifecycle(sequence, round, member, setup, "target_turn_start", "source_turn_start"); events.push(...start.events); sequence = start.sequence;
        if (member.state.template.kind === "character" && member.state.current_hp === 0 && !member.state.is_dead && !member.state.is_stable) events.push(T().deathSave(sequence++, round, member));
        if (member.state.current_hp > 0 && !member.state.is_dead) { const turn = T().resolveTurn(sequence, round, member, setup); events.push(...turn.events); sequence = turn.sequence; }
        const end = lifecycle(sequence, round, member, setup, "target_turn_end", "source_turn_end"); events.push(...end.events); sequence = end.sequence;
      }
      const current = outcome(setup); if (current !== "active") return finish(setup, init, events, current, round, sequence);
    }
    return finish(setup, init, events, "draw", resolvedRound, sequence);
  }
  function finish(setup, init, events, result, round, sequence) {
    events.push({ sequence, round_number: round, event_type: result === "draw" ? "draw" : "victory", actor_id: "arena", actor_name: "Iron Pit", animation: "victory", description: result === "heroes_win" ? "Heroes win the deathmatch." : result === "monsters_win" ? "Monsters win the deathmatch." : "The fight reaches the arena round limit and ends in a draw." });
    return { battle_id: crypto.randomUUID?.() || `battle-${Date.now()}`, outcome: result, rounds: round, setup, initiative: init, events, ruleset: "SRD 5.2.1 Iron Pit grid deathmatch subset" };
  }
  window.IRON_PIT_BROWSER_ENGINE = { runEncounter };
})();