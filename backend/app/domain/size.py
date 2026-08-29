from enum import StrEnum


class CreatureSize(StrEnum):
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


_SIZE_RANK = {
    CreatureSize.TINY: 0,
    CreatureSize.SMALL: 1,
    CreatureSize.MEDIUM: 2,
    CreatureSize.LARGE: 3,
    CreatureSize.HUGE: 4,
    CreatureSize.GARGANTUAN: 5,
}


def size_at_most(size: CreatureSize, maximum: CreatureSize) -> bool:
    return _SIZE_RANK[size] <= _SIZE_RANK[maximum]
