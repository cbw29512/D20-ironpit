(() => {
  "use strict";

  const HERO_BACK = 0;
  const HERO_FRONT = 5;
  const MONSTER_FRONT = 10;
  const MONSTER_BACK = 15;

  function usesBackline(template) {
    const primary = template?.attacks?.find((attack) => attack.id === template.primary_attack_id) || template?.attacks?.[0];
    if (primary?.kind === "ranged") return true;
    if (template?.kind === "character" && (template.spell_save_actions?.length || template.defensive_spell_actions?.length)) return true;
    return false;
  }

  function startingPosition(template, side) {
    const back = usesBackline(template);
    if (side === "heroes") return back ? HERO_BACK : HERO_FRONT;
    if (side === "monsters") return back ? MONSTER_BACK : MONSTER_FRONT;
    throw new Error(`Unknown encounter side: ${side}`);
  }

  window.IRON_PIT_BROWSER_FORMATION = {
    usesBackline,
    startingPosition,
  };
})();
