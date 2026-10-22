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
  function populate() {
    const edition = $("edition").value;
    fill("hero", heroRoster().filter(row => row.ruleset === edition));
    fill("monster", monsterRoster(edition).filter(row => row.ruleset === edition));
    $("status").textContent = `Loaded ${$("hero").options.length} pregens and ${$("monster").options.length} monsters for ${edition}.`;
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
        const required_aspects = entry.recipe ? entry.recipe.aspects.map(aspect => ({kind:aspect.kind,value:aspect.value,observed:window.IRON_PIT_COMBAT_PRESETS.aspectFired(battle,aspect)})) : [];
        results.push({pattern:entry.recipe?.title || null,required_aspects,selection:entry.selection,seed:entry.seed,cards_unchanged,outcome:battle.outcome,rounds:battle.rounds,
          events:battle.events.length,observed:observed(battle.events),stable,ms:Math.round(performance.now()-start),log:battle.events});
      } catch (error) { results.push({pattern:entry.recipe?.title || null,selection:entry.selection,seed:entry.seed,error:String(error.message || error)}); }
    }
    report = {generated_at:new Date().toISOString(),engine:"IRON_PIT_BROWSER_ENGINE.runEncounter",coverage_kind:"observed events only; not RAW correctness",results};
    const failed = results.filter(row => row.error || row.stable === false || row.cards_unchanged === false || row.required_aspects?.some(aspect => !aspect.observed)).length;
    $("status").textContent = `${results.length} runs; ${failed} engine errors, replay mismatches or card mutations.`;
    $("summary").textContent = `${results.filter(row => row.outcome === "heroes_win").length} hero wins, ${results.filter(row => row.outcome === "monsters_win").length} monster wins, ${results.filter(row => row.outcome === "draw").length} draws.`;
    const table = document.createElement("table");
    const head = document.createElement("tr");
    for (const key of ["Pattern","Seed","Heroes","Monsters","Outcome / Error","Rounds","Events","Replay","Cards unchanged","Required mechanics"]) {
      const th = document.createElement("th"); th.textContent=key; head.append(th);
    }
    table.append(head);
    results.forEach(row => {
      const tr=document.createElement("tr");
      for (const value of [row.pattern || "Ad hoc",row.seed,row.selection.hero_ids.length,row.selection.monster_ids.length,row.error || row.outcome,row.rounds ?? "—",row.events ?? "—",row.stable === null || row.stable === undefined ? "Not checked" : row.stable ? "PASS" : "FAIL",row.cards_unchanged === undefined ? "—" : row.cards_unchanged ? "PASS" : "FAIL",row.required_aspects ? row.required_aspects.every(a => a.observed) ? "PASS" : "FAIL" : "Not asserted"]) {
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
  $("all-presets").addEventListener("click", async () => {
    const button = $("all-presets");
    button.disabled = true;
    $("status").textContent = "Building certified 2014/2024 preset fights…";
    try {
      const recipes = window.IRON_PIT_COMBAT_PRESET_RECIPES.recipes;
      const catalogs = {};
      for (const edition of ["2014", "2024"]) catalogs[edition] = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog(edition);
      const entries = recipes.map(recipe => {
        const roster = window.IRON_PIT_COMBAT_PRESETS.resolve(recipe, catalogs[recipe.ruleset]);
        return {
          recipe, seed: recipe.seed,
          selection: {ruleset:recipe.ruleset,
            hero_ids:roster.heroes.map(card=>card.runnable_template_id),
            monster_ids:roster.monsters.map(card=>card.runnable_template_id)}
        };
      });
      // One sequential run per recipe. Each entry retains its full event log.
      execute(entries, true);
      $("status").textContent += " All preset patterns checked with repeat-seed, source-card immutability and required event assertions. Select a result row for its preserved log.";
    } catch (error) {
      $("status").textContent = "Fight All configuration error: " + String(error.message || error);
    } finally {
      button.disabled = false;
    }
  });
  $("download").addEventListener("click",()=>{
    if (!report) return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:"application/json"}));
    const anchor=document.createElement("a"); anchor.href=url;anchor.download="iron-pit-engine-test-report.json";anchor.click();
    URL.revokeObjectURL(url);
  });
  populate();
})();
