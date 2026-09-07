(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const execution = () => window.IRON_PIT_EXECUTION;
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const lab = () => window.IRON_PIT_BATTLE_LAB;
  const turboView = () => window.IRON_PIT_TURBO_VIEW;

  function slotMap(match) {
    return { heroes: match.heroes.indexes, monsters: match.monsters.indexes };
  }

  function syncControls(state) {
    try {
      const active = Boolean(state.session && !state.session.complete);
      el("step-session-actions").hidden = !active;
      el("next-event-button").disabled = state.fighting || !active;
      el("watch-rest-button").disabled = state.fighting || !active;
      const replayStep = el("turbo-replay-step-button");
      if (replayStep) replayStep.disabled = state.fighting || !state.turboBatch;
    } catch (error) {
      console.error("Execution controls could not be synchronized", error);
      throw error;
    }
  }

  function writeProgress(session) {
    const events = session.battle.events.slice(0, session.eventIndex);
    view().writeLog({ events });
  }

  function finishSession(state, session, prefix = null) {
    try {
      view().writeLog(session.battle); view().showResult(session.battle); state.hasRun = true;
      if (prefix) {
        el("lab-summary").textContent = `${prefix} · ${session.rolls.length} deterministic dice rolls.`;
      } else {
        el("lab-summary").textContent = lab().summary(session.battle, session.rolls, session.diagnosticId);
      }
    } catch (error) {
      console.error("Completed execution could not be presented", error);
      throw error;
    }
  }

  async function startLive(api, mode) {
    const match = api.matchup(); if (match.error) { el("status").textContent = match.error; return; }
    try {
      api.state.session = null; api.state.fighting = true; api.render(); api.clearResult();
      el("status").textContent = mode === "step" ? "Resolving fight for Step Mode…" : "Rolling initiative…";
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const session = execution().resolveLive(match.selection, slotMap(match)); api.state.session = session;
      if (mode === "step") {
        await session.begin(); el("status").textContent = `Step Mode ready · 0 / ${session.battle.events.length} events.`;
      } else {
        await session.watch(); finishSession(api.state, session);
      }
    } catch (error) {
      console.error("Live execution failed", error);
      el("status").textContent = "Fight stopped because a required RAW mechanic is unsupported or the battle engine failed.";
    } finally { api.state.fighting = false; api.updateControls(); syncControls(api.state); }
  }

  async function nextEvent(api) {
    const session = api.state.session; if (!session || session.complete) return;
    try {
      api.state.fighting = true; api.updateControls(); syncControls(api.state);
      const status = await session.step(); writeProgress(session);
      if (status.complete) finishSession(api.state, session, session.mode === "replay" ? `Replay seed ${session.seed}` : null);
      else el("status").textContent = `Step Mode · event ${status.event_index} / ${status.event_count}.`;
    } catch (error) {
      console.error("Step execution failed", error); el("status").textContent = `Step execution failed: ${error.message}`;
    } finally { api.state.fighting = false; api.updateControls(); syncControls(api.state); }
  }

  async function watchRest(api) {
    const session = api.state.session; if (!session || session.complete) return;
    try {
      api.state.fighting = true; api.updateControls(); syncControls(api.state);
      await session.watch(); finishSession(api.state, session, session.mode === "replay" ? `Replay seed ${session.seed}` : null);
    } catch (error) {
      console.error("Watch-rest execution failed", error); el("status").textContent = `Watch execution failed: ${error.message}`;
    } finally { api.state.fighting = false; api.updateControls(); syncControls(api.state); }
  }

  async function runTurbo(api) {
    const match = api.matchup(); if (match.error) { el("status").textContent = match.error; return; }
    try {
      const count = turboView().fightCount(); api.state.session = null; api.state.fighting = true;
      turboView().hide(); api.render(); api.clearResult("Turbo Mode is running the full combat engine without animations.");
      el("status").textContent = `Turbo: 0 / ${count.toLocaleString()} fights`;
      api.state.turboBatch = await execution().runTurbo(match.selection, count, null, (done, total) => {
        el("status").textContent = `Turbo: ${done.toLocaleString()} / ${total.toLocaleString()} fights`;
      });
      turboView().render(api.state.turboBatch); el("status").textContent = `Turbo complete: ${api.state.turboBatch.valid_fights.toLocaleString()} valid fights.`;
    } catch (error) {
      console.error("Turbo execution failed", error); el("status").textContent = error.message || "Turbo Mode failed.";
    } finally { api.state.fighting = false; api.updateControls(); syncControls(api.state); }
  }

  async function replayTurbo(api, mode) {
    if (!api.state.turboBatch) return;
    const match = api.matchup(); if (match.error) { el("status").textContent = match.error; return; }
    let fightNumber = null;
    try {
      fightNumber = turboView().replayNumber(api.state.turboBatch);
      const record = turboView().findFight(api.state.turboBatch, fightNumber) || api.state.turboBatch.errors.find((item) => item.fight_number === fightNumber);
      if (!record) throw new Error(`Fight #${fightNumber} was not found.`);
      api.state.fighting = true; api.render(); api.clearResult();
      const session = execution().resolveReplay(api.state.turboBatch.selection, record.seed, slotMap(match)); api.state.session = session;
      el("status").textContent = `${mode === "step" ? "Step" : "Watch"} replay #${fightNumber} · seed ${record.seed}.`;
      if (mode === "step") await session.begin();
      else { await session.watch(); finishSession(api.state, session, `Turbo fight #${fightNumber} replay · seed ${record.seed}`); }
    } catch (error) {
      console.error("Turbo replay failed", error);
      el("status").textContent = fightNumber ? `Turbo fight #${fightNumber} reproduced an engine error: ${error.message}` : error.message;
    } finally { api.state.fighting = false; api.updateControls(); syncControls(api.state); }
  }

  function install(api) {
    el("fight-button").addEventListener("click", () => startLive(api, "watch"));
    el("rerun-button").addEventListener("click", () => startLive(api, "watch"));
    el("step-fight-button").addEventListener("click", () => startLive(api, "step"));
    el("next-event-button").addEventListener("click", () => nextEvent(api));
    el("watch-rest-button").addEventListener("click", () => watchRest(api));
    el("turbo-button").addEventListener("click", () => runTurbo(api));
    el("turbo-replay-button").addEventListener("click", () => replayTurbo(api, "watch"));
    el("turbo-replay-step-button").addEventListener("click", () => replayTurbo(api, "step"));
    syncControls(api.state);
  }

  window.IRON_PIT_BATTLE_ACTIONS = { install, syncControls };
})();
