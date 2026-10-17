(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  let nodes = new Map();

  function setup(battle, recipe, seed) {
    nodes = new Map();
    $("arena-title").textContent = (recipe.title || recipe.id || "Roster fight") + " · " + recipe.ruleset + " · seed " + seed;
    $("arena-teams").replaceChildren(); $("arena-log").replaceChildren();
    $("arena-event").textContent = "Preparing fight…";
    for (const [side, members] of [["Heroes", battle.setup.heroes], ["Monsters", battle.setup.monsters]]) {
      const section = document.createElement("div");
      section.className = "team";
      const title = document.createElement("h3"); title.textContent = side; section.append(title);
      for (const member of members) {
        const node = document.createElement("div"); node.className = "fighter";
        const name = document.createElement("strong"); name.textContent = member.state.template.name;
        const hp = document.createElement("progress");
        const maximum = Number(member.state.template.max_hp) || Math.max(1, Number(member.state.current_hp));
        hp.max = maximum; hp.value = maximum;
        const label = document.createElement("small"); label.textContent = maximum + " / " + maximum + " HP";
        node.append(name, hp, label); section.append(node);
        nodes.set(member.combatant_id, { node, hp, label, maximum });
      }
      $("arena-teams").append(section);
    }
  }

  function apply(event) {
    const line = document.createElement("li");
    const title = document.createElement("strong");
    title.textContent = "Round " + event.round_number + ": " + (event.event_type || "event");
    const detail = document.createElement("p");
    detail.textContent = event.description || event.event_type || "Combat event";
    line.append(title, detail);
    $("arena-log").append(line);
    $("arena-event").textContent = line.textContent;
    $("arena-log").scrollTop = $("arena-log").scrollHeight;
    const target = nodes.get(event.target_id);
    if (target && typeof event.hp_after === "number") {
      const hp = Math.max(0, Math.min(target.maximum, event.hp_after));
      target.hp.value = hp; target.label.textContent = hp + " / " + target.maximum + " HP";
      target.node.classList.toggle("fallen", hp === 0);
    }
    while ($("arena-log").children.length > 300) $("arena-log").firstElementChild.remove();
  }

  async function play(battle, recipe, seed) {
    setup(battle, recipe, seed);
    for (const event of battle.events) {
      apply(event);
      const ms = Number($("speed").value);
      if (!Number.isFinite(ms) || ms < 0) throw Error("Invalid spectator playback delay.");
      await sleep(ms);
    }
  }
  window.IRON_PIT_BETA_SPECTATOR = { play, setup, apply };
})();