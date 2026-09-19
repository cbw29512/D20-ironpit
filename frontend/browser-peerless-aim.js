(() => {
  "use strict";
  const FEATURE = "boon-combat-prowess";

  function apply(attacker, hit, naturalOne, turnKey) {
    try {
      if (hit || naturalOne || !turnKey) return { hit, used: false };
      if (!attacker.state?.template?.peerless_aim) return { hit: false, used: false };
      attacker.state.feature_last_turn_keys ||= {};
      if (attacker.state.feature_last_turn_keys[FEATURE] === turnKey) return { hit: false, used: false };
      attacker.state.feature_last_turn_keys[FEATURE] = turnKey;
      return { hit: true, used: true };
    } catch (error) {
      console.error("Peerless Aim failed", attacker?.state?.template?.name, error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PEERLESS_AIM = { apply };
})();
