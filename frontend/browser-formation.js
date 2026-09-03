(() => {
  "use strict";

  const HERO_BACK = 0;
  const HERO_FRONT = 5;
  const MONSTER_FRONT = 10;
  const MONSTER_BACK = 15;

  const attacks = (template) => template?.attacks || [];
  function hasRangedWeaponOffense(template) {
    return attacks(template).some((attack) => attack.kind === "ranged" && Number.isFinite(attack.long) && attack.long > 5);
  }
  function primaryWeaponIsRanged(template) {
    const primary = attacks(template).find((attack) => attack.id === template?.primary_attack_id) || attacks(template)[0];
    return primary?.kind === "ranged" && Number.isFinite(primary.long) && primary.long > 5;
  }
  function hasRangedSpellOffense(template) {
    if ((template?.spell_attack_actions || []).some((action) => action.attackKind === "ranged" && (action.range || 0) > 5)) return true;
    return (template?.spell_save_actions || []).some((action) => (action.range || 0) > 5);
  }
  function hasTrueRangeOffense(template) { return hasRangedWeaponOffense(template) || hasRangedSpellOffense(template); }
  function usesBackline(template) { return primaryWeaponIsRanged(template) || hasRangedSpellOffense(template); }

  function startingPosition(template, side) {
    const back = usesBackline(template);
    if (side === "heroes") return back ? HERO_BACK : HERO_FRONT;
    if (side === "monsters") return back ? MONSTER_BACK : MONSTER_FRONT;
    throw new Error(`Unknown encounter side: ${side}`);
  }

  function backlineHoldsPosition(member, setup) {
    if (!hasRangedWeaponOffense(member.state.template)) return false;
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    return !enemies.some((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.current_hp > 0
      && Math.abs(member.position_ft - enemy.position_ft) <= 5);
  }

  window.IRON_PIT_BROWSER_FORMATION = {
    hasRangedWeaponOffense, hasTrueRangeOffense, usesBackline, startingPosition, backlineHoldsPosition,
  };
})();
