(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const R = () => window.IRON_PIT_BROWSER_FORMATION_ROWS;

  function fillList(node, names) {
    if (!node) return;
    node.replaceChildren();
    if (!names.length) {
      const empty = document.createElement("li");
      empty.className = "formation-empty";
      empty.textContent = "—";
      node.append(empty);
      return;
    }
    for (const name of names) {
      const item = document.createElement("li");
      item.textContent = name;
      node.append(item);
    }
  }

  function rowOf(member, events) {
    let row = member.state.initial_formation_row || member.state.formation_row;
    for (const event of events || []) {
      if (event.feature_id === "formation-step-up" && event.actor_id === member.combatant_id) row = "front";
    }
    return row === "back" ? "back" : "front";
  }

  function namesFor(members, row, events) {
    return members
      .filter((member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0)
      .filter((member) => rowOf(member, events) === row)
      .map((member) => member.state.template.name);
  }

  function renderBattle(setup, events) {
    try {
      if (!setup) return;
      fillList(el("hero-front-row"), namesFor(setup.heroes, "front", events));
      fillList(el("hero-back-row"), namesFor(setup.heroes, "back", events));
      fillList(el("monster-front-row"), namesFor(setup.monsters, "front", events));
      fillList(el("monster-back-row"), namesFor(setup.monsters, "back", events));
    } catch (error) {
      console.error("Formation board could not render battle rows", { error });
      throw error;
    }
  }

  function renderPreview(state) {
    try {
      const runtime = (card, side) => {
        if (!card?.runnable_template_id) return null;
        if (card.ruleset === "2014") {
          return side === "heroes"
            ? window.IRON_PIT_BROWSER_HEROES?.[card.runnable_template_id]
            : window.IRON_PIT_BROWSER_MONSTERS_2014?.[card.runnable_template_id];
        }
        return side === "heroes"
          ? window.IRON_PIT_BROWSER_HEROES?.[card.runnable_template_id]
          : window.IRON_PIT_BROWSER_MONSTERS?.[card.runnable_template_id];
      };
      const toMember = (card, side, index) => {
        const template = runtime(card, side) || { name: card.name, attacks: [], primary_attack_id: null };
        return {
          combatant_id: `${side}-${index}`,
          state: { template, is_alive: true, is_dead: false, current_hp: 1, formation_row: null },
        };
      };
      const heroes = (state.heroSlots || []).filter(Boolean).map((card, index) => toMember(card, "heroes", index));
      const monsters = (state.monsterSlots || []).filter(Boolean).map((card, index) => toMember(card, "monsters", index));
      R()?.assignFormationRows(heroes);
      R()?.assignFormationRows(monsters);
      renderBattle({ heroes, monsters }, []);
    } catch (error) {
      console.error("Formation board could not render preview rows", { error });
      throw error;
    }
  }

  window.IRON_PIT_FORMATION_BOARD = { renderBattle, renderPreview };
})();
