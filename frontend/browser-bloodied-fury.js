(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  function active(state, attack) {
    try {
      if (attack?.isSpellAttack || !state?.template?.traits?.includes("bloodied-fury") || attack?.kind !== "melee") return false;
      const maximum = S()?.effectiveMaxHp?.(state);
      if (!Number.isFinite(maximum) || maximum <= 0) throw new Error("Bloodied Fury requires an effective maximum HP value.");
      return state.current_hp * 2 <= maximum;
    } catch (error) {
      console.error("Browser Bloodied Fury eligibility failed", { combatant: state?.template?.id || state?.template?.name, attack: attack?.id, error });
      throw error;
    }
  }
  function resolveBeforeAttackRoll(ctx) {
    const api = ctx.attackRollApi;
    if (!api) throw new Error("Before-attack-roll hook requires attackRollApi.");
    const roll = api.requireContext(ctx);
    api.setAdvantageSource(roll, "bloodied-fury", active(ctx.member.state, ctx.attack) ? 1 : 0);
    return api.noEventResult(ctx.sequence);
  }
  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Bloodied Fury hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BEFORE_ATTACK_ROLL;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "bloodied-fury")) return;
    hooks.registerAbility(phase, {
      id: "bloodied-fury", priority: 30, rulesets: ["2024"],
      appliesTo: (member, ctx) => active(member.state, ctx.attack),
      resolve: resolveBeforeAttackRoll,
    });
  }
  window.IRON_PIT_BROWSER_BLOODIED_FURY = { active, installAbilityHooks, resolveBeforeAttackRoll };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();