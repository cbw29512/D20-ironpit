(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const heroRoster = () => Object.values(window.IRON_PIT_BROWSER_HEROES || {});
  const monsterRoster = edition => Object.values(edition === "2014" ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {} : window.IRON_PIT_BROWSER_MONSTERS || {});
  let report = null;
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
  function paintCards(side) {
    const selected = $(side).value;
    const source = side === "hero" ? heroRoster() : monsterRoster($("edition").value);
    const query = $(side + "-search").value.trim().toLowerCase();
    const entries = unique(source.filter(row => row.ruleset === $("edition").value))
      .filter(row => [row.name, row.id, row.class_id, row.level, row.challenge_rating, row.cr]
        .some(value => String(value ?? "").toLowerCase().includes(query)));
    const target = $(side + "-cards");
    target.replaceChildren();
    for (const item of entries) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "pick-card";
      button.setAttribute("aria-pressed", String(item.id === selected));
      const name = document.createElement("strong");
      name.textContent = item.name || item.id;
      const info = document.createElement("small");
      info.textContent = side === "hero"
        ? [item.class_id, item.level != null ? "Level " + item.level : ""].filter(Boolean).join(" · ")
        : [item.challenge_rating != null ? "CR " + item.challenge_rating : item.cr != null ? "CR " + item.cr : "", item.armor_class != null ? "AC " + item.armor_class : ""].filter(Boolean).join(" · ");
      button.append(name, info);
      button.addEventListener("click", () => {
        $(side).value = item.id;
        paintCards(side);
      });
      target.append(button);
    }
    if (!entries.length) target.textContent = "No matching certified cards.";
  }
  function populate() {
    const edition = $("edition").value;
    fill("hero", heroRoster().filter(row => row.ruleset === edition));
    fill("monster", monsterRoster(edition).filter(row => row.ruleset === edition));
    $("status").textContent = `Loaded ${$("hero").options.length} pregens and ${$("monster").options.length} monsters for ${edition}.`;
    paintCards("hero"); paintCards("monster");
  }
  function fight(selection, seed) {
    return window.IRON_PIT_BROWSER_TURBO.runSeeded(selection,seed).battle;
  }
  function selection() {
    const edition = $("edition").value;
    if (!$("hero").value || !$("monster").value) throw new Error("Both teams require a certified card.");
    return {ruleset: edition, hero_ids: Array(integer("hero-count", 1, 6)).fill($("hero").value),
      monster_ids: Array(integer("monster-count", 1, 6)).fill($("monster").value)};
  }
  function signature(battle) {
    return window.IRON_PIT_BATTLE_LAB.fingerprint(battle);
  }
  function observed(events) {
    const groups = {event_types: {}, feature_ids: {}, applied_conditions: {}, damage_types: {}};
    const increment = (group, value) => { if (typeof value === "string" && value) group[value] = (group[value] || 0) + 1; };
    for (const event of events) {
      increment(groups.event_types, event.event_type);
      increment(groups.feature_ids, event.feature_id);
      for (const condition of event.applied_condition_ids || []) increment(groups.applied_conditions, condition);
      for (const component of event.damage_components || []) increment(groups.damage_types, component.damage_type);
    }
    return groups;
  }
  function cardSnapshot(selection) {
    const heroes = window.IRON_PIT_BROWSER_HEROES || {};
    const monsters = selection.ruleset === "2014" ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {} : window.IRON_PIT_BROWSER_MONSTERS || {};
    return JSON.stringify({heroes:selection.hero_ids.map(id => heroes[id]),monsters:selection.monster_ids.map(id => monsters[id])});
  }
  function execute(entries, repeat) {
    const results = [];
    for (const entry of entries) {
      try {
        const start = performance.now(), before = cardSnapshot(entry.selection);
        const battle = fight(entry.selection, entry.seed);
        const stable = repeat ? signature(battle) === signature(fight(entry.selection, entry.seed)) : null;
        const cards_unchanged = before === cardSnapshot(entry.selection);
        results.push({selection:entry.selection,seed:entry.seed,cards_unchanged,outcome:battle.outcome,rounds:battle.rounds,
          events:battle.events.length,observed:observed(battle.events),stable,ms:Math.round(performance.now()-start),log:battle.events});
      } catch (error) { results.push({selection:entry.selection,seed:entry.seed,error:String(error.message || error)}); }
    }
    report = {generated_at:new Date().toISOString(),engine:"IRON_PIT_BROWSER_ENGINE.runEncounter",coverage_kind:"observed events only; not RAW correctness",results};
    const failed = results.filter(row => row.error || row.stable === false || row.cards_unchanged === false).length;
    $("status").textContent = `${results.length} runs; ${failed} engine errors, replay mismatches or card mutations.`;
    $("summary").textContent = `${results.filter(row => row.outcome === "heroes_win").length} hero wins, ${results.filter(row => row.outcome === "monsters_win").length} monster wins, ${results.filter(row => row.outcome === "draw").length} draws.`;
    const table = document.createElement("table");
    const head = document.createElement("tr");
    for (const key of ["Seed","Heroes","Monsters","Outcome / Error","Rounds","Events","Replay","Cards unchanged"]) {
      const th = document.createElement("th"); th.textContent=key; head.append(th);
    }
    table.append(head);
    results.forEach(row => {
      const tr=document.createElement("tr");
      for (const value of [row.seed,row.selection.hero_ids.length,row.selection.monster_ids.length,row.error || row.outcome,row.rounds ?? "—",row.events ?? "—",row.stable === null || row.stable === undefined ? "Not checked" : row.stable ? "PASS" : "FAIL",row.cards_unchanged === undefined ? "—" : row.cards_unchanged ? "PASS" : "FAIL"]) {
        const td=document.createElement("td"); td.textContent=String(value); tr.append(td);
      }
      tr.addEventListener("click",()=>{$("events").textContent=JSON.stringify(row.log || row.error,null,2);});
      table.append(tr);
    });
    $("results").replaceChildren(table);
    const coverage = document.createElement("pre");
    coverage.textContent = JSON.stringify(results.reduce((totals,row) => {
      for (const [group,counts] of Object.entries(row.observed || {})) for (const [key,count] of Object.entries(counts)) totals[group][key]=(totals[group][key] || 0)+count;
      return totals;
    },{event_types:{},feature_ids:{},applied_conditions:{},damage_types:{}}),null,2);
    $("results").append(coverage);
    $("events").textContent = JSON.stringify(results[0]?.log || results[0]?.error || [], null, 2);
    $("download").disabled=false;
  }
  function guarded(run) {
    try {run();} catch (error) {$("status").textContent="Test configuration error: "+String(error.message || error);}
  }
  $("edition").addEventListener("change",populate);
  for (const side of ["hero","monster"]) {
    $(side).addEventListener("change", () => paintCards(side));
    $(side + "-search").addEventListener("input", () => paintCards(side));
  }
  $("quick-fight").addEventListener("click", () => guarded(() => {
    execute([{selection:selection(),seed:integer("seed",1,4294967295)}], true);
    $("events").scrollIntoView({behavior:"smooth",block:"start"});
  }));

  $("fight").addEventListener("click",()=>guarded(()=>{
    const base=selection(), count=integer("runs",1,100), seed=integer("seed",1,4294967295);
    if (seed + count - 1 > 0xffffffff) throw new RangeError("Seed range exceeds 32-bit dice limit; choose a lower starting seed.");
    execute(Array.from({length:count},(_,i)=>({selection:base,seed:seed+i})),false);
  }));
  $("repeat").addEventListener("click",()=>guarded(()=>{
    execute([{selection:selection(),seed:integer("seed",1,4294967295)}],true);
  }));
  $("matrix").addEventListener("click",()=>guarded(()=>{
    const edition=$("edition").value, seed=integer("seed",1,4294967295);
    const heroes=unique(heroRoster().filter(row=>row.ruleset===edition));
    const monsters=unique(monsterRoster(edition).filter(row=>row.ruleset===edition));
    const offset=integer("matrix-offset",0,Math.max(0,heroes.length*monsters.length-1));
    const size=integer("matrix-size",1,100);
    const entries=Array.from({length:Math.min(size,heroes.length*monsters.length-offset)},(_,i)=>{
      const n=offset+i,h=heroes[Math.floor(n/monsters.length)],m=monsters[n%monsters.length];
      return {selection:{ruleset:edition,hero_ids:[h.id],monster_ids:[m.id]},seed};
    });
    execute(entries,true);
    $("status").textContent += ` Matrix matchups ${offset+1}–${offset+entries.length} of ${heroes.length*monsters.length}.`;
  }));
  $("download").addEventListener("click",()=>{
    if (!report) return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:"application/json"}));
    const anchor=document.createElement("a"); anchor.href=url;anchor.download="iron-pit-engine-test-report.json";anchor.click();
    URL.revokeObjectURL(url);
  });
  populate();
})();
