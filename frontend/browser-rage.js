(() => {
  "use strict";

  const EFFECT = "rage", FRENZY_2014 = "frenzy-2014";
  const RESISTANCES = ["bludgeoning", "piercing", "slashing"], MINDLESS = ["charmed", "frightened"];
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
    spend: (state) => { state.bonus_action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;
  const active = (state) => state.active_effect_ids.includes(EFFECT);
  const is2014 = (state) => state.template.ruleset === "2014";
  const damageBonus = (state, attack) => active(state) && attack.rageEligible ? (state.template.rage_damage_bonus || 0) : 0;

  function endMindlessConditions(state) {
    if (!state.template.mindless_rage || is2014(state)) return [];
    const removed = MINDLESS.filter((id) => state.active_effect_ids.includes(id));
    if (!removed.length) return [];
    state.timed_effects = state.timed_effects.filter((effect) => !removed.includes(effect.effect_id));
    state.active_effect_ids = state.active_effect_ids.filter((id) => !removed.includes(id));
    return removed;
  }

  function enter(sequence, round, member) {
    const state = member.state;
    if (state.template.wearing_heavy_armor || !(state.template.rage_damage_bonus > 0) || active(state)) return null;
    if (!(state.resources.rage > 0) || !E().available(state, "bonus_action")) return null;
    state.resources.rage -= 1; E().spend(state, "bonus_action"); state.active_effect_ids.push(EFFECT);
    const frenzy2014 = is2014(state) && state.template.frenzy_bonus_attack_2014;
    if (frenzy2014) state.active_effect_ids.push(FRENZY_2014);
    const removed = endMindlessConditions(state);
    for (const type of RESISTANCES) if (!state.temporary_damage_resistances.includes(type)) state.temporary_damage_resistances.push(type);
    state.rage_expires_round = round + 1; state.rage_max_round = round + (is2014(state) ? 10 : 100);
    let description = `${state.template.name} enters Rage.`;
    if (frenzy2014) description += " The Berserker enters a Frenzy.";
    if (removed.length) description += ` Mindless Rage ends ${removed.join(", ")}.`;
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: EFFECT, removed_condition_ids: removed,
      resource_remaining: state.resources.rage, animation: "rage", description };
  }

  function extendFromAttack(state, round) {
    if (!active(state)) return;
    state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
  }

  function end(state) {
    if (!active(state)) return null;
    const frenzied = state.active_effect_ids.includes(FRENZY_2014);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== EFFECT && id !== FRENZY_2014);
    state.temporary_damage_resistances = state.temporary_damage_resistances.filter((type) => !RESISTANCES.includes(type));
    state.rage_expires_round = null; state.rage_max_round = null;
    return frenzied ? X().gain(state) : null;
  }

  function endIfIncapacitated(state) {
    if (state.template.wearing_heavy_armor || state.is_dead || Q().incapacitated(state)) end(state);
  }

  function maintain(sequence, round, member) {
    const state = member.state;
    if (is2014(state) || !active(state) || state.rage_expires_round === null || state.rage_expires_round > round
        || (state.rage_max_round && state.rage_max_round <= round) || !E().available(state, "bonus_action")) return null;
    E().spend(state, "bonus_action");
    state.rage_expires_round = Math.min(round + 1, state.rage_max_round || round + 1);
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: EFFECT, animation: "rage",
      description: `${state.template.name} extends Rage with a Bonus Action.` };
  }

  function cleanupExpired(sequence, round, member) {
    const state = member.state;
    if (!active(state) || state.rage_expires_round === null || state.rage_expires_round > round) {
      return { events: [], sequence };
    }
    const exhaustion = end(state);
    if (exhaustion === null) return { events: [], sequence };
    return { events: [{ sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: state.template.name, feature_id: "exhaustion", animation: "condition",
      description: `${state.template.name}'s Frenzy ends and causes Exhaustion level ${exhaustion}.` }], sequence: sequence + 1 };
  }

  function finalize(sequence, round, member) {
    const maintenance = maintain(sequence, round, member);
    if (maintenance) return { event: maintenance, sequence: sequence + 1 };
    const cleaned = cleanupExpired(sequence, round, member);
    return { event: cleaned.events[0] || null, sequence: cleaned.sequence };
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Rage hook installation requires browser-ability-hooks.js.");
    const bonusPhase = hooks.PHASES.BONUS_ACTION_WINDOW;
    const finalizePhase = hooks.PHASES.TURN_FINALIZE;
    const bonusIds = () => new Set(hooks.abilitiesFor(bonusPhase).map((item) => item.id));

    if (!bonusIds().has("rage-enter")) hooks.registerAbility(bonusPhase, {
      id: "rage-enter", priority: 10, rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
      resolve: ({ sequence, round, member, setup, turnKey }) => {
        const rage = enter(sequence, round, member);
        if (!rage) return null;
        const events = [rage]; let nextSequence = sequence + 1;
        const fraction = member.state.template.instinctive_pounce_fraction || 0;
        if (fraction > 0) {
          const movement = window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT;
          if (!movement) throw new Error("Rage Instinctive Pounce requires browser-activation-movement.js.");
          const moved = movement.resolve(nextSequence, round, member, setup, { speedFraction: fraction, turnKey });
          events.push(...moved.events); nextSequence = moved.sequence;
          window.IRON_PIT_BROWSER_PALADIN_AURAS_2014?.sync(setup);
        }
        return { events, sequence: nextSequence, claimed: true };
      },
    });

    if (!bonusIds().has("rage-maintain")) hooks.registerAbility(bonusPhase, {
      id: "rage-maintain", priority: 120, rulesets: ["2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "postAction",
      resolve: ({ sequence, round, member }) => {
        const event = maintain(sequence, round, member);
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });

    if (!hooks.abilitiesFor(finalizePhase).some((item) => item.id === "rage-expiry-cleanup")) {
      hooks.registerAbility(finalizePhase, {
        id: "rage-expiry-cleanup", priority: 100, rulesets: ["2014", "2024"],
        resolve: ({ sequence, round, member }) => {
          const result = cleanupExpired(sequence, round, member);
          return { ...result, claimed: false };
        },
      });
    }
  }

  window.IRON_PIT_BROWSER_RAGE = {
    active, cleanupExpired, damageBonus, end, endIfIncapacitated, enter, extendFromAttack,
    finalize, installAbilityHooks, maintain,
  };
})();
