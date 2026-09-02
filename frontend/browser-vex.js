(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const EFFECT_ID = "weapon-mastery-vex";

  function active(attacker, attack) {
    return attack.masteryProperty === "Vex"
      && (attacker.template.weapon_masteries || []).includes(attack.weaponId);
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

  window.IRON_PIT_BROWSER_VEX = { active, apply };
})();
