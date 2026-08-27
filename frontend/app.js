(() => {
  "use strict";

  const button = document.querySelector("#fight-button");
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };

  async function loadRoster(view) {
    try {
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/roster/demo`);
      if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
      view.hydrateRoster(await response.json());
      view.resetArena("Ready.");
    } catch (error) {
      console.error("Roster load failed", error);
      view.resetArena("Roster API unavailable. Enter the Pit will retry the battle API.");
    }
  }

  async function startFight(view) {
    try {
      button.disabled = true;
      view.resetArena("Requesting battle...");
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/battles/demo`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      const battle = await response.json();
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena();
      await view.replay(battle.events);
      view.setStatus(battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.");
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus("Battle failed. Check the FastAPI deployment and CORS settings.");
    } finally {
      button.disabled = false;
    }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    button.addEventListener("click", () => startFight(view));
    loadRoster(view);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
