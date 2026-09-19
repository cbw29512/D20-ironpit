(() => {
  "use strict";

  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function active(attacker, attack) {
    return W().active(attacker, attack, "Graze");
  }

  function rawDamage(attacker, attack) {
    try {
      if (!active(attacker, attack)) return null;
      const modifier = attack.attackAbilityModifier;
      if (!Number.isInteger(modifier)) {
        throw new Error(`Graze attack ${attack.id || attack.name} requires an explicit attack ability modifier.`);
      }
      return Math.max(0, modifier);
    } catch (error) {
      console.error("Graze mastery resolution failed.", error);
      throw error;
    }
  }

  function resolveMiss(ctx) {
    const outcome = O().requireOutcome(ctx);
    const raw = rawDamage(ctx.member.state, ctx.attack);
    if (raw === null) return null;
    const target = ctx.target.state;
    const appliedTotal = A().adjustedDamage(target, raw, ctx.attack.damageType, false);
    outcome.damageComponents = [{
      source: `${ctx.attack.name} (Graze)`, notation: String(raw), rolls: [], modifier: 0,
      damage_type: ctx.attack.damageType, total: raw, applied_total: appliedTotal,
    }];
    outcome.damageRoll = {
      notation: String(raw), rolls: [], modifier: 0, selected_roll: null, mode: "normal", total: appliedTotal,
    };
    const states = ctx.setup ? [...ctx.setup.heroes, ...ctx.setup.monsters].map((member) => member.state) : [];
    const appliedTypes = appliedTotal > 0 ? [ctx.attack.damageType] : [];
    outcome.damageOutcome = A().applyDamage(target, appliedTotal, false, appliedTypes, states);
    return O().noEventResult(ctx.sequence);
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Graze hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_MISS;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "graze-mastery")) return;
    hooks.registerAbility(phase, {
      id: "graze-mastery", priority: 10, rulesets: ["2024"],
      appliesTo: (member, ctx) => active(member.state, ctx.attack),
      resolve: resolveMiss,
    });
  }

  window.IRON_PIT_BROWSER_GRAZE = { active, installAbilityHooks, rawDamage, resolveMiss };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
})();
