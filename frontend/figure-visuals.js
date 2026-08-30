(() => {
  "use strict";

  const has = (name, pattern) => pattern.test(name);
  const EXPLICIT = new Map([
    ["owlbear", { form: "bear", detail: "owlbear" }],
    ["axe beak", { form: "bird", detail: "beak" }],
  ]);

  function inferredProfile(name) {
    let form = "humanoid", detail = "none";
    if (has(name, /wolf spider|spider/)) form = "spider";
    else if (has(name, /wasp/)) form = "winged-insect";
    else if (has(name, /centipede/)) form = "centipede";
    else if (has(name, /snake/)) form = "snake";
    else if (has(name, /crab/)) form = "crab";
    else if (has(name, /bat/)) form = "bat";
    else if (has(name, /axe beak|eagle|hawk|owl|vulture|raven|pteranodon/)) form = "bird";
    else if (has(name, /crocodile|lizard/)) form = "reptile";
    else if (has(name, /bear/)) form = "bear";
    else if (has(name, /frog/)) form = "frog";
    else if (has(name, /beetle/)) form = "insect";
    else if (has(name, /shrub/)) form = "plant";
    else if (has(name, /horse|pony|mule|camel|deer|elk|goat|rhinoceros/)) form = "hoofed";
    else if (has(name, /wolf|rat|weasel|badger|boar|tiger|panther|hyena|mastiff/)) form = "quadruped";
    else if (has(name, /ogre/)) form = "brute";

    if (has(name, /deer|elk/)) detail = "antlers";
    else if (has(name, /goat/)) detail = "horns";
    else if (has(name, /rhinoceros/)) detail = "horn";
    else if (has(name, /boar/)) detail = "tusks";
    else if (has(name, /tiger|panther/)) detail = "cat";
    else if (has(name, /wolf|hyena|mastiff/)) detail = "canine";
    else if (has(name, /axe beak/)) detail = "beak";
    return { form, detail };
  }

  function profile(template) {
    const name = String(template.name || "").toLowerCase();
    const visual = template.visual || {};
    const inferred = EXPLICIT.get(name) || inferredProfile(name);
    return {
      form: visual.figure_form || inferred.form,
      detail: visual.figure_detail || inferred.detail,
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
    node.dataset.figureForm = info.form;
    node.classList.toggle("pit-large", ["large", "huge", "gargantuan"].includes(info.size));
    node.classList.toggle("pit-small", ["tiny", "small"].includes(info.size));
  }

  window.IRON_PIT_FIGURE_VISUALS = { decorate, inferredProfile, profile };
})();
