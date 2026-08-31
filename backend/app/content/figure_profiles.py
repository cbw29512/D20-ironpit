from __future__ import annotations

from typing import Literal, TypedDict

FigureForm = Literal[
    "aquatic-reptile", "bat", "bear", "bird", "brute", "centipede", "crab", "frog",
    "hippogriff", "hoofed", "humanoid", "insect", "plant", "primate", "pterosaur",
    "quadruped", "reptile", "snake", "spider", "theropod", "winged-insect",
]


class FigureProfile(TypedDict):
    form: FigureForm
    detail: str


def _p(form: FigureForm, detail: str) -> FigureProfile:
    return {"form": form, "detail": detail}


MONSTER_FIGURE_PROFILES: dict[str, FigureProfile] = {
    "Ankylosaurus": _p("reptile", "ankylosaurus"),
    "Archelon": _p("aquatic-reptile", "archelon"),
    "Awakened Shrub": _p("plant", "shrub"),
    "Axe Beak": _p("bird", "beak"),
    "Baboon": _p("primate", "baboon"),
    "Badger": _p("quadruped", "badger"),
    "Bandit": _p("humanoid", "bandit"),
    "Bat": _p("bat", "bat"),
    "Black Bear": _p("bear", "bear"),
    "Boar": _p("quadruped", "tusks"),
    "Brown Bear": _p("bear", "bear"),
    "Camel": _p("hoofed", "camel"),
    "Cat": _p("quadruped", "cat"),
    "Commoner": _p("humanoid", "commoner"),
    "Constrictor Snake": _p("snake", "snake"),
    "Crab": _p("crab", "crab"),
    "Crocodile": _p("reptile", "crocodile"),
    "Deer": _p("hoofed", "antlers"),
    "Dire Wolf": _p("quadruped", "canine"),
    "Draft Horse": _p("hoofed", "equine"),
    "Eagle": _p("bird", "raptor"),
    "Elk": _p("hoofed", "antlers"),
    "Frog": _p("frog", "frog"),
    "Giant Badger": _p("quadruped", "badger"),
    "Giant Bat": _p("bat", "bat"),
    "Giant Boar": _p("quadruped", "tusks"),
    "Giant Centipede": _p("centipede", "centipede"),
    "Giant Constrictor Snake": _p("snake", "snake"),
    "Giant Crab": _p("crab", "crab"),
    "Giant Crocodile": _p("reptile", "crocodile"),
    "Giant Eagle": _p("bird", "raptor"),
    "Giant Elk": _p("hoofed", "antlers"),
    "Giant Fire Beetle": _p("insect", "beetle"),
    "Giant Goat": _p("hoofed", "horns"),
    "Giant Lizard": _p("reptile", "lizard"),
    "Giant Owl": _p("bird", "owl"),
    "Giant Rat": _p("quadruped", "rodent"),
    "Giant Venomous Snake": _p("snake", "snake"),
    "Giant Wasp": _p("winged-insect", "wasp"),
    "Giant Weasel": _p("quadruped", "mustelid"),
    "Giant Wolf Spider": _p("spider", "spider"),
    "Goblin Minion": _p("humanoid", "goblin"),
    "Goblin Warrior": _p("humanoid", "goblin"),
    "Guard": _p("humanoid", "guard"),
    "Hawk": _p("bird", "raptor"),
    "Hippogriff": _p("hippogriff", "hippogriff"),
    "Hobgoblin Warrior": _p("humanoid", "hobgoblin"),
    "Hyena": _p("quadruped", "hyena"),
    "Jackal": _p("quadruped", "canine"),
    "Kobold Warrior": _p("humanoid", "kobold"),
    "Lizard": _p("reptile", "lizard"),
    "Mastiff": _p("quadruped", "canine"),
    "Mule": _p("hoofed", "equine"),
    "Ogre": _p("brute", "ogre"),
    "Owl": _p("bird", "owl"),
    "Owlbear": _p("bear", "owlbear"),
    "Panther": _p("quadruped", "cat"),
    "Plesiosaurus": _p("aquatic-reptile", "plesiosaur"),
    "Polar Bear": _p("bear", "bear"),
    "Pony": _p("hoofed", "equine"),
    "Pteranodon": _p("pterosaur", "pteranodon"),
    "Rat": _p("quadruped", "rodent"),
    "Raven": _p("bird", "corvid"),
    "Rhinoceros": _p("hoofed", "horn"),
    "Riding Horse": _p("hoofed", "equine"),
    "Saber-Toothed Tiger": _p("quadruped", "sabertooth"),
    "Scout": _p("humanoid", "scout"),
    "Tiger": _p("quadruped", "cat"),
    "Tyrannosaurus Rex": _p("theropod", "tyrannosaurus"),
    "Vulture": _p("bird", "vulture"),
    "Warhorse": _p("hoofed", "equine"),
    "Warrior Infantry": _p("humanoid", "infantry"),
    "Weasel": _p("quadruped", "mustelid"),
    "Wolf": _p("quadruped", "canine"),
}
