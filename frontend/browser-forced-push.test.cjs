const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost(member, maximum) {
    const order = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
    return order[member.state.template.size] <= order[maximum];
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, attacker, target, attack) {
    return {
      sequence,
      round_number: round,
      target_id: target.combatant_id,
      hit: true,
      description: `${attacker.state.template.name} hits ${target.state.template.name} with ${attack.name}.`,
    };
  },
};
window.IRON_PIT_BROWSER_LIGHT_ATTACK = { resolve: () => ({ events: [], sequence: 2 }) };
window.IRON_PIT_BROWSER_WEAPON_MASTERY = { resolveCleave: (sequence) => ({ events: [], sequence }) };

const source = fs.readFileSync(path.join(__dirname, "browser-standard-attack-action.js"), "utf8");
vm.runInThisContext(source, { filename: "browser-standard-attack-action.js" });

function member(id, side, position, size) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      template: { name: id, size, kind: "monster" },
      is_alive: true,
      is_dead: false,
      turn_terminated: false,
    },
  };
}

{
  const attacker = member("attacker", "heroes", 0, "medium");
  const target = member("target", "monsters", 5, "large");
  const attack = { name: "Warhammer", pushTargetAwayFt: 10, pushTargetMaxSize: "large" };
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, attacker, target, attack, 5, {});
  assert.equal(target.position_ft, 15);
  assert.match(event.description, /pushed 10 feet straight away/);
}

{
  const attacker = member("attacker", "heroes", 0, "medium");
  const target = member("target", "monsters", 5, "huge");
  const attack = { name: "Warhammer", pushTargetAwayFt: 10, pushTargetMaxSize: "large" };
  window.IRON_PIT_BROWSER_ATTACK.resolveAttack(2, 1, attacker, target, attack, 5, {});
  assert.equal(target.position_ft, 5);
}

console.log("browser forced push regression passed");
