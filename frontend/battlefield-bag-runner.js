(() => {
  "use strict";
  // Runner state: {running, stopRequested}, owned by the player-facing UI.
  // Only normal ready catalog cards are queued; the homebrew bag is
  // compiled using the same editor and passed to the real matchup loader.
  const EDITIONS = ["2014", "2024"];
  const BASE_SEED = 12345;
  const el = id => document.getElementById(id);

  async function selectEdition(api, edition) {
    try {
      await api.ensureRuleset(edition, true);
      if (api.state.ruleset !== edition || api.state.catalog?.ruleset !== edition)
        throw new Error("Could not switch the real battlefield to " + edition + ".");
    } catch (error) {
      console.error("Battlefield gauntlet edition setup failed", {edition, error});
      throw error;
    }
  }

  async function plan(api) {
    try {
      const entries = [];
      for (const edition of EDITIONS) {
        await selectEdition(api, edition);
        const ready = api.state.catalog.heroes.filter(card =>
          card.ruleset === edition && card.kind === "character" &&
          card.coverage_status === "raw_ready" && card.runnable_template_id);
        if (!ready.length) throw new Error("No playable pregens for " + edition + ".");
        entries.push(...ready.sort((a, b) =>
          a.runnable_template_id.localeCompare(b.runnable_template_id)));
      }
      const identities = entries.map(card => card.ruleset + ":" + card.runnable_template_id);
      if (new Set(identities).size !== identities.length)
        throw new Error("Duplicate player-facing pregen in gauntlet roster.");
      return entries;
    } catch (error) {
      console.error("Could not build player-facing pregen gauntlet plan", error);
      throw error;
    }
  }

  function bagCard(edition) {
    try {
      const bag = window.IRON_PIT_TEST_PUNCHING_BAG;
      const compiler = window.IRON_PIT_CUSTOM_MONSTER_RUNTIME;
      if (!bag?.draft || !bag?.template || !compiler?.decorate)
        throw new Error("Standard homebrew Punching Bag compiler is missing.");
      const card = compiler.decorate(bag.draft(edition));
      const compiled = bag.template(edition);
      if (card.coverage_status !== "custom_ready" ||
          card.runnable_template_id !== compiled.id)
        throw new Error("Punching Bag did not compile as a playable custom card.");
      return {...card, compiled_template: compiled};
    } catch (error) {
      console.error("Could not prepare player-facing Punching Bag card", {edition, error});
      throw error;
    }
  }

  async function run(api, control, onProgress = () => {}) {
    if (api.state.fighting || (api.state.session && !api.state.session.complete))
      throw new Error("Finish the current player fight before starting Test All.");
    if (control.running) throw new Error("The Punching Bag gauntlet is already running.");
    control.running = true;
    control.stopRequested = false;
    api.state.fighting = true;
    let report = null;
    try {
      const entries = await plan(api);
      report = window.IRON_PIT_BATTLEFIELD_BAG_REPORT.create(entries.length, BASE_SEED);
      onProgress(report);
      for (let index = 0; index < entries.length; index += 1) {
        if (control.stopRequested) break;
        const entry = entries[index];
        const seed = window.IRON_PIT_BROWSER_TURBO.deriveSeed(BASE_SEED, index + 1);
        let session = null;
        try {
          if (api.state.ruleset !== entry.ruleset)
            await selectEdition(api, entry.ruleset);
          // Real player-facing cards, board slots, validation and selection.
          api.load([entry], [bagCard(entry.ruleset)],
            entry.name + " vs Punching Bag (seed " + seed + ")");
          const match = api.matchup();
          if (match.error || match.heroes.cards.length !== 1 ||
              match.monsters.cards.length !== 1)
            throw new Error(match.error || "Punching Bag fight must be 1v1.");
          const source = window.IRON_PIT_BROWSER_HEROES?.[entry.runnable_template_id];
          if (!source) throw new Error("The certified pregen template is unavailable.");
          const snapshot = JSON.stringify(source);
          const slotMap = {heroes: match.heroes.indexes, monsters: match.monsters.indexes};
          // Same execution/replay path that players invoke. Instant presentation
          // avoids hours of animation while retaining every real combat event.
          session = window.IRON_PIT_EXECUTION.resolveReplay(match.selection, seed, slotMap);
          await window.IRON_PIT_BATTLEFIELD_REPLAY.play(
            session.battle, slotMap, {instant: true});
          window.IRON_PIT_BATTLEFIELD_VIEW.writeLog(session.battle);
          window.IRON_PIT_BATTLEFIELD_VIEW.showResult(session.battle);
          api.state.hasRun = true;
          window.IRON_PIT_BATTLEFIELD_BAG_REPORT.record(
            report, entry, seed, session, snapshot);
        } catch (error) {
          console.error("Player-facing Punching Bag fight failed", {entry, seed, error});
          window.IRON_PIT_BATTLEFIELD_BAG_REPORT.failure(report, entry, seed, error, session);
        }
        el("status").textContent = "Punching Bag: " +
          report.completed + " / " + report.total + " pregens tested.";
        try { onProgress(report); }
        catch (error) { console.error("Could not refresh gauntlet progress", error); }
        await new Promise(resolve => window.requestAnimationFrame(resolve));
      }
      return window.IRON_PIT_BATTLEFIELD_BAG_REPORT.finish(
        report, control.stopRequested);
    } catch (error) {
      console.error("Player-facing Punching Bag suite aborted", error);
      if (report) window.IRON_PIT_BATTLEFIELD_BAG_REPORT.finish(report, true);
      throw error;
    } finally {
      api.state.fighting = false;
      api.state.session = null;
      control.running = false;
      api.updateControls();
    }
  }
  window.IRON_PIT_BATTLEFIELD_BAG_RUNNER = {plan, bagCard, run};
})();