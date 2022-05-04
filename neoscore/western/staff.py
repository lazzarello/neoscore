from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, cast

from neoscore.core.exceptions import NoClefError
from neoscore.core.has_music_font import HasMusicFont
from neoscore.core.layout_controllers import MarginController, NewLine
from neoscore.core.music_font import MusicFont
from neoscore.core.painted_object import PaintedObject
from neoscore.core.path import Path
from neoscore.core.pen import Pen, PenDef
from neoscore.core.point import Point, PointDef
from neoscore.core.positioned_object import PositionedObject
from neoscore.core.units import ZERO, Mm, Unit, make_unit_class
from neoscore.western.staff_fringe_layout import StaffFringeLayout

if TYPE_CHECKING:
    from neoscore.western.clef import Clef
    from neoscore.western.key_signature import KeySignature


class Staff(PaintedObject, HasMusicFont):
    """A staff with decently high-level knowledge of its contents."""

    # Type sentinel used to hackily check if objects are Staff
    # without importing the type, risking cyclic imports.
    _neoscore_staff_type_marker = True

    # Padding on left side of staff before anything should come after it
    # (in pseudo-staff-units)
    _LEFT_PADDING = 0.5

    def __init__(
        self,
        pos: PointDef,
        parent: Optional[PositionedObject],
        length: Unit,
        line_spacing: Unit = Mm(1.75),
        line_count: int = 5,
        music_font_family: str = "Bravura",
        pen: Optional[PenDef] = None,
    ):
        """
        Args:
            pos: The position of the top-left corner of the staff
            parent: The parent for the staff. Make this a ``Flowable``
                to allow the staff to run across line and page breaks.
            length: The horizontal width of the staff
            line_spacing: The distance between two lines in the staff.
            line_count: The number of lines in the staff.
            music_font_family: The name of the font to use for MusicText objects
                in the staff. This defaults to the system-wide default music font
                family.
            pen: The pen used to draw the staff lines. Defaults to a line with
                thickness from the music font's engraving default.
        """
        unit = self._make_unit_class(line_spacing)
        self._music_font = MusicFont(music_font_family, unit)
        pen = pen or Pen(
            thickness=self._music_font.engraving_defaults["staffLineThickness"]
        )
        PaintedObject.__init__(self, pos, parent, pen=pen)
        self._line_count = line_count
        self._length = length
        self._fringe_layouts = {}

    ######## PUBLIC PROPERTIES ########

    @property
    def music_font(self) -> MusicFont:
        return self._music_font

    @property
    def height(self) -> Unit:
        """The height of the staff from top to bottom line.

        If the staff only has one line, its height is defined as 0.
        """
        return self.unit(self.line_count - 1)

    @property
    def line_count(self) -> int:
        """The number of lines in the staff"""
        return self._line_count

    @property
    def center_y(self) -> Unit:
        """The position of the center staff position"""
        return self.height / 2

    @property
    def barline_extent(self) -> tuple[Unit, Unit]:
        """The starting and stopping Y positions of barlines in this staff.

        For staves with more than 1 line, this extends from the top line to bottom
        line. For single-line staves, this extends from 1 unit above and below the
        staff.
        """
        if self.line_count == 1:
            return self.unit(-1), self.unit(1)
        else:
            return ZERO, self.height

    @property
    def breakable_length(self) -> Unit:
        # Override expensive ``Path.length`` since the staff length here
        # is already known.
        return self._length

    ######## PUBLIC METHODS ########

    def distance_to_next_of_type(self, staff_object: PositionedObject) -> Unit:
        """Find the x distance until the next occurrence of an object's type.

        If the object is the last of its type, this gives the remaining length
        of the staff after the object.

        This is useful for determining rendering behavior of staff objects
        which are active until another of their type occurs,
        such as ``KeySignature`` and ``Clef``.
        """
        start_x = self.map_x_to(cast(PositionedObject, staff_object))
        all_others_of_class = (
            item
            for item in self.descendants_of_exact_class(type(staff_object))
            if item != staff_object
        )
        closest_x = Unit(float("inf"))
        for item in all_others_of_class:
            relative_x = self.map_x_to(item)
            if start_x < relative_x < closest_x:
                closest_x = relative_x
        if closest_x == Unit(float("inf")):
            return self.breakable_length - start_x
        return closest_x - start_x

    def clefs(self) -> list[tuple[Unit, Clef]]:
        """All the clefs in this staff, ordered by their relative x pos."""
        cached_clef_positions = getattr(self, "_clef_x_positions", None)
        if cached_clef_positions:
            return cached_clef_positions
        result = [
            (clef.pos_x_in_staff, clef)
            for clef in self.descendants_with_attribute("middle_c_staff_position")
        ]
        result.sort(key=lambda tup: tup[0])
        self._clef_x_positions = result
        return result

    def active_clef_at(self, pos_x: Unit) -> Optional[Clef]:
        """Return the active clef at a given x position, if any."""
        clefs = self.clefs()
        return next(
            (clef for (clef_x, clef) in reversed(clefs) if clef_x <= pos_x),
            None,
        )

    def key_signatures(self) -> list[tuple[Unit, KeySignature]]:
        """All the key signatures in this staff, ordered by their relative x pos."""
        cached_clef_positions = getattr(self, "_key_signature_x_positions", None)
        if cached_clef_positions:
            return cached_clef_positions
        result = [
            (sig.pos_x_in_staff, sig)
            for sig in self.descendants_with_attribute(
                "_neoscore_key_signature_type_marker"
            )
        ]
        result.sort(key=lambda tup: tup[0])
        self._key_signature_x_positions = result
        return result

    def active_key_signature_at(self, pos_x: Unit) -> Optional[KeySignature]:
        """Return the active key signature at a given x position, if any."""

        sigs = self.key_signatures()
        return next(
            (sig for (sig_x, sig) in reversed(sigs) if sig_x <= pos_x),
            None,
        )

    def middle_c_at(self, pos_x: Unit) -> Unit:
        """Find the y-axis staff position of middle-c at a given point.

        Looks for clefs and other transposing modifiers to determine
        the position of middle-c.

        If no clef is present, a ``NoClefError`` is raised.
        """
        clef = self.active_clef_at(pos_x)
        if clef is None:
            raise NoClefError
        return clef.middle_c_staff_position

    def y_inside_staff(self, pos_y: Unit) -> bool:
        """Determine if a y-axis position is inside the staff.

        This is true for any position within or on the outer lines.
        """
        return ZERO <= pos_y <= self.height

    def y_on_ledger(self, pos_y: Unit) -> bool:
        """Determine if a y-axis position is approximately at a ledger line position

        This is true for any whole-number staff position outside of the staff
        """
        return (not self.y_inside_staff(pos_y)) and self.unit(
            pos_y
        ).display_value % 1 == 0

    def ledgers_needed_for_y(self, position: Unit) -> list[Unit]:
        """Find the y positions of all ledgers needed for a given y position"""
        # Work on positions as integers for simplicity
        start = int(self.unit(position).display_value)
        if start < 0:
            return [self.unit(pos) for pos in range(start, 0, 1)]
        elif start > self.line_count - 1:
            return [self.unit(pos) for pos in range(start, self.line_count - 1, -1)]
        else:
            return []

    def fringe_layout_at(self, location: Optional[NewLine]) -> StaffFringeLayout:
        if location:
            cached_result = self._fringe_layouts.get(location)
            if cached_result:
                return cached_result
            line_staff_pos_x = location.flowable_x - self.flowable.descendant_pos_x(
                self
            )
            layout = self._fringe_layout_at_staff_pos_x(line_staff_pos_x)
            self._fringe_layouts[location] = layout
            return layout
        return self._fringe_layout_at_staff_pos_x(ZERO)

    def render_slice(
        self,
        pos: Point,
        clip_start_x: Optional[Unit],
        clip_width: Optional[Unit],
        flowable_line: Optional[NewLine],
    ):
        fringe_layout = self.fringe_layout_at(flowable_line or ZERO)
        if clip_width is None:
            if clip_start_x is None:
                slice_length = self.breakable_length
            else:
                slice_length = self.breakable_length - clip_start_x
        else:
            slice_length = clip_width
        path = self._create_staff_segment_path(
            Point(pos.x + fringe_layout.staff, pos.y),
            slice_length - fringe_layout.staff,
        )
        path.render()
        path.remove()

    def render_complete(
        self,
        pos: Point,
        flowable_line: Optional[NewLine] = None,
        flowable_x: Optional[Unit] = None,
    ):
        self.render_slice(pos, None, None, flowable_line)

    def render_before_break(self, pos: Point, flowable_line: NewLine, flowable_x: Unit):
        self.render_slice(
            pos,
            ZERO,
            flowable_line.flowable_x + flowable_line.length - flowable_x,
            flowable_line,
        )

    def render_spanning_continuation(
        self, pos: Point, flowable_line: NewLine, object_x: Unit
    ):
        self.render_slice(pos, object_x, flowable_line.length, flowable_line)

    def render_after_break(self, pos: Point, flowable_line: NewLine, object_x: Unit):
        self.render_slice(pos, object_x, None, flowable_line)

    ######## PRIVATE METHODS ########

    def _fringe_layout_at_staff_pos_x(self, pos_x: Unit) -> StaffFringeLayout:
        clef = self.active_clef_at(pos_x)
        key_sig = self.active_key_signature_at(pos_x)
        clef_width = clef.bounding_rect.width if clef else ZERO
        time_signature_fringe_pos = ZERO  # TODO
        key_signature_fringe_pos = time_signature_fringe_pos - key_sig.visual_width
        clef_fringe_pos = key_signature_fringe_pos - clef_width
        staff_fringe_pos = clef_fringe_pos - self.unit(Staff._LEFT_PADDING)
        return StaffFringeLayout(
            pos_x, staff_fringe_pos, clef_fringe_pos, key_signature_fringe_pos, ZERO
        )

    def _create_staff_segment_path(self, doc_pos: Point, length: Unit) -> Path:
        path = Path(doc_pos, None, pen=self.pen)
        for i in range(self.line_count):
            y_offset = self.unit(i)
            path.move_to(ZERO, y_offset)
            path.line_to(length, y_offset)
        return path

    @staticmethod
    def _make_unit_class(staff_unit_size: Unit) -> Type[Unit]:
        """Create a Unit class with a ratio of 1 to a staff unit size

        Args:
            staff_unit_size

        Returns:
            type: A new StaffUnit class specifically for use in this staff.
        """

        return make_unit_class("StaffUnit", staff_unit_size.base_value)

    def _register_layout_controllers(self):
        flowable = self.flowable
        if not flowable:
            return
        staff_flowable_x = flowable.descendant_pos_x(self)
        flowable.add_margin_controller(
            MarginController(
                staff_flowable_x, self.unit(Staff._LEFT_PADDING), "neoscore_staff"
            )
        )
        for clef_x, clef in self._clef_x_positions:
            flowable_x = staff_flowable_x + clef_x
            margin_needed = clef.bounding_rect.width
            flowable.add_margin_controller(
                MarginController(flowable_x, margin_needed, "neoscore_clef")
            )
        # Assume that in key signatures have the same width in all clefs
        for keysig in self.descendants_with_attribute(
            "_neoscore_key_signature_type_marker"
        ):
            flowable_x = staff_flowable_x + keysig.x
            flowable.add_margin_controller(
                MarginController(flowable_x, keysig.visual_width, "neoscore_keysig")
            )

    def pre_render_hook(self):
        # TODO do these need to be cleaned up after rendering?
        self._register_layout_controllers()
