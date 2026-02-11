"""
Scout Smelting Loop - Refining Raw Data into Intent.

The Smelting Loop is the metabolic process that transforms raw conversation
logs (the "Data Ghost") into structured strategic intent.

HOLD₁ (Input) → Raw conversation logs
AGENT (Scout) → Context Filter with Struggle Filter
HOLD₂ (Output) → strategic_intent.yaml

Scout (Capacity) absorbs the noise of your life.
Maverick (Capability) only sees the signal of your intent.
"""

from sovereign.smelter.filter import StruggleFilter
from sovereign.smelter.loop import SmeltingLoop


__all__ = ["SmeltingLoop", "StruggleFilter"]
