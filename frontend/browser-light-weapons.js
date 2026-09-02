(() => {
  "use strict";

  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const MARKER = "light-extra-attack";
  const NICK = "weapon-mastery-nick";

  function hasStyle(state, style) {
    const styles = state.template.fighting_styles || (state.template.fighting_style ? [state.template.fighting_style] : []);
    return styles.includes(style);
  }

  function nickActive(state, attack) {
    return Boolean(attack?.light && W().active(state, attack, "Nick"));
  }

  function used(state, turnKey) {
    return state.feature_last_turn_keys?.[MARKER] === turnKey;
  }

  function markUsed(state, turnKey) {
    state.feature_last_turn_keys ||= {};
    state.feature_last_turn_keys[MARKER] = turnKey;
  }

  function adjustedProfile(state, attack) {
    const modifier = attack.attackAbilityModifier;
    if (!Number.isInteger(modifier)) {
      console.error(`Light extra attack ${attack.id} requires an explicit attack ability modifier.`);
      throw new Error(`Light extra attack ${attack.id} has no attack ability modifier.`);
    }
    if (hasStyle(state, "Two-Weapon Fighting")) return { ...attack };
    return { ...attack, damageBonus: attack.damageBonus - Math.max(0, modifier) };
  }

  function plan(state, triggerAttack, turnKey) {
    if (!triggerAttack?.light || used(state, turnKey)) return null;
    const candidates = (state.template.attacks || []).filter((attack) =>
      attack.light && attack.weaponId !== triggerAttack.weaponId,
    );
    if (!candidates.length) return null;
    const nickCandidate = candidates.find((attack) => nickActive(state, attack));
    const chosen = nickCandidate || candidates[0];
    const nick = nickActive(state, triggerAttack) || nickActive(state, chosen);
    return {
      attack: adjustedProfile(state, chosen),
      usesBonusAction: !nick,
      featureId: nick ? NICK : MARKER,
    };
  }

  window.IRON_PIT_BROWSER_LIGHT_WEAPONS = {
    MARKER, NICK, adjustedProfile, hasStyle, markUsed, nickActive, plan, used,
  };
})();
