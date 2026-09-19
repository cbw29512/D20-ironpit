(() => {
  "use strict";

  const FEATURE = "brutal-strike";
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const F = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;

  function eligible(state, attack, turnKey, hasDisadvantage = false) {
    return Boolean(state?.template?.ruleset !== "2014"
      && (state?.template?.brutal_strike_damage_dice || 0) > 0
      && turnKey && !hasDisadvantage && attack?.attackAbility === "strength"
      && B2()?.active(state) && state.feature_last_turn_keys?.[FEATURE] !== turnKey);
  }

  function advantageSuppression(state, attack, turnKey, hasDisadvantage = false) {
    return Number(eligible(state, attack, turnKey, hasDisadvantage));
  }

  function bonusDamage(state, attack, turnKey, hasDisadvantage = false) {
    if (!eligible(state, attack, turnKey, hasDisadvantage)) return null;
    state.feature_last_turn_keys[FEATURE] = turnKey;
    return {
      source: "Brutal Strike", diceCount: state.template.brutal_strike_damage_dice,
      diceSize: 10, damageType: attack.damageType,
    };
  }

  function resolveBeforeAttackRoll(ctx) {
    const api = ctx.attackRollApi;
    if (!api) throw new Error("Before-attack-roll hook requires attackRollApi.");
    const roll = api.requireContext(ctx);
    const hasDisadvantage = roll.baseDisadvantageSources > 0 || roll.rangedDisadvantage;
    const suppression = advantageSuppression(
      ctx.member.state, ctx.attack, ctx.turnKey, hasDisadvantage,
    );
    const reckless = api.advantageSource(roll, "reckless-attacker");
    api.setAdvantageSource(roll, "reckless-attacker", Math.max(0, reckless - suppression));
    return api.noEventResult(ctx.sequence);
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Brutal Strike hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BEFORE_ATTACK_ROLL;
    if (hooks.abilitiesFor(phase).some((item) => item.id === FEATURE)) return;
    hooks.registerAbility(phase, {
      id: FEATURE, priority: 20, rulesets: ["2024"],
      appliesTo: (member) => (member.state.template.brutal_strike_damage_dice || 0) > 0,
      resolve: resolveBeforeAttackRoll,
    });
  }

  function hamstring(defender, sourceId) {
    M().add(defender, {
      id: `hamstring-blow:${sourceId}`, source_id: sourceId, source_effect_id: "hamstring-blow",
      kind: "speed", flat_bonus: -15, expires_at_start_of_source_turn: true,
    });
    return true;
  }

  function forceful(attacker, defender, setup) {
    return F().pushStraightAway(defender, attacker, setup, 15);
  }

  function followForceful(sequence, round, attacker, defender, setup, options = {}) {
    const allowance = Math.floor(M().effectiveSpeed(attacker.state) / 2);
    const normalRemaining = attacker.state.movement_remaining_ft;
    attacker.state.movement_remaining_ft = allowance;
    try {
      return R().moveToward(sequence, round, attacker, defender, setup, 5, "forced",
        { ...options, disengaged: true });
    } finally {
      attacker.state.movement_remaining_ft = normalRemaining;
    }
  }

  window.IRON_PIT_BROWSER_BRUTAL_STRIKE = {
    advantageSuppression, bonusDamage, eligible, forceful, followForceful, hamstring,
    installAbilityHooks, resolveBeforeAttackRoll,
  };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();