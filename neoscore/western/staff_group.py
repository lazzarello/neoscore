from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from neoscore.core.layout_controllers import NewLine
from neoscore.core.units import ZERO, Unit
from neoscore.western.staff_fringe_layout import StaffFringeLayout

if TYPE_CHECKING:
    from neoscore.western.staff import Staff


class StaffGroup:

    # Padding on left side of staff before anything should come after it
    # (in pseudo-staff-units)
    LEFT_PADDING = 0.5
    # Padding to the right of the entire fringe
    RIGHT_PADDING = 1
    # Padding on either side of time signatures in fringes
    TIME_SIG_LEFT_PADDING = 0.5
    # PAdding to the left of key signatures in fringes
    KEY_SIG_LEFT_PADDING = 0.5

    def __init__(self) -> None:
        self._fringe_layout_cache: dict[
            tuple[Staff, Optional[NewLine]], StaffFringeLayout
        ] = {}
        self.staves: list[Staff] = []

    def fringe_layout_at(
        self, staff: Staff, location: Optional[NewLine]
    ) -> StaffFringeLayout:
        # If the layout is already cached, return it
        cached_value = self._fringe_layout_cache.get((staff, location))
        if cached_value:
            return cached_value
        # Work out the layouts of each staff in isolation first
        isolated_layouts = []
        min_staff_basis = ZERO  # Wider fringes give a lower number here (further left)
        for iter_staff in self.staves:
            layout = self._fringe_layout_for_isolated_staff(iter_staff, location)
            min_staff_basis = min(min_staff_basis, layout.staff)
            isolated_layouts.append((iter_staff, layout))
        # Then align each layout to fit the widest layout found, and store each in cache
        for iter_staff, isolated_layout in isolated_layouts:
            aligned_layout = self._align_layout(isolated_layout, min_staff_basis)
            self._fringe_layout_cache[(iter_staff, location)] = aligned_layout
        # Now the requested layout is cached, so return it
        return self._fringe_layout_cache[(staff, location)]

    def _align_layout(
        self, layout: StaffFringeLayout, staff_basis: Unit
    ) -> StaffFringeLayout:
        if layout.staff == staff_basis:
            return layout
        # Find the delta from the layout's staff basis to the alignment's
        # Note that these are all *negative* numbers
        delta = staff_basis - layout.staff
        return StaffFringeLayout(
            layout.pos_x_in_staff,
            # Staff, clef, and key signatures are left-aligned to widest fringe
            layout.staff + delta,
            layout.clef + delta,
            layout.key_signature + delta,
            # Time signatures are right-aligned
            layout.time_signature,
        )

    def _fringe_layout_for_isolated_staff(
        self, staff: Staff, location: Optional[NewLine]
    ) -> StaffFringeLayout:
        if location:
            staff_pos_x = location.flowable_x - staff.flowable.descendant_pos_x(staff)
            if staff_pos_x < ZERO:
                # This happens on the first line of a staff positioned at x>0 relative
                # to its flowable.
                staff_pos_x = ZERO
        else:
            staff_pos_x = ZERO
        # Work right-to-left through different fringe layers
        current_x = -staff.unit(StaffGroup.RIGHT_PADDING)
        clef = staff.active_clef_at(staff_pos_x)
        key_sig = staff.active_key_signature_at(staff_pos_x)
        time_sig = next(
            (sig for x, sig in staff.time_signatures if x == staff_pos_x), None
        )

        if (
            (not time_sig)
            and (clef.clef_type.glyph_name == "fClef")
            and staff_pos_x == ZERO
        ):
            print(staff.time_signatures)

        clef_fringe_pos = current_x
        key_signature_fringe_pos = current_x
        time_signature_fringe_pos = current_x

        if time_sig:
            current_x -= time_sig.visual_width
            time_signature_fringe_pos = current_x
            current_x -= staff.unit(StaffGroup.TIME_SIG_LEFT_PADDING)
        if key_sig:
            current_x -= key_sig.visual_width
            key_signature_fringe_pos = current_x
            current_x -= staff.unit(StaffGroup.KEY_SIG_LEFT_PADDING)
        if clef:
            current_x -= clef.bounding_rect.width
            clef_fringe_pos = current_x
        current_x -= staff.unit(StaffGroup.LEFT_PADDING)
        staff_fringe_pos = current_x
        return StaffFringeLayout(
            staff_pos_x,
            staff_fringe_pos,
            clef_fringe_pos,
            key_signature_fringe_pos,
            time_signature_fringe_pos,
        )
