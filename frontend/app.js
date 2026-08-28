(() => {
  "use strict";

  const fightButton = document.querySelector("#fight-button");
  const characterSelect = document.querySelector("#character-select");
  const monsterSelect = document.querySelector("#monster-select");
  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const previewRoster = window.IRON_PIT_TEST_ROSTER;
  const previewEngine = window.IRON_PIT_TEST_ENGINE;
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };
  let catalog = { characters: [], monsters: [] };

  function selectedCharacter() { return catalog.characters.find((item) => item.id === characterSelect.value); }
  function selectedMonster() { return catalog.monsters.find((item) => item.id === monsterSelect.value); }

  function setControlsDisabled(disabled) {
    try {
      fightButton.disabled = disabled;
      characterSelect.disabled = disabled;
      monsterSelect.disabled = disabled;
    } catch (error) { console.error("Control state update failed", error); }
  }

  function populateSelect(select, items, labeler) {
    select.innerHTML = "";
    for (const item of items) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = labeler(item);
      select.appendChild(option);
    }
  }

  function hydrateSelection(view, message = "Ready — press Fight.") {
    try {
      const fighter = selectedCharacter();
      const monster = selectedMonster();
      if (!fighter || !monster) throw new Error("Selected matchup is unavailable.");
      view.hydrateRoster({ fighter, monster });
      view.resetArena(message, 5);
      setControlsDisabled(false);
    } catch (error) { console.error("Matchup hydration failed", error); view.setStatus("Matchup could not be loaded."); }
  }

  async function loadRulesCoverage(rulesView) {
    try {
      const endpoint = apiBase ? `${apiBase}/api/rules/coverage` : "rules-coverage.json";
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`Rules coverage returned ${response.status}`);
      rulesView.render(await response.json());
    } catch (error) {
      console.error("Rules coverage load failed", error);
      rulesView.setError("Rules coverage could not be loaded.");
    }
  }

  async function loadCatalog(view) {
    try {
      if (apiBase) {
        const response = await fetch(`${apiBase}/api/test/roster`);
        if (!response.ok) throw new Error(`Test roster returned ${response.status}`);
        catalog = await response.json();
      } else {
        if (!previewRoster) throw new Error("Secure preview test roster is unavailable.");
        catalog = { characters: Object.values(previewRoster.characters), monsters: Object.values(previewRoster.monsters) };
      }
      populateSelect(characterSelect, catalog.characters, (item) => `${item.name} · ${item.archetype} ${item.level}`);
      populateSelect(monsterSelect, catalog.monsters, (item) => `${item.name} · CR ${item.challenge_rating}`);
      characterSelect.value = "aldric-vane-l1";
      monsterSelect.value = "srd-goblin-warrior";
      hydrateSelection(view, "Choose a matchup, then press Fight.");
    } catch (error) {
      console.error("Test roster load failed", error);
      view.resetArena("Test roster could not be loaded.", 5);
    }
  }

  async function requestBattle() {
    const characterId = characterSelect.value;
    const monsterId = monsterSelect.value;
    try {
      if (!apiBase) return previewEngine.buildAutomaticBattle(characterId, monsterId);
      const endpoint = `/api/test/fight/${encodeURIComponent(characterId)}/${encodeURIComponent(monsterId)}`;
      const response = await fetch(`${apiBase}${endpoint}`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      return await response.json();
    } catch (error) { console.error("Battle request failed", error); throw error; }
  }

  async function startFight(view) {
    try {
      setControlsDisabled(true);
      view.resetArena(apiBase ? "Requesting fight..." : "The monster chooses its opening approach...", 5);
      const battle = await requestBattle();
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena("Rolling initiative...", battle.battlefield.starting_distance_ft);
      await view.replay(battle.events);
      view.setStatus(battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.");
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus(apiBase ? "Battle failed. Check the FastAPI deployment." : "Secure preview battle failed.");
    } finally { setControlsDisabled(false); }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    const rulesView = window.createIronPitRulesView();
    characterSelect.addEventListener("change", () => hydrateSelection(view));
    monsterSelect.addEventListener("change", () => hydrateSelection(view));
    fightButton.addEventListener("click", () => startFight(view));
    setControlsDisabled(true);
    loadCatalog(view);
    loadRulesCoverage(rulesView);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
