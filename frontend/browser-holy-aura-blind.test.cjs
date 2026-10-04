"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => state.is_unconscious || (state.active_effect_ids || []).includes("incapacitated"),
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.state.position?.x || 0) - (b.state.position?.x || 0)) * 5,
};
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (state, ability, dc, context = {}) => {
    const roll = (window.IRON_PIT_DICE && window.IRON_PIT_DICE.roll)
      ? window.IRON_PIT_DICE.roll(20)
      : (context.forcedRoll ?? 1);
    return { succeeded: roll >= dc, roll: { total: roll } };
  },
};
window.IRON_PIT_DICE = {
  rolls: [1],
  roll() {
    return this.rolls.shift() ?? 1;
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  apply(state, effectId, sourceId, options = {}) {
    state.active_effect_ids.push(effectId);
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: options.sourceEffectId || null,
      expiry_timing: options.expiryTiming || null,
      expires_round: options.expiresRound ?? null,
    });
    return effectId;
  },
};

load("browser-melee-hit-save-retaliation.js");

function member(id, side, x, extras = {}) {
  return {
    combatant_id: id, side,
    state: {
      template: {
        name: id,
        creature_type: extras.type || "humanoid",
        timed_self_buff_actions: extras.buffs || [],
      },
      current_hp: extras.hp ?? 40,
      is_alive: true, is_dead: false, is_unconscious: false,
      active_effect_ids: [],
      timed_effects: extras.effects || [],
      position: { x, y: 0 },
    },
  };
}

const auraBuff = [{
  id: "holy-aura",
  friendlySaveAdvantageAura: {
    radius_ft: 30,
    all_saves: true,
    attacks_against_disadvantage: true,
    melee_hit_save_retaliation: {
      attacker_creature_types: ["fiend", "undead"],
      save_ability: "constitution",
      save_dc: 18,
      condition_id: "blinded",
      expiry_timing: "target_turn_end",
      duration_rounds: 1,
    },
  },
}];

{
  const cleric = member("cleric", "heroes", 0, {
    buffs: auraBuff,
    effects: [{ source_id: "cleric", source_effect_id: "holy-aura" }],
  });
  const ally = member("ally", "heroes", 1);
  const fiend = member("fiend", "monsters", 2, { type: "fiend" });
  const setup = { heroes: [cleric, ally], monsters: [fiend] };
  window.IRON_PIT_DICE.rolls = [1];
  const applied = window.IRON_PIT_BROWSER_MELEE_HIT_SAVE_RETALIATION.apply(
    fiend, ally, { melee: true, setup, round: 1 },
  );
  assert.equal(applied, "blinded");
  assert.ok(fiend.state.active_effect_ids.includes("blinded"));
  assert.equal(fiend.state.timed_effects[0].expiry_timing, "target_turn_end");
}

{
  const cleric = member("cleric", "heroes", 0, {
    buffs: auraBuff,
    effects: [{ source_id: "cleric", source_effect_id: "holy-aura" }],
  });
  const ally = member("ally", "heroes", 1);
  const human = member("human", "monsters", 2, { type: "humanoid" });
  const setup = { heroes: [cleric, ally], monsters: [human] };
  assert.equal(
    window.IRON_PIT_BROWSER_MELEE_HIT_SAVE_RETALIATION.apply(
      human, ally, { melee: true, setup, round: 1 },
    ),
    null,
  );
}

{
  const cleric = member("cleric", "heroes", 0, {
    buffs: auraBuff,
    effects: [{ source_id: "cleric", source_effect_id: "holy-aura" }],
  });
  const ally = member("ally", "heroes", 1);
  const fiend = member("fiend", "monsters", 2, { type: "fiend" });
  const setup = { heroes: [cleric, ally], monsters: [fiend] };
  window.IRON_PIT_DICE.rolls = [20];
  assert.equal(
    window.IRON_PIT_BROWSER_MELEE_HIT_SAVE_RETALIATION.apply(
      fiend, ally, { melee: true, setup, round: 1 },
    ),
    null,
  );
  assert.ok(!fiend.state.active_effect_ids.includes("blinded"));
}

console.log("Holy Aura Fiend/Undead melee Blind rider browser parity passed.");
