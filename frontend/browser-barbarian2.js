(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const EFFECT_ID = "reckless-attack";

  function active(state) { return Boolean(state?.active_effect_ids?.includes(EFFECT_ID)); }
  function hasReckless(state) {
    return Boolean(state?.template?.reckless_attack || state?.template?.traits?.includes("reckless"));
  }
  function eligible(state, attack) {
    if (attack?.attackAbility !== "strength") return false;
    return state.template.ruleset !== "2014" || attack.kind === "melee";
  }

  function dangerSenseAdvantage(state, ability) {
    if (!state?.template?.danger_sense || ability !== "dexterity" || Q().incapacitated(state)) return 0;
    if (state.template.ruleset === "2014" && ["blinded", "deafened"].some((id) => state.active_effect_ids.includes(id))) return 0;
    return 1;
  }

  function activate(member, attack, round) {
    if (!member?.state || !hasReckless(member.state) || !eligible(member.state, attack) || active(member.state)) return false;
    const applied = T()?.apply(member.state, EFFECT_ID, member.combatant_id, {
      sourceEffectId: EFFECT_ID, appliedRound: round, expiresRound: round + 1, expiryTiming: "source_turn_start",
    });
    if (applied !== EFFECT_ID) throw new Error("Reckless Attack effect could not be applied.");
    return true;
  }

  function attackAdvantage(state, attack) { return Number(active(state) && eligible(state, attack)); }
  function attacksAgainstAdvantage(state) { return Number(active(state)); }

  function resolveBeforeAttackRoll(ctx) {
    const api = ctx.attackRollApi;
    if (!api) throw new Error("Before-attack-roll hook requires attackRollApi.");
    const roll = api.requireContext(ctx);
    const started = ctx.allowReckless === true && activate(ctx.member, ctx.attack, ctx.round);
    if (started) window.IRON_PIT_BROWSER_BARBARIAN3?.markRecklessUse(ctx.member.state, ctx.turnKey);
    api.setAdvantageSource(roll, "reckless-attacker", attackAdvantage(ctx.member.state, ctx.attack));
    api.setAdvantageSource(roll, "reckless-defender", attacksAgainstAdvantage(ctx.target.state));
    if (started) {
      roll.descriptionFragments.push(`${ctx.member.state.template.name} uses Reckless Attack.`);
      roll.aggregateFeatureId ||= EFFECT_ID;
    }
    return api.noEventResult(ctx.sequence);
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Reckless Attack hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BEFORE_ATTACK_ROLL;
    if (hooks.abilitiesFor(phase).some((item) => item.id === EFFECT_ID)) return;
    hooks.registerAbility(phase, {
      id: EFFECT_ID, priority: 10, rulesets: ["2014", "2024"],
      appliesTo: (member, ctx) => hasReckless(member.state) && eligible(member.state, ctx.attack),
      resolve: resolveBeforeAttackRoll,
    });
  }

  window.IRON_PIT_BROWSER_BARBARIAN2 = {
    active, activate, attackAdvantage, attacksAgainstAdvantage, dangerSenseAdvantage,
    eligible, hasReckless, installAbilityHooks, resolveBeforeAttackRoll,
  };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();