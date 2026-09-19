(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const EFFECT_ID = "studied-attacks";

  function active(attacker) {
    return Boolean(attacker?.template?.studied_attacks);
  }

  function apply(attacker, attackerId, targetId, round) {
    if (!active(attacker)) return false;
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

  function resolveMiss(ctx) {
    const outcome = O().requireOutcome(ctx);
    outcome.studiedApplied = apply(
      ctx.member.state, ctx.member.combatant_id, ctx.originalTarget.combatant_id, ctx.round,
    );
    return outcome.studiedApplied ? O().noEventResult(ctx.sequence) : null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Studied Attacks hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_MISS;
    if (hooks.abilitiesFor(phase).some((item) => item.id === EFFECT_ID)) return;
    hooks.registerAbility(phase, {
      id: EFFECT_ID, priority: 20, rulesets: ["2024"],
      appliesTo: (member) => active(member.state),
      resolve: resolveMiss,
    });
  }

  window.IRON_PIT_BROWSER_STUDIED_ATTACKS = { active, apply, installAbilityHooks, resolveMiss };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
})();
