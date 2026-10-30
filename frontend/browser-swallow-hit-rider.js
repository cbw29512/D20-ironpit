(() => {
  "use strict";

  function applyHit(ctx) {
    try {
      if (!ctx.preHitGrappledByAttacker) return null;
      const rule = (ctx.member.state.template.swallowActions || []).find((item) =>
        item.deliveryMode === "attack_hit" && item.attackId === ctx.attack.id
      );
      if (!rule) return null;

      const swallow = window.IRON_PIT_BROWSER_SWALLOW;
      const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
      if (!swallow?.swallowAfterBite || !outcome?.noEventResult) {
        throw new Error("Attack-hit Swallow requires shared Swallow and attack-outcome runtimes.");
      }
      const applied = swallow.swallowAfterBite(
        ctx.member.combatant_id,
        ctx.member.state,
        ctx.target.combatant_id,
        ctx.target.state,
        rule,
        true,
      );
      if (!applied) return null;

      for (const conditionId of ["blinded", "restrained"]) {
        if (!ctx.attackOutcome.appliedConditions.includes(conditionId)) {
          ctx.attackOutcome.appliedConditions.push(conditionId);
        }
      }
      return outcome.noEventResult(ctx.sequence);
    } catch (error) {
      console.error("Browser attack-hit Swallow delivery failed.", {
        attacker: ctx?.member?.combatant_id,
        target: ctx?.target?.combatant_id,
        attack: ctx?.attack?.id,
        error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Attack-hit Swallow requires browser-ability-hooks.js.");
      const phase = hooks.PHASES.ON_HIT;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "swallow-attack-hit")) return;
      hooks.registerAbility(phase, {
        id: "swallow-attack-hit",
        priority: 45,
        rulesets: ["2014", "2024"],
        appliesTo: (member, ctx) =>
          Boolean(ctx.preHitGrappledByAttacker)
          && (member.state.template.swallowActions || []).some((item) =>
            item.deliveryMode === "attack_hit" && item.attackId === ctx.attack.id
          ),
        resolve: applyHit,
      });
    } catch (error) {
      console.error("Browser attack-hit Swallow hook installation failed.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SWALLOW_HIT_RIDER = { applyHit, installAbilityHooks };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
