(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const records = [];
  const MAX_VISIBLE = 80;
  const take = (value) => JSON.stringify(value, (key, data) => key === "item" || key === "summary" || key === "body" ? undefined : data, 2);
  function record(battle, selection, seed, failure = null) {
    const entry = { number: records.length + 1, ruleset: selection.ruleset,
      heroes: [...selection.hero_ids], monsters: [...selection.monster_ids],
      seed, outcome: battle?.outcome || "ERROR", rounds: battle?.rounds || 0,
      events: battle?.events || [], failure };
    records.push(entry);
    const holder = $("beta-history"); if (!holder) return;
    const item = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "#" + entry.number + " · " + entry.ruleset + " · " +
      entry.heroes.join(", ") + " vs " + entry.monsters.join(", ") + " · " +
      entry.outcome + " · " + entry.rounds + " rounds · " +
      entry.events.length + " events · seed " + seed + (failure ? " · " + failure : "");
    item.append(summary);
    item.addEventListener("toggle", () => {
      if (!item.open || item.childElementCount > 1) return;
      const body = document.createElement("div");
      body.className = "beta-history-events";
      for (const event of entry.events) {
        body.append(window.IRON_PIT_BATTLEFIELD_VIEW.eventRow(event));
      }
      item.append(body);
    });
    holder.append(item);
    while (holder.childElementCount > MAX_VISIBLE) holder.firstElementChild.remove();
    $("beta-history-count").textContent = records.length + " fights recorded (" +
      Math.min(records.length, MAX_VISIBLE) + " most recent shown). Complete history in download.";
  }
  let active = null;
  function begin(selection, seed) {
    active = { number: records.length + 1, ruleset: selection.ruleset,
      heroes: [...selection.hero_ids], monsters: [...selection.monster_ids],
      seed, outcome: "IN PROGRESS", rounds: 0, events: [], failure: null };
    records.push(active);
    const holder = $("beta-history");
    const item = document.createElement("details"), summary = document.createElement("summary");
    item.open = true;
    summary.textContent = "Fight #" + active.number + " · " + selection.ruleset +
      " · seed " + seed + " · IN PROGRESS";
    const body = document.createElement("div");
    body.className = "beta-history-events";
    item.append(summary, body); holder.append(item);
    active.item = item; active.summary = summary; active.body = body;
    while (holder.childElementCount > MAX_VISIBLE) holder.firstElementChild.remove();
    $("beta-history-count").textContent = records.length + " fights recorded; complete history retained.";
  }
  function step(event) {
    if (!active) return;
    active.events.push(event);
    active.rounds = Math.max(active.rounds, Number(event.round_number) || 0);
    active.body.append(window.IRON_PIT_BATTLEFIELD_VIEW.eventRow(event));
    active.body.scrollTop = active.body.scrollHeight;
    active.summary.textContent = "Fight #" + active.number + " · " + active.ruleset +
      " · seed " + active.seed + " · round " + active.rounds +
      " · " + active.events.length + " events · IN PROGRESS";
  }
  function finish(battle) {
    if (!active) return;
    active.outcome = battle.outcome;
    active.rounds = battle.rounds;
    active.summary.textContent = "Fight #" + active.number + " · " + active.ruleset +
      " · seed " + active.seed + " · " + active.outcome +
      " · " + active.rounds + " rounds · " + active.events.length + " events";
    active.item.open = false;
    active = null;
  }
  function download() {
    const data = new Blob([take({ generated: new Date().toISOString(), fights: records })],
      { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(data);
    link.download = "ironpit-beta-complete-fight-log.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 5000);
  }
  $("beta-history-download")?.addEventListener("click", download);
  window.IRON_PIT_BETA_LOG = { record, begin, step, finish, download, entries: () => records };
})();
