(() => {
  "use strict";
  const clone = (v) => structuredClone(v);
  function inheritWeaponHitTraitForForm(owner, form, profiles, rider, magicalWeapons) {
    if (owner?.kind !== "monster" || form?.kind !== "monster" ||
        owner.ruleset !== form.ruleset) {
      throw new Error("Inherited weapon trait requires same-edition monster sources.");
    }
    if (!rider || typeof rider.source !== "string" || !rider.source ||
        !Number.isInteger(rider.diceCount) || rider.diceCount < 1) {
      throw new Error("Weapon-hit rider needs explicit nonempty source and rolled damage.");
    }
    const ownerIds = new Set((owner.attacks || []).map((a) => a.id));
    const formIds = new Set((form.attacks || []).map((a) => a.id));
    if (!ownerIds.size || !formIds.size ||
        [...ownerIds].some((id) => formIds.has(id))) {
      throw new Error("Owner and acquired form weapon IDs must not collide.");
    }
    const rows = profiles || [];
    const seen = new Set(rows.map((a) => a.id));
    if (seen.size !== rows.length ||
        rows.length !== ownerIds.size + formIds.size ||
        [...seen].some((id) => !ownerIds.has(id) && !formIds.has(id))) {
      throw new Error("Source-validated owner and form attack inventory required.");
    }
    return rows.map((profile) => {
      const copy = clone(profile);
      if (ownerIds.has(profile.id)) return copy;
      const riders = copy.onHitDamage || [];
      const matches = riders.filter((part) => part.source === rider.source);
      if (matches.length && (matches.length !== 1 ||
          JSON.stringify(matches[0]) !== JSON.stringify(rider))) {
        throw new Error("Existing weapon-hit source conflicts with inherited trait.");
      }
      if (!matches.length) riders.push(clone(rider));
      copy.onHitDamage = riders;
      const qualifiers = copy.damageSourceQualifiers || [];
      if (magicalWeapons && !qualifiers.includes("magical")) qualifiers.push("magical");
      copy.damageSourceQualifiers = qualifiers;
      return copy;
    });
  }
  window.IRON_PIT_BROWSER_MONSTER_FORM_WEAPON_TRAITS = { inheritWeaponHitTraitForForm };
})();
