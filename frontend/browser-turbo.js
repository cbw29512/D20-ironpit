(() => {
  "use strict";

  const UINT32_RANGE = 0x100000000, MAX_FIGHTS = 10000;
  const engine = () => window.IRON_PIT_BROWSER_ENGINE;
  const lab = () => window.IRON_PIT_BATTLE_LAB;

  function validSeed(seed) {
    const value = Number(seed);
    if (!Number.isInteger(value) || value < 0 || value > 0xffffffff) throw new RangeError("Seed must be a 32-bit unsigned integer.");
    return value >>> 0;
  }

  function seededDice(seed) {
    let state = validSeed(seed);
    const history = [];
    const next = () => {
      state = (Math.imul(1664525, state) + 1013904223) >>> 0;
      return state;
    };
    const roll = (sides) => {
      try {
        if (!Number.isInteger(sides) || sides < 2) throw new RangeError("Die sides must be an integer >= 2.");
        const limit = UINT32_RANGE - (UINT32_RANGE % sides);
        let value;
        do value = next(); while (value >= limit);
        const result = (value % sides) + 1;
        history.push({ sides, value: result });
        return result;
      } catch (error) {
        console.error(`Seeded d${sides} roll failed`, error);
        throw error;
      }
    };
    const rollMany = (count, sides) => {
      try {
        if (!Number.isInteger(count) || count < 1) throw new RangeError("Dice count must be positive.");
        return Array.from({ length: count }, () => roll(sides));
      } catch (error) { console.error("Seeded dice pool failed", error); throw error; }
    };
    return {
      roll, rollMany,
      clearHistory: () => { history.length = 0; },
      getHistory: () => history.map((item) => ({ ...item })),
    };
  }

  function randomSeed() {
    try {
      if (!globalThis.crypto?.getRandomValues) throw new Error("Web Crypto RNG is unavailable.");
      const buffer = new Uint32Array(1); globalThis.crypto.getRandomValues(buffer); return buffer[0];
    } catch (error) { console.error("Turbo batch seed generation failed", error); throw error; }
  }

  function deriveSeed(batchSeed, fightNumber) {
    let value = (validSeed(batchSeed) ^ Math.imul(fightNumber, 0x9e3779b9)) >>> 0;
    value ^= value >>> 16; value = Math.imul(value, 0x7feb352d) >>> 0;
    value ^= value >>> 15; value = Math.imul(value, 0x846ca68b) >>> 0;
    return (value ^ (value >>> 16)) >>> 0;
  }

  function runSeeded(selection, seed) {
    const prior = window.IRON_PIT_DICE, dice = seededDice(seed);
    try {
      window.IRON_PIT_DICE = dice;
      const battle = engine().runEncounter(structuredClone(selection));
      const rolls = dice.getHistory();
      const diagnosticId = lab()?.diagnosticId?.(selection.hero_ids, selection.monster_ids, rolls) || null;
      return { battle, seed: validSeed(seed), rolls, diagnostic_id: diagnosticId };
    } catch (error) {
      console.error(`Seeded Iron Pit fight failed for seed ${seed}`, error);
      throw error;
    } finally { window.IRON_PIT_DICE = prior; }
  }

  const survivors = (members) => members.filter((member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0).length;
  function fightSummary(fightNumber, replay) {
    const battle = replay.battle;
    return {
      fight_number: fightNumber, seed: replay.seed, outcome: battle.outcome, rounds: battle.rounds,
      hero_survivors: survivors(battle.setup.heroes), monster_survivors: survivors(battle.setup.monsters),
      roll_count: replay.rolls.length, diagnostic_id: replay.diagnostic_id,
      safety_stop: battle.outcome === "draw" && battle.rounds >= 100,
    };
  }

  const rate = (value, total) => total ? Number(((value / total) * 100).toFixed(2)) : 0;
  async function runBatch(selection, fights, batchSeed = null, onProgress = null) {
    const count = Number(fights);
    if (!Number.isInteger(count) || count < 1 || count > MAX_FIGHTS) throw new RangeError(`Turbo fights must be 1-${MAX_FIGHTS}.`);
    const resolvedSeed = batchSeed == null ? randomSeed() : validSeed(batchSeed), summaries = [], errors = [];
    for (let fightNumber = 1; fightNumber <= count; fightNumber += 1) {
      const seed = deriveSeed(resolvedSeed, fightNumber);
      try { summaries.push(fightSummary(fightNumber, runSeeded(selection, seed))); }
      catch (error) { errors.push({ fight_number: fightNumber, seed, error_type: error?.name || "Error", message: error?.message || String(error) }); }
      if (onProgress && (fightNumber === count || fightNumber % 25 === 0)) onProgress(fightNumber, count);
      if (fightNumber % 100 === 0) await new Promise((resolve) => window.setTimeout(resolve, 0));
    }
    const valid = summaries.length, heroes = summaries.filter((item) => item.outcome === "heroes_win").length;
    const monsters = summaries.filter((item) => item.outcome === "monsters_win").length, draws = summaries.filter((item) => item.outcome === "draw").length;
    const fastest = summaries.reduce((best, item) => !best || item.rounds < best.rounds ? item : best, null);
    const longest = summaries.reduce((best, item) => !best || item.rounds > best.rounds ? item : best, null);
    return {
      batch_seed: resolvedSeed, selection: structuredClone(selection), requested_fights: count, valid_fights: valid, engine_errors: errors.length,
      heroes_wins: heroes, monsters_wins: monsters, draws, heroes_win_rate: rate(heroes, valid), monsters_win_rate: rate(monsters, valid), draw_rate: rate(draws, valid),
      average_rounds: valid ? Number((summaries.reduce((sum, item) => sum + item.rounds, 0) / valid).toFixed(2)) : 0,
      fastest_fight_number: fastest?.fight_number || null, longest_fight_number: longest?.fight_number || null, fights: summaries, errors,
    };
  }

  window.IRON_PIT_BROWSER_TURBO = { MAX_FIGHTS, deriveSeed, runBatch, runSeeded, seededDice };
})();