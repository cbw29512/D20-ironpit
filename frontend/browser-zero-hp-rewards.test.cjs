const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
window.IRON_PIT_BROWSER_STATE = {
  grantTemporaryHp(state, amount) {
    if (amount < 0) throw new Error("Temporary HP cannot be negative.");
    state.temporary_hp = Math.max(state.temporary_hp || 0, amount);
    return state.temporary_hp;
  },
};
vm.runInThisContext(fs.readFileSync("frontend/browser-zero-hp-rewards.js", "utf8"));

function fixture() {
  const source = {
    combatant_id: "varek",
    side: "heroes",
    state: {
      temporary_hp: 3,
      template: {
        name: "Varek Ashenmark",
        zero_hp_temporary_hp_grant: {
          source_id: "dark-ones-blessing",
          source_name: "Dark One's Blessing",
          temporary_hp: 10,
        },
      },
    },
  };
  const target = {
    combatant_id: "goblin",
    side: "monsters",
    state: { template: { name: "Goblin" } },
  };
  return { source, target, setup: { heroes: [source], monsters: [target] } };
}

{
  const { source, target, setup } = fixture();
  const event = {
    sequence: 1, actor_id: "varek", target_id: "goblin",
    hp_before: 6, hp_after: 0,
  };
  const reward = window.IRON_PIT_BROWSER_ZERO_HP_REWARDS.resolve(
    2, 1, source, event, setup,
  );
  assert.equal(reward.feature_id, "dark-ones-blessing");
  assert.equal(reward.temporary_hp_before, 3);
  assert.equal(reward.temporary_hp_after, 10);
  assert.equal(source.state.temporary_hp, 10);
}

{
  const { source, target, setup } = fixture();
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP_REWARDS.resolve(
    2, 1, source,
    { sequence: 1, actor_id: "varek", target_id: "goblin", hp_before: 6, hp_after: 1 },
    setup,
  ), null);
  target.side = "heroes";
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP_REWARDS.resolve(
    2, 1, source,
    { sequence: 1, actor_id: "varek", target_id: "goblin", hp_before: 6, hp_after: 0 },
    setup,
  ), null);
}

console.log("Browser generic zero-HP Temporary HP rewards passed.");
