(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
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

  window.IRON_PIT_BROWSER_STUDIED_ATTACKS = { active, apply };
})();
