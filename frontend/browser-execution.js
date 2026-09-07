(() => {
  "use strict";

  const engine = () => window.IRON_PIT_BROWSER_ENGINE;
  const dice = () => window.IRON_PIT_DICE;
  const lab = () => window.IRON_PIT_BATTLE_LAB;
  const replayView = () => window.IRON_PIT_BATTLEFIELD_REPLAY;
  const turbo = () => window.IRON_PIT_BROWSER_TURBO;

  function snapshot(session) {
    return {
      mode: session.mode,
      event_index: session.eventIndex,
      event_count: session.battle.events?.length || 0,
      started: session.started,
      complete: session.complete,
      seed: session.seed,
    };
  }

  function createSession({ battle, slotMap, rolls = [], diagnosticId = null, mode, seed = null }) {
    if (!battle || !slotMap) throw new Error("Execution session requires a battle and slot map.");
    const session = {
      battle,
      slotMap: structuredClone(slotMap),
      rolls: structuredClone(rolls),
      diagnosticId,
      mode,
      seed,
      eventIndex: 0,
      started: false,
      complete: false,
    };

    session.begin = async () => {
      try {
        if (!session.started) {
          replayView().bindBattle(session.battle, session.slotMap);
          session.started = true;
          if (!(session.battle.events || []).length) {
            replayView().syncFinal(session.battle);
            session.complete = true;
          }
        }
        return snapshot(session);
      } catch (error) {
        console.error("Iron Pit execution session could not start", error);
        throw error;
      }
    };

    session.step = async () => {
      try {
        await session.begin();
        if (session.complete) return snapshot(session);
        const event = session.battle.events[session.eventIndex];
        await replayView().eventStep(event);
        session.eventIndex += 1;
        if (session.eventIndex >= session.battle.events.length) {
          replayView().syncFinal(session.battle);
          session.complete = true;
        }
        return snapshot(session);
      } catch (error) {
        console.error("Iron Pit execution step failed", error);
        throw error;
      }
    };

    session.watch = async () => {
      try {
        await session.begin();
        while (!session.complete) await session.step();
        return snapshot(session);
      } catch (error) {
        console.error("Iron Pit watch execution failed", error);
        throw error;
      }
    };

    session.state = () => snapshot(session);
    return session;
  }

  function resolveLive(selection, slotMap) {
    try {
      dice().clearHistory();
      const battle = engine().runEncounter(structuredClone(selection));
      const rolls = dice().getHistory();
      const diagnosticId = lab().diagnosticId(selection.hero_ids, selection.monster_ids, rolls);
      return createSession({ battle, slotMap, rolls, diagnosticId, mode: "live" });
    } catch (error) {
      console.error("Live Iron Pit resolution failed", error);
      throw error;
    }
  }

  function resolveReplay(selection, seed, slotMap) {
    try {
      const replay = turbo().runSeeded(selection, seed);
      return createSession({
        battle: replay.battle,
        slotMap,
        rolls: replay.rolls,
        diagnosticId: replay.diagnostic_id,
        mode: "replay",
        seed: replay.seed,
      });
    } catch (error) {
      console.error(`Replay resolution failed for seed ${seed}`, error);
      throw error;
    }
  }

  async function runTurbo(selection, fights, batchSeed = null, onProgress = null) {
    try {
      return await turbo().runBatch(selection, fights, batchSeed, onProgress);
    } catch (error) {
      console.error("Turbo execution failed", error);
      throw error;
    }
  }

  window.IRON_PIT_EXECUTION = { createSession, resolveLive, resolveReplay, runTurbo };
})();
