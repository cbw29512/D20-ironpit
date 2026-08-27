(() => {
  "use strict";

  const meleeButton = document.querySelector("#fight-button");
  const rangedButton = document.querySelector("#ranged-button");
  const buttons = [meleeButton, rangedButton];
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };

  function setButtonsDisabled(disabled) {
    try { for (const button of buttons) button.disabled = disabled; }
    catch (error) { console.error("Button state update failed", error); }
  }

  async function loadRoster(view) {
    try {
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/roster/demo`);
      if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
      view.hydrateRoster(await response.json());
      view.resetArena("Ready — choose a starting distance.", 5);
    } catch (error) {
      console.error("Roster load failed", error);
      view.resetArena("Roster API unavailable. A battle request will retry the API.", 5);
    }
  }

  async function startFight(view, endpoint, fallbackDistance) {
    try {
      setButtonsDisabled(true);
      view.resetArena("Requesting battle...", fallbackDistance);
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}${endpoint}`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      const battle = await response.json();
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena("Rolling initiative...", battle.battlefield.starting_distance_ft);
      await view.replay(battle.events);
      view.setStatus(
        battle.winner_name
          ? `${battle.winner_name} wins in round ${battle.rounds}!`
          : "The duel is a draw."
      );
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus("Battle failed. Check the FastAPI deployment and CORS settings.");
    } finally {
      setButtonsDisabled(false);
    }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    meleeButton.addEventListener("click", () => startFight(view, "/api/battles/demo", 5));
    rangedButton.addEventListener("click", () => startFight(view, "/api/battles/demo-ranged", 90));
    loadRoster(view);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
