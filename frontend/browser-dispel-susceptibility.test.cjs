const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
global.window = global;
for (const name of [
  'browser-monsters-2014.js', 'browser-heroes.js', 'browser-state.js',
  'browser-condition-immunity.js', 'browser-condition-rules.js',
  'browser-modifiers.js', 'browser-concentration.js', 'browser-replacement-forms.js',
  'browser-timed-conditions.js', 'browser-action-economy.js', 'browser-spellcasting.js',
  'browser-effect-tag-conditions.js', 'browser-effect-removal.js',
]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), 'utf8'), { filename: name });
const armor = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014).find(item => item.name === 'Animated Armor');
const casterTemplate = Object.values(window.IRON_PIT_BROWSER_HEROES).find(item =>
  item.ruleset === '2014' && item.effect_removal_actions?.some(action => (action.effectTags || []).includes('spell_dispelling')));
assert.ok(casterTemplate, 'Production export preserves incoming semantic tags');
assert.deepEqual(armor.effect_tag_condition_grants.map(g => [g.effect_tag, g.condition_id, g.duration_rounds]),
  [['spell_dispelling', 'stunned', 10]]);
const api = window.IRON_PIT_BROWSER_EFFECT_REMOVAL;
function fixture() {
  const member = (id, side, template, position) => ({ combatant_id: id, side, position_ft: position,
    state: window.IRON_PIT_BROWSER_STATE.buildState(template) });
  const actor = member('caster', 'heroes', casterTemplate, 0);
  const target = member('target', 'monsters', { ...armor, name: 'Renamed construct' }, 30);
  actor.state.resources['spell-slot-3'] = 2;
  return { actor, target, setup: { heroes: [actor], monsters: [target], ruleset: '2014' } };
}
{
  const { actor, target, setup } = fixture();
  const before = JSON.stringify(target.state.template);
  const picked = api.choose(actor, setup, '1:caster');
  const event = api.resolve(1, 2, actor, setup, picked.action, picked.effect, '1:caster');
  assert.deepEqual(event.applied_condition_ids, ['stunned']);
  assert.equal(event.hp_before, event.hp_after);
  assert.equal(target.state.is_alive, true);
  assert.equal(target.state.is_dead, false);
  assert.equal(target.state.is_unconscious, false);
  assert.equal(window.IRON_PIT_BROWSER_CONDITION_RULES.speedZero(target.state), true);
  assert.equal(window.IRON_PIT_BROWSER_CONDITION_RULES.autoCritical(target.state), false);
  for (const cost of ['action', 'bonus_action', 'reaction']) assert.equal(window.IRON_PIT_ACTION_ECONOMY.available(target.state, cost), false);
  assert.equal(actor.state.action_available, false);
  assert.equal(actor.state.resources['spell-slot-3'], 1);
  const timed = target.state.timed_effects[0];
  assert.equal(timed.expires_round, 12);
  assert.equal(timed.repeat_save_dc, null);
  assert.equal(timed.ends_on_damage, false);
  assert.equal(window.IRON_PIT_BROWSER_TIMED.expireSourceStart(2, 11, actor, setup).events.length, 0);
  actor.state.is_dead = true;
  assert.deepEqual(window.IRON_PIT_BROWSER_TIMED.expireSourceStart(2, 12, actor, setup).events[0].removed_condition_ids, ['stunned']);
  assert.deepEqual(target.state.active_effect_ids, []);
  assert.equal(JSON.stringify(target.state.template), before);
  assert.deepEqual(window.IRON_PIT_BROWSER_STATE.buildState(target.state.template).timed_effects, []);
}
for (const reason of ['range', 'immune', 'ordinary', 'already_stunned', 'slot']) {
  const { actor, target, setup } = fixture();
  if (reason === 'range') target.position_ft = 121;
  if (reason === 'immune') target.state.template = { ...armor, condition_immunities: ['stunned'] };
  if (reason === 'ordinary') target.state.template = { ...armor, effect_tag_condition_grants: [] };
  if (reason === 'already_stunned') target.state.active_effect_ids.push('stunned');
  if (reason === 'slot') actor.state.resources['spell-slot-3'] = 0;
  assert.equal(api.choose(actor, setup, '1:caster'), null, reason);
  assert.equal(actor.state.action_available, true);
}
for (const reason of ['range', 'slot', 'dependency']) {
  const { actor, target, setup } = fixture();
  const picked = api.choose(actor, setup, '1:caster');
  const saved = window.IRON_PIT_BROWSER_TIMED;
  if (reason === 'range') target.position_ft = 121;
  if (reason === 'slot') actor.state.resources['spell-slot-3'] = 0;
  if (reason === 'dependency') delete window.IRON_PIT_BROWSER_TIMED;
  try { assert.throws(() => api.resolve(1, 1, actor, setup, picked.action, picked.effect, '1:caster')); }
  finally { window.IRON_PIT_BROWSER_TIMED = saved; }
  assert.equal(actor.state.action_available, true);
  assert.deepEqual(target.state.timed_effects, []);
}
console.log('Dispel susceptibility reuses shared Stunned with lifecycle and legality parity.');
{
  const { actor, target, setup } = fixture();
  target.state.concentration = { source_id: 'target', effect_id: 'buff', started_round: 1 };
  actor.state.active_modifiers.push({ id: 'buff', source_id: 'target', source_effect_id: 'buff',
    kind: 'armor-class', flat_bonus: 2, concentration_required: true });
  const picked = api.choose(actor, setup, '1:caster');
  api.resolve(1, 1, actor, setup, picked.action, picked.effect, '1:caster');
  assert.equal(target.state.concentration, null);
  assert.deepEqual(actor.state.active_modifiers, []);
}
