from __future__ import annotations

"""Foundation notes for 2014 mechanic:spellcasting batch 1.

33 monsters remain in this category. Related open work:
- #1081 prepared monster spells pregen adapter
- #1049 Pit Fiend innate spellcasting structure
- #935 spellcasting one-slot gate foundation

Targets for subsequent wiring (foundations only):
- Acolyte, Archmage, Cult Fanatic, Druid, Flameskull, Mage, Priest, Spirit Naga
- Cloud Giant, Couatl, Deva, Djinni, Drider, Drow, Dryad, Efreeti, Glabrezu
- Green Hag, Guardian Naga, Gynosphinx, Ice Mephit, Lamia, Lich, Magma Mephit
- Night Hag, Oni, Planetar, Rakshasa, Solar, Storm Giant

No admission claims. Exact-head CI required.
"""


def spellcasting_batch_1_targets() -> list[str]:
    return [
        "Acolyte",
        "Archmage",
        "Cult Fanatic",
        "Druid",
        "Flameskull",
        "Mage",
        "Priest",
        "Spirit Naga",
        "Cloud Giant",
        "Couatl",
        "Deva",
        "Djinni",
        "Drider",
        "Drow",
        "Dryad",
        "Efreeti",
        "Glabrezu",
        "Green Hag",
        "Guardian Naga",
        "Gynosphinx",
        "Ice Mephit",
        "Lamia",
        "Lich",
        "Magma Mephit",
        "Night Hag",
        "Oni",
        "Planetar",
        "Rakshasa",
        "Solar",
        "Storm Giant",
    ]
