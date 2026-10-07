const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = global;
for (const name of [
  "browser-monsters-2014.js", "browser-state.js", "browser-modifiers.js",
  "browser-concentration.js", "browser-replacement-forms.js",
  "browser-zero-hp-replacement.js", "browser-zero-hp.js",
  "browser-healing.js", "browser-regeneration.js", "browser-terminal-effects.js",
]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

// These are semantic fixtures built with production state, not alternative resolvers.
const armor = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014).find((item) => item.name === "Animated Armor");
const template = { ...armor, name: "Unrelated display name" };
const build = () => window.IRON_PIT_BROWSER_STATE.buildState(template);
const terminal = window.IRON_PIT_BROWSER_TERMINAL_EFFECTS;
const prevention = {
  id: "protection", source_id: "ally", source_effect_id: "protection",
  kind: "zero-hp-replacement", replacement_hp: 1, prevents_instant_death: true,
};
{
  const state = build(), ordinary = build();
  state.active_modifiers.push({ ...prevention });
  ordinary.active_modifiers.push({ ...prevention });
  assert.equal(terminal.applyTerminalEffectTag(state, " ANTIMAGIC "), "dead");
  assert.deepEqual(state.active_modifiers, [prevention]);
  assert.equal(window.IRON_PIT_BROWSER_ZERO_HP.applyInstantDeath(ordinary), "zero_hp_replacement");
  assert.equal(ordinary.is_dead, false);
}
{
  const before = JSON.stringify(template);
  const state = window.IRON_PIT_BROWSER_STATE.buildState({ ...template,
    regeneration: { amount: 10, survives_zero_until_turn: true },
  });
  state.current_hp = 0;
  state.is_unconscious = true;
  assert.equal(terminal.applyTerminalEffectTag(state, "antimagic"), "dead");
  assert.equal(terminal.applyTerminalEffectTag(state, "antimagic"), "unchanged");
  assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(state, 10), 0);
  assert.equal(window.IRON_PIT_BROWSER_REGENERATION.apply(state).healed, 0);
  assert.equal(state.current_hp, 0);
  assert.equal(state.is_dead, true);
  const fresh = build();
  assert.equal(fresh.current_hp, template.max_hp);
  assert.equal(fresh.is_dead, false);
  assert.equal(JSON.stringify(template), before);
}
{
  const state = build(), ally = build();
  // A declared form should revert while death remains terminal on the owner.
  state.replacement_form = {
    original_template: template, form_template: { ...template, id: "other-form" },
    ends_on_incapacitated: true, source_id: "form", source_name: "Any form",
  };
  state.template = state.replacement_form.form_template;
  state.concentration = { source_id: "owner", effect_id: "buff", started_round: 1 };
  ally.active_modifiers.push({
    id: "buff", source_id: "owner", source_effect_id: "buff",
    kind: "armor-class", flat_bonus: 2, concentration_required: true,
  });
  assert.equal(terminal.applyTerminalEffectTag(state, "antimagic", [ally]), "dead");
  assert.equal(state.replacement_form, null);
  assert.equal(state.template.id, template.id);
  assert.equal(state.concentration, null);
  assert.deepEqual(ally.active_modifiers, []);
  assert.equal(state.current_hp, 0);
  assert.equal(state.is_dead, true);
}
{
  const state = build();
  state.template = { ...template, terminal_effect_tags: [] };
  assert.equal(terminal.applyTerminalEffectTag(state, "antimagic"), "not_susceptible");
  assert.throws(() => terminal.applyTerminalEffectTag(state, " "), /non-empty/);
  assert.equal(state.is_dead, false);
  assert.equal(state.current_hp, template.max_hp);
}
{
  const state = build(), saved = window.IRON_PIT_BROWSER_CONCENTRATION;
  state.concentration = { source_id: "owner", effect_id: "buff" };
  delete window.IRON_PIT_BROWSER_CONCENTRATION;
  try {
    assert.throws(() => terminal.applyTerminalEffectTag(state, "antimagic"), /concentration runtime/);
    assert.equal(state.is_dead, false, "Missing dependencies fail before HP mutation");
  } finally {
    window.IRON_PIT_BROWSER_CONCENTRATION = saved;
  }
}
console.log("Shared terminal-effect lifecycle and prevention distinction passed.");
