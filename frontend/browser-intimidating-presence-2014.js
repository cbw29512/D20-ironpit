(() => {
  "use strict";

  const FEATURE = "intimidating-presence-2014", FRIGHTENED = "frightened";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const immunityKey = (sourceId) => `${FEATURE}:immune:${sourceId}`;

  function activeEffect(target, sourceId) {
    return target.state.timed_effects.find((effect) => effect.effect_id === FRIGHTENED
      && effect.source_id === sourceId && effect.source_effect_id === FEATURE) || null;
  }

  function canPerceive(target) {
    const effects = target.state.active_effect_ids || [];
    return !(effects.includes("blinded") && effects.includes("deafened"));
  }

  function canUse(actor, target) {
    const dc = actor.state.template.intimidating_presence_2014_dc || 0;
    return actor.state.template.ruleset === "2014" && dc > 0 && E().available(actor.state, "action")
      && target.state.is_alive && !target.state.is_dead && S().distance(actor, target) <= 30
      && canPerceive(target) && !I().immune(target.state, FRIGHTENED)
      && !(immunityKey(actor.combatant_id) in target.state.feature_last_turn_keys)
      && !activeEffect(target, actor.combatant_id);
  }

  function resolve(sequence, round, actor, target) {
    if (!canUse(actor, target)) return null;
    const dc = actor.state.template.intimidating_presence_2014_dc;
    const save = V().resolveSavingThrow(target.state, "wisdom", dc);
    E().spend(actor.state, "action");
    const applied = [];
    if (save.succeeded) target.state.feature_last_turn_keys[immunityKey(actor.combatant_id)] = "24h";
    else {
      const effect = T().apply(target.state, FRIGHTENED, actor.combatant_id, {
        sourceEffectId: FEATURE, appliedRound: round, expiresRound: round + 1,
        expiryTiming: "source_turn_end", useDefaultPoisonRecovery: false,
      });
      if (effect) applied.push(effect);
    }
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: actor.combatant_id, actor_name: actor.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      saving_throw_roll: save.roll, save_ability: "wisdom", save_dc: dc, save_succeeded: save.succeeded,
      applied_condition_ids: applied, feature_id: FEATURE, animation: "fear",
      description: `${actor.state.template.name} uses Intimidating Presence; ${target.state.template.name} ${save.succeeded ? "resists" : "is Frightened"}.`,
    };
  }

  function extend(sequence, round, actor, target) {
    const effect = activeEffect(target, actor.combatant_id);
    if (!effect || !E().available(actor.state, "action") || S().distance(actor, target) > 60) return null;
    E().spend(actor.state, "action"); effect.expires_round = round + 1;
    return {
      sequence, round_number: round, event_type: "feature", actor_id: actor.combatant_id,
      actor_name: actor.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      feature_id: FEATURE, animation: "fear",
      description: `${actor.state.template.name} extends Intimidating Presence on ${target.state.template.name}.`,
    };
  }

  function cleanupTarget(sequence, round, target, setup) {
    const events = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    for (const effect of [...target.state.timed_effects]) {
      if (effect.source_effect_id !== FEATURE) continue;
      const source = members.get(effect.source_id); if (!source) continue;
      const lineOfSight = !target.state.active_effect_ids.includes("blinded")
        && !source.state.active_effect_ids.includes("invisible");
      if (lineOfSight && S().distance(target, source) <= 60) continue;
      const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: target.combatant_id, actor_name: target.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        removed_condition_ids: removed, feature_id: FEATURE, animation: "condition-ended",
        description: `Intimidating Presence ends on ${target.state.template.name}.`,
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014 = { canUse, cleanupTarget, extend, resolve };
})();
