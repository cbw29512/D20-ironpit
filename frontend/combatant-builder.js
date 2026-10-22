(() => {
  "use strict";
  const number = (values, key, low, high) => {
    const raw = values[key];
    if (raw == null || String(raw).trim() === "") throw new Error(key + " is required.");
    const n = Number(raw);
    if (!Number.isInteger(n) || n < low || n > high) throw new Error(key + " must be an integer between " + low + " and " + high + ".");
    return n;
  };
  const textValue = (values, key) => {
    const v = String(values[key] || "").trim();
    if (!v) throw new Error(key + " is required.");
    return v;
  };
  const makeDefinition = (values) => {
    const kind = textValue(values, "kind");
    if (!["monster", "character"].includes(kind)) throw new Error("Invalid combatant mode.");
    const ruleset = textValue(values, "ruleset");
    if (!["2014", "2024"].includes(ruleset)) throw new Error("Invalid ruleset.");
    const id = textValue(values, "id");
    const attackId = textValue(values, "attack_id");
    if (!/^[a-z0-9][a-z0-9-]*$/.test(id) || !/^[a-z0-9][a-z0-9-]*$/.test(attackId))
      throw new Error("IDs must use lowercase letters, digits and hyphens.");
    const size = textValue(values, "size").toLowerCase();
    if (!["tiny", "small", "medium", "large", "huge", "gargantuan"].includes(size))
      throw new Error("Invalid size.");
    const attack_kind = textValue(values, "attack_kind");
    if (!["melee", "ranged"].includes(attack_kind)) throw new Error("Invalid attack type.");
    const damage_type = textValue(values, "damage_type");
    if (!["slashing","piercing","bludgeoning","fire","cold","lightning","thunder","acid","poison","necrotic","radiant","psychic","force"].includes(damage_type))
      throw new Error("Unsupported damage type.");
    const base = {
      schema_version: 1,
      id, name: textValue(values, "name"), archetype: textValue(values, "archetype"),
      kind, ruleset, size,
      armor_class: number(values, "armor_class", 1, 99),
      max_hp: number(values, "max_hp", 1, 100000),
      speed_ft: number(values, "speed_ft", 0, 1000),
      initiative_bonus: number(values, "initiative_bonus", -50, 50),
      attacks: [{
        id: attackId, name: textValue(values, "attack_name"), attack_kind,
        attack_bonus: number(values, "attack_bonus", -50, 50),
        damage: {count: number(values, "damage_count", 1, 100), size: number(values, "damage_size", 2, 20), bonus: number(values, "damage_bonus", -100, 100)},
        damage_type,
        animation: attack_kind === "melee" ? "slash" : "projectile"
      }],
      primary_attack_id: attackId,
      source: "user-authored combatant builder draft"
    };
    if (values.creature_type && String(values.creature_type).trim()) base.creature_type = String(values.creature_type).trim();
    if (kind === "character") {
      base.level = number(values, "level", 1, 20);
      base.ability_scores = Object.fromEntries(
        ["strength","dexterity","constitution","intelligence","wisdom","charisma"].map(key => [key, number(values, key, 1, 30)])
      );
    }
    return base;
  };
  // Keep the compiler-independent data constructor available to Node tests.
  if (typeof module !== "undefined" && module.exports) module.exports = {makeDefinition};
  if (typeof document === "undefined") return;
  const form = document.getElementById("combatant-form");
  if (!form) return;
  const kind = document.getElementById("kind");
  const scores = document.getElementById("scores-group");
  const level = document.getElementById("level-label");
  const status = document.getElementById("status");
  const preview = document.getElementById("preview");
  const exportButton = document.getElementById("export");
  let draft = null;
  const changeMode = () => {
    const character = kind.value === "character";
    scores.hidden = !character;
    level.hidden = !character;
    document.getElementById("archetype-label").firstChild.textContent = character ? "Class / archetype" : "Type / archetype";
    draft = null;
    exportButton.disabled = true;
  };
  kind.addEventListener("change", changeMode);
  form.addEventListener("input", () => { draft = null; exportButton.disabled = true; });
  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      const values = Object.fromEntries(new FormData(form).entries());
      draft = makeDefinition(values);
      preview.textContent = JSON.stringify(draft, null, 2);
      status.dataset.error = "false";
      status.textContent = "Draft validated locally. Use the canonical compiler for full combat legality.";
      exportButton.disabled = false;
    } catch (error) {
      draft = null;
      exportButton.disabled = true;
      status.dataset.error = "true";
      status.textContent = error.message;
    }
  });
  exportButton.addEventListener("click", () => {
    if (!draft) return;
    const blob = new Blob([JSON.stringify(draft, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = draft.id + ".combatant.json";
    link.click();
    URL.revokeObjectURL(url);
  });
  changeMode();
})();
