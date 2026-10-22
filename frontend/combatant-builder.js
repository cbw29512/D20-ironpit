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
      armor_class: number(values, "armor_class", kind === "monster" ? 0 : 1, 99),
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
    if (values.secondary_enabled === "on") {
      const secondId = textValue(values, "secondary_attack_id");
      if (!/^[a-z0-9][a-z0-9-]*$/.test(secondId) || secondId === attackId)
        throw new Error("Secondary attack needs a unique lowercase ID.");
      const secondKind = textValue(values, "secondary_attack_kind");
      const secondType = textValue(values, "secondary_damage_type");
      if (!["melee", "ranged"].includes(secondKind) ||
          !["slashing","piercing","bludgeoning","fire","cold","lightning","thunder","acid","poison","necrotic","radiant","psychic","force"].includes(secondType))
        throw new Error("Invalid secondary attack type.");
      base.attacks.push({
        id: secondId, name: textValue(values, "secondary_attack_name"),
        attack_kind: secondKind,
        attack_bonus: number(values, "secondary_attack_bonus", -50, 50),
        damage: {
          count: number(values, "secondary_damage_count", 1, 100),
          size: number(values, "secondary_damage_size", 2, 20),
          bonus: number(values, "secondary_damage_bonus", -100, 100)
        },
        damage_type: secondType,
        animation: secondKind === "melee" ? "slash" : "projectile"
      });
    }
    // Ordered effects are source declarations; the shared combat resolver executes them.
    const effects = values.on_hit_effects || [];
    if (!Array.isArray(effects) || effects.length > 12) throw new Error("Up to 12 on-hit effects are supported.");
    for (const [index, row] of effects.entries()) {
      if (!row || !["damage", "prone", "save_condition"].includes(row.kind))
        throw new Error("Unsupported on-hit effect at position " + (index + 1));
      const targetAttack = base.attacks.find(attack => attack.id === (row.attack_id || attackId));
      if (!targetAttack) throw new Error("Choose an existing attack for effect " + (index + 1));
      if (row.kind === "damage") {
        if (!["slashing","piercing","bludgeoning","fire","cold","lightning","thunder","acid","poison","necrotic","radiant","psychic","force"].includes(row.damage_type))
          throw new Error("Invalid chained damage type.");
        targetAttack.effects = targetAttack.effects || [];
        targetAttack.effects.push({
          kind: "damage", source: "on-hit-" + (index + 1),
          dice: {count: number(row, "count", 1, 100), size: number(row, "size", 2, 100), bonus: number(row, "bonus", -100, 100)},
          damage_type: row.damage_type
        });
      } else if (row.kind === "prone") {
        targetAttack.effects = targetAttack.effects || [];
        targetAttack.effects.push({kind: "prone"});
      } else {
        const conditions = ["blinded","charmed","deafened","frightened","grappled","incapacitated","invisible","paralyzed","petrified","poisoned","prone","restrained","stunned","unconscious"];
        if (!conditions.includes(row.condition)) throw new Error("Unsupported condition.");
        if (!["strength","dexterity","constitution","intelligence","wisdom","charisma"].includes(row.save_ability))
          throw new Error("Invalid save ability.");
        targetAttack.effects = targetAttack.effects || [];
        targetAttack.effects.push({
          kind: "save_condition", save_ability: row.save_ability,
          dc: number(row, "dc", 1, 40), condition: row.condition,
          duration_rounds: number(row, "duration_rounds", 1, 100800)
        });
      }
    }
    if (values.creature_type && String(values.creature_type).trim()) base.creature_type = String(values.creature_type).trim();
    if (kind === "character") {
      const classes = ["artificer","barbarian","bard","cleric","druid","fighter","monk","paladin","ranger","rogue","sorcerer","warlock","wizard"];
      if (!classes.includes(base.archetype.toLowerCase()))
        throw new Error("Choose a supported base class for a pregen.");
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
  const saveButton = document.getElementById("save-custom");
  let draft = null;
  const changeMode = () => {
    const character = kind.value === "character";
    scores.hidden = !character;
    level.hidden = !character;
    document.getElementById("archetype-label").firstChild.textContent = character ? "Class / archetype" : "Type / archetype";
    const monsterArchetype = document.getElementById("monster-archetype");
    const characterClass = document.getElementById("character-class");
    monsterArchetype.hidden = character;
    monsterArchetype.disabled = character;
    monsterArchetype.required = !character;
    characterClass.hidden = !character;
    characterClass.disabled = !character;
    characterClass.required = character;
    characterClass.name = character ? "archetype" : "";
    document.querySelector('[name="armor_class"]').min = character ? "1" : "0";
    draft = null;
    exportButton.disabled = true;
    if (saveButton) saveButton.disabled = true;
  };
  const secondaryToggle = document.querySelector('[name="secondary_enabled"]');
  const secondaryFields = document.getElementById("secondary-attack-fields");
  secondaryToggle.addEventListener("change", () => {
    secondaryFields.hidden = !secondaryToggle.checked;
    document.querySelectorAll("#effect-list [data-effect-row]").forEach(row => {
      const selector = row.querySelector('[data-field="attack_id"]');
      const other = selector?.querySelector('option[value="__secondary__"]');
      if (other) other.disabled = !secondaryToggle.checked;
      if (!secondaryToggle.checked && selector?.value === "__secondary__") selector.value = "__primary__";
    });
    draft = null;
    exportButton.disabled = true;
    if (saveButton) saveButton.disabled = true;
  });
  const invalidateDraft = () => {
    draft = null;
    exportButton.disabled = true;
    if (saveButton) saveButton.disabled = true;
  };
  const effectList = document.getElementById("effect-list");
  const addEffect = document.getElementById("add-effect");
  if (effectList && addEffect) addEffect.addEventListener("click", () => {
    if (effectList.children.length >= 12) return;
    invalidateDraft();
    const row = document.createElement("div");
    row.dataset.effectRow = "true";
    row.className = "effect-row";
    row.innerHTML = '<label>Attack<select data-field="attack_id"><option value="__primary__">Primary attack</option><option value="__secondary__">Second attack</option></select></label>' +
      '<label>Effect type<select data-field="kind"><option value="damage">Additional damage</option><option value="prone">Knock Prone</option><option value="save_condition">Save or condition</option></select></label>' +
      '<label>Damage type<select data-field="damage_type">' + ["acid","bludgeoning","cold","fire","force","lightning","necrotic","piercing","poison","psychic","radiant","slashing","thunder"].map(x=>'<option>'+x+'</option>').join("") + '</select></label>' +
      '<label>Dice count<input data-field="count" type="number" min="1" value="1"></label>' +
      '<label>Die size<select data-field="size"><option>4</option><option selected>6</option><option>8</option><option>10</option><option>12</option><option>20</option></select></label>' +
      '<label>Damage bonus<input data-field="bonus" type="number" value="0"></label>' +
      '<label>Save ability<select data-field="save_ability">' + ["strength","dexterity","constitution","intelligence","wisdom","charisma"].map(x=>'<option>'+x+'</option>').join("") + '</select></label>' +
      '<label>Save DC<input data-field="dc" type="number" min="1" max="40" value="12"></label>' +
      '<label>Condition<select data-field="condition">' + ["blinded","charmed","deafened","frightened","grappled","incapacitated","invisible","paralyzed","petrified","poisoned","prone","restrained","stunned","unconscious"].map(x=>'<option>'+x+'</option>').join("") + '</select></label>' +
      '<label>Duration (rounds)<input data-field="duration_rounds" type="number" min="1" value="1"></label>' +
      '<button type="button" class="secondary" data-remove>Remove effect</button>';
    const refresh = () => {
      const secondaryOption = row.querySelector('[data-field="attack_id"] option[value="__secondary__"]');
      secondaryOption.disabled = !secondaryToggle.checked;
      if (!secondaryToggle.checked && row.querySelector('[data-field="attack_id"]').value === "__secondary__")
        row.querySelector('[data-field="attack_id"]').value = "__primary__";
      const selected = row.querySelector('[data-field="kind"]').value;
      for (const field of ["damage_type","count","size","bonus","save_ability","dc","condition","duration_rounds"]) {
        const el = row.querySelector('[data-field="' + field + '"]');
        el.parentElement.hidden = selected === "prone" ||
          (selected === "damage" && ["save_ability","dc","condition","duration_rounds"].includes(field)) ||
          (selected === "save_condition" && ["damage_type","count","size","bonus"].includes(field));
      }
    };
    row.querySelector('[data-field="kind"]').addEventListener("change", () => { refresh(); invalidateDraft(); });
    row.querySelector("[data-remove]").addEventListener("click", () => { row.remove(); invalidateDraft(); });
    effectList.appendChild(row);
    refresh();
  });
  const pageMode = window.location.pathname.endsWith("custom-monster-builder.html") ? "monster"
    : window.location.pathname.endsWith("custom-pregen-builder.html") ? "character" : null;
  if (pageMode) {
    kind.value = pageMode;
    kind.disabled = true;
  }
  kind.addEventListener("change", changeMode);
  form.addEventListener("input", () => { draft = null; exportButton.disabled = true; });
  form.addEventListener("submit", event => {
    event.preventDefault();
    try {
      const values = Object.fromEntries(new FormData(form).entries());
      if (pageMode) values.kind = pageMode;
      values.on_hit_effects = Array.from(document.querySelectorAll("#effect-list [data-effect-row]"), row => {
        const read = name => row.querySelector('[data-field="' + name + '"]')?.value;
        return {kind: read("kind"), attack_id: read("attack_id") === "__secondary__" ? values.secondary_attack_id : values.attack_id, damage_type: read("damage_type"),
          count: read("count"), size: read("size"), bonus: read("bonus"),
          save_ability: read("save_ability"), dc: read("dc"),
          condition: read("condition"), duration_rounds: read("duration_rounds")};
      });
      draft = makeDefinition(values);
      preview.textContent = JSON.stringify(draft, null, 2);
      status.dataset.error = "false";
      status.textContent = draft.kind === "character" ? "Character draft only: RAW class progression, proficiency, saves, damage, and feature legality require the edition-specific character builder before combat use." : "Homebrew draft validated locally. Use the canonical compiler for full combat legality.";
      exportButton.disabled = false;
      if (saveButton) saveButton.disabled = false;
    } catch (error) {
      draft = null;
      exportButton.disabled = true;
    if (saveButton) saveButton.disabled = true;
      status.dataset.error = "true";
      status.textContent = error.message;
    }
  });
  if (saveButton) saveButton.addEventListener("click", () => {
    if (!draft) return;
    try {
      const library = window.IRON_PIT_CUSTOM_LIBRARY;
      if (!library) throw new Error("Custom library is unavailable.");
      library.save(draft);
      status.dataset.error = "false";
      status.textContent = draft.name + " saved to Custom " + (draft.kind === "monster" ? "Monsters" : "Pregens") + ". This draft is not combat-certified yet.";
    } catch (error) {
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
