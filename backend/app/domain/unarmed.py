from pydantic import BaseModel, Field


class UnarmedStrikeDamage(BaseModel):
    """2024 Unarmed Strike Damage option used by the Opportunity Attack fallback."""

    attack_bonus: int
    damage: int = Field(ge=0)
