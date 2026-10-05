(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const presets = () => window.IRON_PIT_COMBAT_PRESETS;
  const execution = () => window.IRON_PIT_EXECUTION;
  const view = () => window.IRON_PIT_BATTLEFIELD_VIEW;
  const replayView = () => window.IRON_PIT_BATTLEFIELD_REPLAY;
  const actions = () => window.IRON_PIT_BATTLE_ACTIONS;

  function slotMap(match) {
    return { heroes: match.heroes.indexes, monsters: match.monsters.indexes };
  }

  function outcomeLabel(battle) {
    if (battle.outcome === "heroes_win") return "HEROES WIN";
    if (battle.outcome === "monsters_win") return "MONSTERS WIN";
    return "DRAW";
  }

  function fillLog(battle) {
    try {
      const log = el("combat-review-log");
      if (!log) throw new Error("Combat review log is missing.");
      log.replaceChildren();
      for (const event of battle.events || []) log.append(view().eventRow(event));
    } catch (error) {
      console.error("Combat review log could not be rendered", error);
      throw error;
    }
  }

  function hide() {
    try {
      const dialog = el("combat-review");
      if (!dialog) return;
      if (typeof dialog.close === "function" && dialog.open) dialog.close();
      dialog.hidden = true;
    } catch (error) {
      console.error("Combat review dialog could not close", error);
      throw error;
    }
  }

  function open(recipe, session) {
    try {
      const dialog = el("combat-review");
      if (!dialog) throw new Error("Combat review dialog is missing.");
      const battle = session.battle;
      el("combat-review-title").textContent = recipe.title;
      el("combat-review-meta").textContent = `${outcomeLabel(battle)} · ${battle.rounds} round${battle.rounds === 1 ? "" : "s"} · recorded seed ${recipe.seed} · Look for: ${recipe.purpose}`;
      fillLog(battle);
      dialog.hidden = false;
      if (typeof dialog.showModal === "function" && !dialog.open) dialog.showModal();
    } catch (error) {
      console.error("Combat review dialog could not open", { recipe: recipe?.id, error });
      throw error;
    }
  }

  async function loadCombat(api) {
    const recipe = presets().selected();
    if (!recipe) {
      el("status").textContent = "Select a ready-made fight first.";
      return;
    }
    if (api.state.fighting || (api.state.session && !api.state.session.complete)) return;
    try {
      api.state.fighting = true;
      api.updateControls();
      el("status").textContent = `Loading ${recipe.title} recorded combat log…`;
      if (api.ensureRuleset) await api.ensureRuleset(recipe.ruleset);
      const cards = presets().resolve(recipe, api.state.catalog);
      api.load(cards.heroes, cards.monsters, `${recipe.title} loaded. Look for: ${recipe.purpose}`, recipe);
      const match = api.matchup();
      if (match.error) { el("status").textContent = match.error; return; }
      api.state.session = null;
      api.clearResult("Loading the recorded battle log…");
      const session = execution().resolveReplay(match.selection, recipe.seed, slotMap(match));
      session.started = true;
      session.complete = true;
      session.eventIndex = (session.battle.events || []).length;
      api.state.session = session;
      replayView()?.bindBattle?.(session.battle, session.slotMap);
      replayView()?.syncFinal?.(session.battle);
      view().writeLog(session.battle);
      view().showResult(session.battle);
      api.state.hasRun = true;
      el("lab-summary").textContent = `Review log · recorded seed ${recipe.seed} · ${session.rolls.length} dice rolls.`;
      open(recipe, session);
      el("status").textContent = `${recipe.title} recorded log ready for review.`;
    } catch (error) {
      console.error("Load Combat review failed", { recipe: recipe?.id, error });
      el("status").textContent = "Could not load the recorded combat log. See console for details.";
    } finally {
      api.state.fighting = false;
      api.updateControls();
      actions()?.syncControls?.(api.state);
    }
  }

  function install(api) {
    try {
      if (!el("load-combat-button") || !el("combat-review") || !el("combat-review-log")) {
        throw new Error("Load Combat review controls are missing.");
      }
      hide();
      el("load-combat-button").addEventListener("click", () => loadCombat(api));
      el("combat-review-close").addEventListener("click", () => hide());
      el("combat-review").addEventListener("click", (event) => {
        if (event?.target === el("combat-review")) hide();
      });
    } catch (error) {
      console.error("Load Combat review could not be installed", error);
      throw error;
    }
  }

  window.IRON_PIT_COMBAT_REVIEW = { hide, install, loadCombat, open };
})();
