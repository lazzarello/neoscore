from dataclasses import dataclass

from neoscore.core.units import ZERO, Unit


@dataclass
class StaffFringeLayout:
    pos_x_in_staff: Unit
    staff: Unit
    clef: Unit
    key_signature: Unit
    TimeSignature: Unit = ZERO
