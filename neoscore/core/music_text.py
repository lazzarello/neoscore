from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple, Optional, Type, cast

from neoscore.core.brush import BrushDef
from neoscore.core.has_music_font import HasMusicFont
from neoscore.core.music_char import MusicChar
from neoscore.core.music_font import MusicFont
from neoscore.core.pen import PenDef
from neoscore.core.point import PointDef
from neoscore.core.rect import Rect
from neoscore.core.text import Text
from neoscore.core.units import Unit

if TYPE_CHECKING:
    from neoscore.core.mapping import Parent


class _CachedTextGeometryKey(NamedTuple):
    text: str  # The key is the plain unicode text, not rich MusicChar list
    font: MusicFont
    scale: float


class _CachedTextGeometry(NamedTuple):
    bounding_rect: Rect


_GEOMETRY_CACHE: dict[_CachedTextGeometryKey, _CachedTextGeometry] = {}


class MusicText(Text, HasMusicFont):
    """
    A glyph with a MusicFont and convenient access to relevant SMuFL metadata.
    """

    # TODO MEDIUM find a way to type this text arg and/or simplify it
    def __init__(
        self,
        pos: PointDef,
        parent: Optional[Parent],
        text: Any,
        font: Optional[MusicFont] = None,
        brush: Optional[BrushDef] = None,
        pen: Optional[PenDef] = None,
        scale: float = 1,
        rotation: float = 0,
        background_brush: Optional[BrushDef] = None,
        z_index: int = 0,
        breakable: bool = True,
    ):
        """
        Args:
            pos: The position of the text.
            parent: The parent of the glyph. If no `font` is given,
                this or one of its ancestors must implement `HasMusicFont`.
            text (str, tuple, MusicChar, or list of these):
                The text to be used, represented as a either a `str`
                (glyph name), `tuple` (glyph name, alternate number),
                `MusicChar`, or a list of these. Empty text will fail.
            font: The music font to be used. If not specified,
                `parent` must be or have a `Staff` ancestor.
            brush: The brush to fill in text shapes with.
            pen: The pen to trace text outlines with. This defaults to no pen.
            scale: A scaling factor to be applied
                in addition to the size of the music font.
            rotation: Angle in degrees. Note that breakable rotated text is
                not currently supported.
            background_brush: Optional brush used to paint the text's bounding rect
                behind it.
            z_index: Controls draw order with higher values drawn first.
            breakable: Whether this object should break across lines in
                Flowable containers.
        """
        if font is None:
            font = HasMusicFont.find_music_font(parent)
        self._music_chars = MusicText._resolve_music_chars(text, font)
        resolved_str = MusicText._music_chars_to_str(self._music_chars)
        Text.__init__(
            self,
            pos,
            parent,
            resolved_str,
            font,
            brush,
            pen,
            scale,
            rotation,
            background_brush,
            z_index,
            breakable,
        )

    ######## PUBLIC PROPERTIES ########

    @property
    def music_chars(self) -> list[MusicChar]:
        """A list of the SMuFL characters in the string including metadata.

        If set, this will also update `self.text`.
        """
        return self._music_chars

    @music_chars.setter
    def music_chars(self, value: list[MusicChar]):
        self._music_chars = value
        self._text = MusicText._music_chars_to_str(value)

    @property
    def text(self) -> str:
        """The raw unicode representation of the SMuFL text.

        If set, this will also update `self.music_chars`
        """
        return self._text

    @text.setter
    # TODO MEDIUM when typing music text args update here as well
    def text(self, value):
        self._music_chars = MusicText._resolve_music_chars(value, self.music_font)
        resolved_str = MusicText._music_chars_to_str(self._music_chars)
        self._text = resolved_str

    @property
    def music_font(self) -> MusicFont:
        """The SMuFL font used in this text.

        This is an expressive synonym for the `font` field which implements the
        `HasMusicFont` mixin.
        """
        return cast(MusicFont, self._font)

    @music_font.setter
    def music_font(self, value: MusicFont):
        self._font = value

    @property
    def unit(self) -> Type[Unit]:
        return self.music_font.unit

    @property
    def bounding_rect(self) -> Rect:
        """The bounding rect for this text when rendered.

        Note that this currently accounts for scaling, but not rotation.
        """
        key = _CachedTextGeometryKey(self.text, self.music_font, self.scale)
        cached_result = _GEOMETRY_CACHE.get(key)
        if cached_result:
            return cached_result.bounding_rect
        bounding_rect = self.font.bounding_rect_of(self.text) * self.scale
        _GEOMETRY_CACHE[key] = _CachedTextGeometry(bounding_rect)
        return bounding_rect

    ######## PRIVATE METHODS ########

    @staticmethod
    def _music_chars_to_str(music_chars: list[MusicChar]) -> str:
        return "".join(char.codepoint for char in music_chars)

    @staticmethod
    def _resolve_music_chars(text: Any, font: MusicFont) -> list[MusicChar]:
        """
        Args:
            text (str, tuple, MusicChar, or list of these):
                The text to be used, represented as a either a `str`
                (glyph name), `tuple` (glyph name, alternate number),
                `MusicChar`, or a list of these.
            font: The font to be applied to the text
        """
        if isinstance(text, str):
            if text:
                return [MusicChar(font, text)]
            else:
                return []
        elif isinstance(text, tuple):
            return [MusicChar(font, *text)]
        elif isinstance(text, MusicChar):
            return [text]
        elif isinstance(text, list):
            music_chars = []
            for music_char in text:
                if isinstance(music_char, str):
                    music_chars.append(MusicChar(font, music_char))
                elif isinstance(music_char, tuple):
                    music_chars.append(MusicChar(font, *music_char))
                elif isinstance(music_char, MusicChar):
                    music_chars.append(music_char)
                else:
                    raise TypeError
            return music_chars
        else:
            raise TypeError
