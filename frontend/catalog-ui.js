(() => {
  "use strict";

  function createIronPitCatalogUI(characterSelect, monsterSelect) {
    let characters = new Map();
    let monsters = new Map();

    function fillSelect(select, entries) {
      try {
        select.replaceChildren();
        for (const entry of entries) {
          const combatant = entry.combatant;
          const option = document.createElement("option");
          option.value = combatant.id;
          option.textContent = combatant.level
            ? `${combatant.name} · ${combatant.archetype} ${combatant.level}`
            : `${combatant.name} · CR ${combatant.challenge_rating}`;
          option.disabled = entry.battle_ready === false;
          select.append(option);
        }
      } catch (error) {
        console.error("Catalog selector population failed", error);
        throw error;
      }
    }

    function hydrate(catalog) {
      try {
        characters = new Map(catalog.characters.map((entry) => [entry.combatant.id, entry]));
        monsters = new Map(catalog.monsters.map((entry) => [entry.combatant.id, entry]));
        fillSelect(characterSelect, catalog.characters);
        fillSelect(monsterSelect, catalog.monsters);
      } catch (error) {
        console.error("Catalog UI hydration failed", error);
        throw error;
      }
    }

    function selectedRoster() {
      try {
        const fighter = characters.get(characterSelect.value)?.combatant;
        const monster = monsters.get(monsterSelect.value)?.combatant;
        if (!fighter || !monster) throw new Error("A battle-ready matchup is not selected.");
        return { fighter, monster };
      } catch (error) {
        console.error("Selected roster lookup failed", error);
        throw error;
      }
    }

    function selectedIds() {
      const roster = selectedRoster();
      return { characterId: roster.fighter.id, monsterId: roster.monster.id };
    }

    return { hydrate, selectedRoster, selectedIds };
  }

  window.createIronPitCatalogUI = createIronPitCatalogUI;
})();
