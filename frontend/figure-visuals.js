(() => {
  "use strict";

  const has = (name, pattern) => pattern.test(name);
  const registry = () => window.IRON_PIT_MONSTER_FIGURE_PROFILES || {};
  const DIRECT_FORMS = new Set([
    "bat", "bear", "bird", "brute", "centipede", "crab", "frog", "gargoyle", "hoofed", "humanoid",
    "insect", "plant", "primate", "pterosaur", "quadruped", "reptile", "scorpion", "snake", "spider", "swarm",
    "theropod", "weapon", "winged-insect",
  ]);

  function inferredProfile(name) {
    let form = "humanoid", detail = "none";
    if (has(name, /wolf spider|spider/)) form = "spider";
    else if (has(name, /wasp/)) form = "winged-insect";
    else if (has(name, /centipede/)) form = "centipede";
    else if (has(name, /snake/)) form = "snake";
    else if (has(name, /crab/)) form = "crab";
    else if (has(name, /bat/)) form = "bat";
    else if (has(name, /eagle|hawk|owl|vulture|raven/)) form = "bird";
    else if (has(name, /crocodile|lizard|dragon/)) form = "reptile";
    else if (has(name, /bear/)) form = "bear";
    else if (has(name, /frog/)) form = "frog";
    else if (has(name, /beetle/)) form = "insect";
    else if (has(name, /shrub|tree|fungus/)) form = "plant";
    else if (has(name, /horse|pony|mule|camel|deer|elk|goat|rhinoceros/)) form = "hoofed";
    else if (has(name, /wolf|hound|rat|weasel|badger|boar|tiger|panther|hyena|mastiff/)) form = "quadruped";
    else if (has(name, /ogre|giant/)) form = "brute";
    if (has(name, /deer|elk/)) detail = "antlers";
    else if (has(name, /goat/)) detail = "horns";
    else if (has(name, /rhinoceros/)) detail = "horn";
    else if (has(name, /boar/)) detail = "tusks";
    else if (has(name, /tiger|panther/)) detail = "cat";
    else if (has(name, /wolf|hound|hyena|mastiff/)) detail = "canine";
    else if (has(name, /dragon/)) detail = "dragon";
    return { form, detail };
  }

  function sourceBackedProfile(template) {
    const name = String(template.name || "").toLowerCase();
    const type = String(template.creature_type || "").toLowerCase();
    const body = String(template.visual?.body_style || "").toLowerCase();
    const inferred = inferredProfile(name);
    if (DIRECT_FORMS.has(body)) return { form: body, detail: inferred.detail };
    if (body === "dragon" || type.includes("dragon")) return { form: "reptile", detail: "dragon" };
    if (body === "swarm" || name.startsWith("swarm of ")) return { form: "swarm", detail: inferred.detail };
    if (inferred.form !== "humanoid") return inferred;
    if (type.includes("humanoid")) return { form: "humanoid", detail: "humanoid" };
    if (type.includes("beast")) return { form: "quadruped", detail: "beast" };
    if (type.includes("plant")) return { form: "plant", detail: "plant" };
    if (type.includes("giant")) return { form: "brute", detail: "giant" };
    if (type.includes("construct")) return { form: "humanoid", detail: "construct" };
    if (type.includes("undead")) return { form: "humanoid", detail: "undead" };
    if (type) return { form: "brute", detail: type.split(" (")[0].replace(/\s+/g, "-") };
    return null;
  }

  function profile(template) {
    const name = String(template.name || "");
    const visual = template.visual || {};
    const reviewed = registry()[name] || null;
    let identity;
    let certified = false;
    if (visual.figure_form) {
      identity = { form: visual.figure_form, detail: visual.figure_detail || "none" };
      certified = true;
    } else if (template.kind === "monster" && reviewed) {
      identity = reviewed;
      certified = true;
    } else if (template.kind === "monster") {
      identity = sourceBackedProfile(template) || { form: "unknown", detail: "uncertified" };
      certified = identity.form !== "unknown";
    } else {
      identity = inferredProfile(name.toLowerCase());
    }
    return {
      ...identity,
      certified,
      size: String(template.size || "medium").toLowerCase(),
      weapon: String(visual.main_hand || template.attacks?.[0]?.name || "natural").toLowerCase(),
      offHand: String(visual.off_hand || "none").toLowerCase(),
      role: String(visual.role || template.archetype || "creature").toLowerCase(),
    };
  }

  function decorate(node, template) {
    const stick = node.querySelector(".stick-figure");
    if (!stick) return;
    const info = profile(template);
    stick.dataset.form = info.form;
    stick.dataset.detail = info.detail;
    stick.dataset.size = info.size;
    stick.dataset.weapon = info.weapon;
    stick.dataset.offHand = info.offHand;
    stick.dataset.role = info.role;
    stick.dataset.certified = info.certified ? "true" : "false";
    node.dataset.figureForm = info.form;
    node.dataset.figureCertified = info.certified ? "true" : "false";
    node.classList.toggle("pit-large", ["large", "huge", "gargantuan"].includes(info.size));
    node.classList.toggle("pit-small", ["tiny", "small"].includes(info.size));
  }

  window.IRON_PIT_FIGURE_VISUALS = { decorate, inferredProfile, profile, sourceBackedProfile };
})();
