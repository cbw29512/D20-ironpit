(() => {
  "use strict";

  const el = (id) => document.getElementById(id);

  function fightCount() {
    try {
      const input = el("turbo-count"), value = Number(input?.value);
      if (!Number.isInteger(value) || value < 1 || value > 10000) throw new RangeError("Turbo fights must be between 1 and 10,000.");
      return value;
    } catch (error) { console.error("Invalid Turbo fight count", error); throw error; }
  }

  function replayNumber(batch) {
    try {
      const value = Number(el("turbo-fight-number")?.value);
      if (!Number.isInteger(value) || value < 1 || value > batch.requested_fights) throw new RangeError(`Fight number must be 1-${batch.requested_fights}.`);
      return value;
    } catch (error) { console.error("Invalid Turbo replay fight number", error); throw error; }
  }

  function hide() {
    const panel = el("turbo-panel"); if (panel) panel.hidden = true;
  }

  function render(batch) {
    try {
      const panel = el("turbo-panel"), errors = batch.engine_errors;
      el("turbo-result-title").textContent = `${batch.requested_fights.toLocaleString()} FIGHT TURBO`;
      el("turbo-result-summary").textContent = `${batch.valid_fights.toLocaleString()} valid · ${errors} engine error${errors === 1 ? "" : "s"}`;
      el("turbo-heroes").textContent = `Heroes ${batch.heroes_wins.toLocaleString()} · ${batch.heroes_win_rate}%`;
      el("turbo-monsters").textContent = `Monsters ${batch.monsters_wins.toLocaleString()} · ${batch.monsters_win_rate}%`;
      el("turbo-draws").textContent = `Draws ${batch.draws.toLocaleString()} · ${batch.draw_rate}%`;
      el("turbo-rounds").textContent = `Average ${batch.average_rounds} rounds`;
      el("turbo-notables").textContent = `Fastest #${batch.fastest_fight_number ?? "—"} · Longest #${batch.longest_fight_number ?? "—"} · Batch seed ${batch.batch_seed}`;
      const input = el("turbo-fight-number"); input.max = String(batch.requested_fights); input.value = String(batch.fastest_fight_number || batch.errors[0]?.fight_number || 1);
      el("turbo-replay-button").disabled = false;
      const errorBox = el("turbo-error-summary"); errorBox.hidden = errors === 0;
      errorBox.textContent = errors ? `${errors} fight${errors === 1 ? "" : "s"} hit an engine-rule error and were excluded from the ratios. Enter that fight number to reproduce it.` : "";
      panel.hidden = false;
    } catch (error) { console.error("Turbo results could not be rendered", error); throw error; }
  }

  function findFight(batch, fightNumber) {
    return batch.fights.find((item) => item.fight_number === fightNumber) || null;
  }

  window.IRON_PIT_TURBO_VIEW = { fightCount, findFight, hide, render, replayNumber };
})();