from __future__ import annotations

from typing import Optional

from neoscore.core.has_music_font import HasMusicFont
from neoscore.core.music_font import MusicFont
from neoscore.core.music_text import MusicText
from neoscore.core.point import Point
from neoscore.core.positioned_object import PositionedObject
from neoscore.core.units import ZERO, Unit
from neoscore.western.meter import Meter, MeterDef


class TimeSignature(PositionedObject, HasMusicFont):

    """A graphical time signature.

    Note that these time signatures are purely cosmetic; they have no effect on
    automatic engraving since ``neoscore.western`` has no internal concept of measures.
    """

    # Type sentinel used to hackily check type
    # without importing the type, risking cyclic imports.
    _neoscore_time_signature_type_marker = True

    def __init__(
        self,
        pos_x: Unit,
        parent: PositionedObject,
        meter: MeterDef,
        font: Optional[MusicFont] = None,
    ):
        """
        Args:
            pos_x: The x position relative to the
                parent staff
            parent: If no font is given, this or one of its ancestors must
                implement ``HasMusicFont``.
            meter: The meter represented.
            font: If provided, this overrides any font found in the ancestor chain.
        """
        PositionedObject.__init__(self, Point(pos_x, ZERO), parent)
        if font is None:
            font = HasMusicFont.find_music_font(parent)
        self._music_font = font
        self._meter = Meter.from_def(meter)
        # Add one glyph for each digit
        self._upper_text = MusicText(
            (ZERO, font.unit(1)),
            self,
            self.meter.upper_text_glyph_names,
        )
        self._lower_text = MusicText(
            (ZERO, font.unit(3)),
            self,
            self.meter.lower_text_glyph_names,
        )
        self._position_glyphs()

    ######## PUBLIC PROPERTIES ########

    @property
    def music_font(self) -> MusicFont:
        return self._music_font

    @property
    def upper_text(self) -> MusicText:
        """MusicText: The upper glyph for the time signature"""
        return self._upper_text

    @property
    def lower_text(self) -> MusicText:
        """MusicText: The lower glyph for the time signature"""
        return self._lower_text

    @property
    def visual_width(self) -> Unit:
        """The visual width of the time signature.

        This is useful for laying out staff objects near time signatures.
        """
        return self._visual_width

    @property
    def meter(self) -> Meter:
        """The meter represented.

        Setting this will automatically update the time signature's glyphs.
        """
        return self._meter

    @meter.setter
    def meter(self, value: MeterDef):
        self._meter = Meter.from_def(value)
        self.upper_text.text = self._meter.upper_text_glyph_names
        self.lower_text.text = self._meter.lower_text_glyph_names
        self._position_glyphs()

    # TODO MEDIUM these glyph positions can probably be simplified now with proper
    # center-alignment support now

    def _position_glyphs(self):
        """This must be called after any modification to the glyph text"""
        # Vertically position
        if not self.meter.lower_text_glyph_names:
            self.upper_text.y = self.music_font.unit(2)
        else:
            self.upper_text.y = self.music_font.unit(1)
            self.lower_text.y = self.music_font.unit(3)
        # Horizontally position
        upper_width = self.upper_text.bounding_rect.width
        lower_width = self.lower_text.bounding_rect.width
        if upper_width > lower_width:
            self._visual_width = upper_width
            self.upper_text.x = ZERO
            self.lower_text.x += (upper_width - lower_width) / 2
        elif lower_width > upper_width:
            self._visual_width = lower_width
            self.lower_text.x = ZERO
            self.upper_text.x += (lower_width - upper_width) / 2
        else:
            # Widths are equal. No adjustment needed.
            self._visual_width = upper_width
        # Finally, if this time signature is placed at x=0 relative to a staff, adjust X
        # to fit the staff's fringe layout. This is rather hacky...
        staff = self.first_ancestor_with_attr("_neoscore_staff_type_marker")
        if staff and staff.descendant_pos_x(self) == ZERO:
            fringe_layout = staff.fringe_layout_at(None)
            x_offset = fringe_layout.time_signature
            self.upper_text.x += x_offset
            self.lower_text.x += x_offset
