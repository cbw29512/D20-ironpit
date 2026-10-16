(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const heroRoster = () => Object.values(window.IRON_PIT_BROWSER_HEROES || {});
  const monsterRoster = edition => Object.values(edition === "2014" ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {} : window.IRON_PIT_BROWSER_MONSTERS || {});
  let report = null;
  const dice = seed => {
    let state = seed >>> 0;
    const roll = sides => { state = (1664525 * state + 1013904223) >>> 0; return state % sides + 1; };
    return {roll, rollMany: (count, sides) => Array.from({length: count}, () => roll(sides))};
  };
  const integer = (id, low, high) => {
    const raw = Number($(id).value);
    if (!Number.isInteger(raw) || raw < low || raw > high) throw new Error(`${id} must be ${low}–${high}`);
    return raw;
  };
  const unique = values => [...new Map(values.map(row => [row.id, row])).values()].sort((a, b) => String(a.name).localeCompare(String(b.name)));
  function fill(id, entries) {
    const old = $(id).value;
    $(id).replaceChildren();
    for (const item of unique(entries)) {
      const option = document.createElement("option");
      option.value = item.id; option.textContent = `${item.name || item.id} — ${item.id}`;
      $(id).append(option);
    }
    if ([...$(id).options].some(option => option.value === old)) $(id).value = old;
  }
  function populate() {
    const edition = $("edition").value;
    fill("hero", heroRoster().filter(row => row.ruleset === edition));
    fill("monster", monsterRoster(edition).filter(row => row.ruleset === edition));
    $("status").textContent = `Loaded ${$("hero").options.length} pregens and ${$("monster").options.length} monsters for ${edition}.`;
  }
  function fight(selection, seed) {
    window.IRON_PIT_DICE = dice(seed);
    return window.IRON_PIT_BROWSER_ENGINE.runEncounter(selection);
  }
  function selection() {
    const edition = $("edition").value;
    if (!$("hero").value || !$("monster").value) throw new Error("Both teams require a certified card.");
    return {ruleset: edition, hero_ids: Array(integer("hero-count", 1, 6)).fill($("hero").value),
      monster_ids: Array(integer("monster-count", 1, 6)).fill($("monster").value)};
  }
  function signature(battle) {
    return JSON.stringify({outcome:battle.outcome,rounds:battle.rounds,events:battle.events});
  }
  function execute(entries, repeat) {
    const results = [];
    for (const entry of entries) {
      try {
        const start = performance.now();
        const battle = fight(entry.selection, entry.seed);
        const stable = repeat ? signature(battle) === signature(fight(entry.selection, entry.seed)) : null;
        results.push({selection:entry.selection,seed:entry.seed,outcome:battle.outcome,rounds:battle.rounds,
          events:battle.events.length,stable,ms:Math.round(performance.now()-start),log:battle.events});
      } catch (error) { results.push({selection:entry.selection,seed:entry.seed,error:String(error.message || error)}); }
    }
    report = {generated_at:new Date().toISOString(),engine:"IRON_PIT_BROWSER_ENGINE.runEncounter",results};
    const failed = results.filter(row => row.error || row.stable === false).length;
    $("status").textContent = `${results.length} runs; ${failed} errors/replay mismatches.`;
    $("summary").textContent = `${results.filter(row => row.outcome === "heroes_win").length} hero wins, ${results.filter(row => row.outcome === "monsters_win").length} monster wins, ${results.filter(row => row.outcome === "draw").length} draws.`;
    const table = document.createElement("table");
    const head = document.createElement("tr");
    for (const key of ["Seed","Heroes","Monsters","Outcome / Error","Rounds","Events","Replay"]) {
      const th = document.createElement("th"); th.textContent=key; head.append(th);
    }
    table.append(head);
    results.forEach(row => {
      const tr=document.createElement("tr");
      for (const value of [row.seed,row.selection.hero_ids.length,row.selection.monster_ids.length,row.error || row.outcome,row.rounds ?? "—",row.events ?? "—",row.stable === null || row.stable === undefined ? "Not checked" : row.stable ? "PASS" : "FAIL"]) {
        const td=document.createElement("td"); td.textContent=String(value); tr.append(td);
      }
      tr.addEventListener("click",()=>{$("events").textContent=JSON.stringify(row.log || row.error,null,2);});
      table.append(tr);
    });
    $("results").replaceChildren(table);
    $("events").textContent = JSON.stringify(results[0]?.log || results[0]?.error || [], null, 2);
    $("download").disabled=false;
  }
  function guarded(run) {
    try {run();} catch (error) {$("status").textContent="Test configuration error: "+String(error.message || error);}
  }
  $("edition").addEventListener("change",populate);
  $("fight").addEventListener("click",()=>guarded(()=>{
    const base=selection(), count=integer("runs",1,100), seed=integer("seed",1,4294967295);
    execute(Array.from({length:count},(_,i)=>({selection:base,seed:seed+i})),false);
  }));
  $("repeat").addEventListener("click",()=>guarded(()=>{
    execute([{selection:selection(),seed:integer("seed",1,4294967295)}],true);
  }));
  $("matrix").addEventListener("click",()=>guarded(()=>{
    const edition=$("edition").value, seed=integer("seed",1,4294967295);
    const heroes=unique(heroRoster().filter(row=>row.ruleset===edition)).slice(0,6);
    const monsters=unique(monsterRoster(edition).filter(row=>row.ruleset===edition)).slice(0,12);
    execute(heroes.flatMap(h=>monsters.map(m=>({selection:{ruleset:edition,hero_ids:[h.id],monster_ids:[m.id]},seed}))),true);
  }));
  $("download").addEventListener("click",()=>{
    if (!report) return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:"application/json"}));
    const anchor=document.createElement("a"); anchor.href=url;anchor.download="iron-pit-engine-test-report.json";anchor.click();
    URL.revokeObjectURL(url);
  });
  populate();
})();
