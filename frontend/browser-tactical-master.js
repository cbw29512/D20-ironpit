(() => {
  "use strict";

  const WEAPON_EFFECT_ID = "weapon-mastery-sap";
  const TACTICAL_EFFECT_ID = "tactical-master-sap";
  const SAP_EFFECT_IDS = new Set([WEAPON_EFFECT_ID, TACTICAL_EFFECT_ID]);
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;

  function applyEffect(attackerId, target, round, effectId, sourceEffectId) {
    if (target.state.is_dead || target.state.current_hp <= 0) return false;
    return Boolean(T().apply(target.state, effectId, attackerId, {
      sourceEffectId, appliedRound: round, expiresRound: round + 1, expiryTiming: "source_turn_start",
    }));
  }

  function selected(state, attack) {
    return W().mastered(state, attack)
      && (state.template.tactical_master_sap_weapon_ids || []).includes(attack.weaponId);
  }

  function weaponEligible(state, attack) {
    return W().active(state, attack, "Sap");
  }

  function applyWeapon(attacker, target, attack, round) {
    if (!weaponEligible(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, WEAPON_EFFECT_ID, "weapon-mastery");
  }

  const disadvantage = (state) => state.timed_effects.some((effect) => SAP_EFFECT_IDS.has(effect.effect_id)) ? 1 : 0;

  function consume(state) {
    const effects = state.timed_effects.filter((effect) => SAP_EFFECT_IDS.has(effect.effect_id));
    for (const effect of [...effects]) T().removeEffect(state, effect);
    return effects.length;
  }

  function applyTactical(attacker, target, attack, round) {
    if (!selected(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, TACTICAL_EFFECT_ID, "tactical-master");
  }

  function resolveBeforeAttackRoll(ctx) {
    const api = ctx.attackRollApi;
    if (!api) throw new Error("Before-attack-roll hook requires attackRollApi.");
    const roll = api.requireContext(ctx);
    const active = disadvantage(ctx.member.state);
    if (!active) return null;
    api.setDisadvantageSource(roll, "sap", active);
    consume(ctx.member.state);
    return api.noEventResult(ctx.sequence);
  }

  function resolveHit(ctx) {
    const outcome = O().requireOutcome(ctx);
    if (ctx.target.state.is_dead || ctx.target.state.current_hp <= 0) return null;
    if (applyWeapon(ctx.member, ctx.target, ctx.attack, ctx.round)) outcome.sapApplied = "weapon";
    else if (applyTactical(ctx.member, ctx.target, ctx.attack, ctx.round)) outcome.sapApplied = "tactical";
    return outcome.sapApplied ? O().noEventResult(ctx.sequence) : null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Sap hook installation requires browser-ability-hooks.js.");
    const pre = hooks.PHASES.BEFORE_ATTACK_ROLL;
    if (!hooks.abilitiesFor(pre).some((item) => item.id === "sap-disadvantage")) {
      hooks.registerAbility(pre, {
        id: "sap-disadvantage", priority: 15, rulesets: ["2024"],
        appliesTo: (member) => disadvantage(member.state) > 0,
        resolve: resolveBeforeAttackRoll,
      });
    }
    const hit = hooks.PHASES.ON_HIT;
    if (!hooks.abilitiesFor(hit).some((item) => item.id === "sap-outcome")) {
      hooks.registerAbility(hit, {
        id: "sap-outcome", priority: 20, rulesets: ["2024"],
        appliesTo: (member, ctx) => weaponEligible(member.state, ctx.attack) || selected(member.state, ctx.attack),
        resolve: resolveHit,
      });
    }
  }

  window.IRON_PIT_BROWSER_SAP = {
    applyEffect, applyWeapon, consume, disadvantage, installAbilityHooks, resolveBeforeAttackRoll, resolveHit, weaponEligible,
  };
  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: applyTactical, eligible: selected, selected };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
