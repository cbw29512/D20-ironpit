(() => {
  "use strict";

  const has = (name, pattern) => pattern.test(name);

  function profile(template) {
    const name = String(template.name || "").toLowerCase();
    const visual = template.visual || {};
    let form = "humanoid", detail = "none";

    if (has(name, /centipede/)) form = "centipede";
    else if (has(name, /snake/)) form = "snake";
    else if (has(name, /crab/)) form = "crab";
    else if (has(name, /bat/)) form = "bat";
    else if (has(name, /eagle|hawk|owl|vulture|raven|pteranodon/)) form = "bird";
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

    return {
      form,
      detail,
      size: template.size || "medium",
      weapon: visual.main_hand || template.attacks?.[0]?.name?.toLowerCase() || "natural",
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
    node.dataset.figureForm = info.form;
    node.classList.toggle("pit-large", ["large", "huge", "gargantuan"].includes(info.size));
    node.classList.toggle("pit-small", ["tiny", "small"].includes(info.size));
  }

  window.IRON_PIT_FIGURE_VISUALS = { decorate, profile };
})();
