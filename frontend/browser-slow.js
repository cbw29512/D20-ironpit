(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const EFFECT_ID = "weapon-mastery-slow";

  function active(attacker, attack) {
    return W().active(attacker, attack, "Slow");
  }

  function apply(attacker, attackerId, target, attack) {
    if (!target || target.current_hp <= 0 || target.is_dead || !active(attacker, attack)) return false;
    M().add(target, {
      id: `${attackerId}:${EFFECT_ID}:${target.template.id}`,
      source_id: attackerId,
      source_effect_id: EFFECT_ID,
      source_name: "Slow",
      kind: "speed",
      flat_bonus: -10,
      expires_at_start_of_source_turn: true,
    });
    return true;
  }

  function resolveHit(ctx) {
    const outcome = O().requireOutcome(ctx);
    outcome.slowApplied = apply(
      ctx.member.state, ctx.member.combatant_id, ctx.target.state, ctx.attack,
    );
    return outcome.slowApplied ? O().noEventResult(ctx.sequence) : null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Slow hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === EFFECT_ID)) return;
    hooks.registerAbility(phase, {
      id: EFFECT_ID, priority: 28, rulesets: ["2024"],
      appliesTo: (member, ctx) => active(member.state, ctx.attack),
      resolve: resolveHit,
    });
  }

  window.IRON_PIT_BROWSER_SLOW = { active, apply, installAbilityHooks, resolveHit };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
