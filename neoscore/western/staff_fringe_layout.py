from dataclasses import dataclass

from neoscore.core.units import ZERO, Unit


@dataclass
class StaffFringeLayout:
    staff: Unit
    clef: Unit
    key_signature: Unit
    TimeSignature: Unit = ZERO
