(() => {
  "use strict";

  function applyHit(ctx) {
    try {
      const rule = (ctx.member.state.template.swallowActions || []).find((item) =>
        item.deliveryMode === "attack_hit" && item.attackId === ctx.attack.id
      );
      if (!rule) return null;
      if (rule.requiresExistingGrapple !== false && !ctx.preHitGrappledByAttacker) return null;
      if (rule.requiresExistingGrapple === false) {
        const sizes = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
        const targetSize = sizes.indexOf(ctx.target.state.template.size);
        const limit = sizes.indexOf(rule.maxTargetSize);
        if (targetSize < 0 || limit < 0) throw new Error("On-hit Swallow requires known size bounds.");
        if (targetSize > limit || ctx.target.state.is_dead || !ctx.target.state.is_alive
          || ctx.target.state.current_hp <= 0 || ctx.target.state.swallowed) return null;
        if (!rule.onHitSaveAbility || !Number.isInteger(rule.onHitSaveDc))
          throw new Error("Non-grapple attack-hit Swallow requires its printed saving throw.");
        const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
        if (!saves?.resolveSavingThrow) throw new Error("Swallow requires universal saving throw resolver.");
        if (ctx.attackOutcome.hitSave?.saveRoll)
          throw new Error("Attack cannot apply two unrelated on-hit saving throws.");
        const save = saves.resolveSavingThrow(
          ctx.target.state, rule.onHitSaveAbility, rule.onHitSaveDc,
          { roundNumber: ctx.round, encounterRoller: ctx.target, setup: ctx.setup },
        );
        ctx.attackOutcome.hitSave = {
          saveRoll: save.roll, saveAbility: rule.onHitSaveAbility,
          saveDc: rule.onHitSaveDc, saveSucceeded: save.succeeded,
        };
        if (save.succeeded) return null;
      }

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
          (member.state.template.swallowActions || []).some((item) =>
            item.deliveryMode === "attack_hit" && item.attackId === ctx.attack.id
            && (item.requiresExistingGrapple === false || Boolean(ctx.preHitGrappledByAttacker))
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
