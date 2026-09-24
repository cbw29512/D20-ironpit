(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const EFFECT_ID = "timed-aura";
  const active = (state, action) => (state.timed_effects || []).some((effect) =>
    effect.effect_id === EFFECT_ID && effect.source_effect_id === action.id);

  function choose(member) {
    try {
      const choices = (member.state.template.timed_aura_actions || []).filter((action) =>
        E().available(member.state, action.actionCost)
        && (member.state.resources[action.resourceId] || 0) >= (action.resourceCost || 1)
        && !active(member.state, action));
      choices.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return choices[0] || null;
    } catch (error) {
      console.error("Timed aura choice failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function activate(sequence, round, member, action) {
    try {
      if (!E().available(member.state, action.actionCost)) throw new Error(action.name + " action cost is unavailable.");
      if ((member.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) throw new Error(action.name + " resource is unavailable.");
      E().spend(member.state, action.actionCost);
      member.state.resources[action.resourceId] -= action.resourceCost || 1;
      T().apply(member.state, EFFECT_ID, member.combatant_id, {
        sourceEffectId: action.id, appliedRound: round, expiresRound: round + action.durationRounds,
        expiryTiming: "source_turn_start", expiresAtStartOfSourceTurn: true, useDefaultPoisonRecovery: false,
      });
      return {
        sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: member.state.template.name, target_id: member.combatant_id,
        target_name: member.state.template.name, feature_id: action.id,
        resource_remaining: member.state.resources[action.resourceId], animation: action.animation || "timed-aura",
        description: member.state.template.name + " uses " + action.name + ".",
      };
    } catch (error) {
      console.error("Timed aura activation failed.", { combatant: member?.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  function matchingSaveAuras(state, ability, context = {}) {
    const sourceType = String(context.sourceCreatureType || "").split(" (")[0].trim().toLowerCase();
    return (state.template.timed_aura_actions || []).filter((action) =>
      active(state, action)
      && (action.savingThrowAdvantageAbilities || []).includes(ability)
      && (!action.savingThrowAdvantageRequiresSpell || Boolean(context.sourceIsSpell))
      && (!(action.savingThrowAdvantageSourceCreatureTypes || []).length
        || action.savingThrowAdvantageSourceCreatureTypes.map((item) => item.toLowerCase()).includes(sourceType)));
  }

  const saveAdvantage = (state, ability, context = {}) => matchingSaveAuras(state, ability, context).length;
  const saveAdvantageSourceNames = (state, ability, context = {}) =>
    [...new Set(matchingSaveAuras(state, ability, context).map((action) => action.name))].sort();

  function resolveStartTurn(sequence, round, target, setup) {
    try {
      const enemies = target.side === "heroes" ? setup.monsters : setup.heroes;
      const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
      const events = [];
      for (const source of enemies) for (const action of source.state.template.timed_aura_actions || []) {
        if (!active(source.state, action) || !(action.startTurnFixedDamage > 0)) continue;
        if (S().distance(source, target) > action.radiusFt) continue;
        const raw = action.startTurnFixedDamage;
        const applied = A().adjustedDamage(target.state, raw, action.damageType);
        const hpBefore = target.state.current_hp;
        if (applied) A().applyDamage(target.state, applied, false, [action.damageType], states);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          damage_roll: { notation: String(raw), rolls: [], modifier: raw, total: applied },
          damage_components: [{ source: action.name, notation: String(raw), rolls: [], modifier: raw,
            damage_type: action.damageType, total: raw, applied_total: applied }],
          hp_before: hpBefore, hp_after: target.state.current_hp, is_dead: target.state.is_dead,
          feature_id: action.id, animation: action.animation || "timed-aura",
          description: target.state.template.name + " takes " + applied + " " + action.damageType + " damage from " + action.name + ".",
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Timed aura start-turn resolution failed.", { combatant: target?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHook() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) {
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= [];
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS.push(installAbilityHook);
      return;
    }
    const phase = hooks.PHASES.TURN_START;
    if (hooks.abilitiesFor(phase).some((ability) => ability.id === "timed-aura-start-turn")) return;
    hooks.registerAbility(phase, {
      id: "timed-aura-start-turn", priority: 20, rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => [...ctx.setup.heroes, ...ctx.setup.monsters].some((source) =>
        (source.state.template.timed_aura_actions || []).some((action) => active(source.state, action))),
      resolve: ({ sequence, round, member, setup }) => {
        const result = resolveStartTurn(sequence, round, member, setup);
        return result.events.length ? { events: result.events, sequence: result.sequence, claimed: false } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TIMED_AURAS = {
    active, activate, choose, installAbilityHook, resolveStartTurn, saveAdvantage, saveAdvantageSourceNames,
  };
  installAbilityHook();
})();
