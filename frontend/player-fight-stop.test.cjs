"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
global.requestAnimationFrame = callback => callback();
const controls = new Map();
const el = id => {
  if (!controls.has(id)) {
    const node = {disabled:false, hidden:false, textContent:"", value:"",
      listeners:{}, addEventListener(type, callback){this.listeners[type]=callback;}};
    controls.set(id,node);
  }
  return controls.get(id);
};
global.document = {getElementById:el};
const load = name => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname,name),"utf8"), {filename:name});
let currentLog = null, showResult = false, seenEvents = [];
let firstSeen = null, releaseFirst = null;
let firstGate = null, started = null;
let resolutions = 0;
const events = Array.from({length:5},(_,i)=>({event_type:"attack",round_number:i+1,id:i+1}));
const battle = {events,setup:{heroes:[],monsters:[]},rounds:5};
window.IRON_PIT_BATTLEFIELD_REPLAY = {
  bindBattle(){},
  eventStep:async event=>{
    if (firstGate) {
      const gate = firstGate; firstGate = null;
      started?.(); await gate;
    }
    seenEvents.push(event.id);
  },
  syncFinal(){},
};
window.IRON_PIT_BATTLEFIELD_VIEW = {
  writeLog:b=>{currentLog=b;}, showResult:()=>{showResult=true;},
};
window.IRON_PIT_BATTLE_LAB = {summary:()=>"Test summary"};
window.IRON_PIT_RULESET_UI = {syncDisabled(){}};
window.IRON_PIT_COMBAT_PRESETS = {selected:()=>null,sync(){}};

(async () => {
try {
  load("browser-execution.js");
  load("player-control-state.js");
  load("battle-fight-stop.js");
  load("battle-actions.js");
  const execution = window.IRON_PIT_EXECUTION;
  execution.resolveLive = (_selection,slotMap)=>{
    resolutions++;
    return execution.createSession({battle,slotMap,mode:"live"});
  };
  const state = {fighting:false,liveFightRunning:false,
    stopFightRequested:false,hasRun:false,session:null,turboBatch:null,
    heroSlots:[{}],monsterSlots:[{}]};
  const api = {
    state, matchup:()=>({error:null,heroes:{indexes:[0]},monsters:{indexes:[0]},
      selection:{hero_ids:["test-hero"],monster_ids:["test-monster"]}}),
    render:()=>window.IRON_PIT_PLAYER_CONTROL_STATE.update(state),
    updateControls:()=>window.IRON_PIT_PLAYER_CONTROL_STATE.update(state),
    clearResult:()=>{currentLog=null;showResult=false;},
  };
  window.IRON_PIT_BATTLE_ACTIONS.install(api);
  api.updateControls();
  assert.equal(el("fight-button").textContent,"Fight");
  assert.equal(el("fight-button").disabled,false);

  // A real delayed event lets a user click Stop while the first event animates.
  firstGate = new Promise(resolve=>{releaseFirst=resolve;});
  const firstStarted = new Promise(resolve=>{started=resolve;});
  const playing = el("fight-button").listeners.click();
  await firstStarted;
  assert.equal(el("fight-button").textContent,"Stop Fight");
  assert.equal(el("fight-button").disabled,false);
  assert.equal(state.fighting,true);
  el("fight-button").listeners.click();
  assert.equal(state.stopFightRequested,true);
  releaseFirst();
  await playing;
  assert.equal(resolutions,1,"Second click must not start another encounter");
  assert.deepEqual(seenEvents,[1],"Stop must prevent all later events");
  assert.equal(state.session.eventIndex,1);
  assert.equal(state.session.stopped,true);
  assert.equal(state.session.complete,true);
  assert.deepEqual(currentLog.events,[events[0]],"Only viewed events are retained");
  assert.equal(showResult,false,"Stop must not show an unearned winner");
  assert.equal(state.hasRun,true);
  assert.match(el("status").textContent,/stopped after 1 events/);
  assert.equal(el("fight-button").textContent,"Fight");
  assert.equal(el("fight-button").disabled,false);

  // Restart must create a completely new replay with normal completion.
  seenEvents=[];
  await el("fight-button").listeners.click();
  assert.equal(resolutions,2);
  assert.deepEqual(seenEvents,[1,2,3,4,5]);
  assert.equal(state.session.stopped,false);
  assert.equal(currentLog.events.length,5);
  assert.equal(showResult,true);

  // A second click during the pre-render frame cancels before resolution.
  let nextFrame = null;
  global.requestAnimationFrame = callback=>{nextFrame=callback;};
  const early = el("fight-button").listeners.click();
  assert.equal(el("fight-button").textContent,"Stop Fight");
  el("fight-button").listeners.click();
  nextFrame();
  await early;
  assert.equal(resolutions,2,"Pre-render stop must not resolve any fight");
  assert.equal(state.session,null);
  assert.equal(state.fighting,false);
  assert.equal(el("fight-button").textContent,"Fight");
  assert.match(el("status").textContent,/stopped before the first event/);
  console.log("Fight/Stop/Fight restart, prefix-only log, and early cancellation passed.");
} catch (error) {
  console.error("Player Fight/Stop regression failed",error);
  process.exitCode=1;
}
})();
