(() => {
  "use strict";
  // Custom characters reuse a certified RAW class/level snapshot. Neither the
  // name nor the browser library is allowed to alter combat abilities.
  const CLASSES = Object.freeze(["barbarian","bard","cleric","druid","fighter","monk",
    "paladin","ranger","rogue","sorcerer","warlock","wizard"]);
  const fields = new Set(["id","name","kind","ruleset","class_id","level","build_mode",
    "custom","coverage_status","runnable_template_id"]);
  const fail = message => {throw new Error("Custom pregen: " + message);};
  function compile(saved) {
    if (!saved || typeof saved !== "object" || Array.isArray(saved)) fail("invalid character.");
    for (const key of Object.keys(saved)) if (!fields.has(key)) fail("unsupported custom override: " + key);
    if (saved.kind !== "character" || saved.build_mode !== "canonical_raw_snapshot")
      fail("RAW class/level snapshot required; free-form character drafts cannot fight.");
    if (!["2014","2024"].includes(saved.ruleset) || !CLASSES.includes(saved.class_id))
      fail("unsupported edition or class.");
    if (!Number.isInteger(saved.level) || saved.level < 1 || saved.level > 20)
      fail("class level must be 1–20.");
    if (!/^[a-z0-9][a-z0-9-]*$/.test(saved.id || "") || typeof saved.name !== "string" ||
        !saved.name.trim() || saved.name.length > 100)
      fail("invalid name or card ID.");
    const matching = Object.values(window.IRON_PIT_BROWSER_HEROES || {}).filter(card =>
      card.ruleset === saved.ruleset && card.kind === "character" &&
      card.class_id === saved.class_id && card.level === saved.level);
    if (matching.length !== 1) fail("exactly one certified RAW class/level build must exist.");
    const template = structuredClone(matching[0]);
    template.id = "custom-pregen-" + saved.ruleset + "-" + saved.id;
    template.name = saved.name.trim();
    // All combat properties, features, ability scores, spells, resources, HP and
    // saves come unmodified from the certified snapshot.
    return template;
  }
  function decorate(saved) {
    if (saved.kind !== "character") return saved;
    try {
      const compiled_template = compile(saved);
      return {...saved,custom:true,class_name:compiled_template.archetype,
        archetype:compiled_template.archetype,coverage_status:"custom_ready",
        runnable_template_id:compiled_template.id,compiled_template};
    } catch (error) {
      return {...saved,custom:true,coverage_status:"custom_draft",
        runnable_template_id:null,compile_error:String(error.message || error)};
    }
  }
  const api={compile,decorate,classes:CLASSES};
  if (typeof module !== "undefined" && module.exports) module.exports=api;
  if (typeof window !== "undefined") window.IRON_PIT_CUSTOM_PREGEN_RUNTIME=api;
})();
