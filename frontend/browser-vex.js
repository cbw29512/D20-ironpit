(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const EFFECT_ID = "weapon-mastery-vex";

  function active(attacker, attack) {
    return W().active(attacker, attack, "Vex");
  }

  function apply(attacker, attackerId, targetId, attack, round, damageDealt) {
    if (!(damageDealt > 0) || !active(attacker, attack)) return false;
    M().add(attacker, {
      id: `${attackerId}:${EFFECT_ID}:${targetId}`,
      source_id: attackerId,
      source_effect_id: EFFECT_ID,
      kind: "next-attack-against-advantage",
      target_id: targetId,
      expires_source_turn_end_round: round + 1,
    });
    return true;
  }

  function resolveHit(ctx) {
    const outcome = O().requireOutcome(ctx);
    outcome.vexApplied = apply(
      ctx.member.state, ctx.member.combatant_id, ctx.target.combatant_id,
      ctx.attack, ctx.round, outcome.damageRoll?.total || 0,
    );
    return outcome.vexApplied ? O().noEventResult(ctx.sequence) : null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Vex hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === EFFECT_ID)) return;
    hooks.registerAbility(phase, {
      id: EFFECT_ID, priority: 30, rulesets: ["2024"],
      appliesTo: (member, ctx) => active(member.state, ctx.attack),
      resolve: resolveHit,
    });
  }

  window.IRON_PIT_BROWSER_VEX = { active, apply, installAbilityHooks, resolveHit };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
