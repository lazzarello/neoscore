import unittest

from neoscore import constants
from neoscore.core import neoscore
from neoscore.core.invisible_object import InvisibleObject
from neoscore.core.music_char import MusicChar
from neoscore.core.music_font import MusicFont
from neoscore.core.music_text import MusicText
from neoscore.core.staff import Staff
from neoscore.utils.units import GraphicUnit, Mm, Unit


class TestMusicText(unittest.TestCase):
    def setUp(self):
        neoscore.setup()
        self.staff = Staff((Mm(0), Mm(0)), None, length=Mm(100), staff_unit=Mm(1))
        self.font = MusicFont(constants.DEFAULT_MUSIC_FONT_NAME, self.staff.unit)

    def test_init(self):
        mock_parent = InvisibleObject((Unit(10), Unit(11)), parent=self.staff)
        mtext = MusicText((Unit(5), Unit(6)), mock_parent, "accidentalFlat", self.font)
        assert mtext.x == GraphicUnit(5)
        assert mtext.y == GraphicUnit(6)
        assert mtext.text == "\ue260"
        assert mtext.font == self.font
        assert mtext.parent == mock_parent

    def test_init_with_one_tuple(self):
        mtext = MusicText((Unit(5), Unit(6)), self.staff, ("brace", 1))
        assert mtext.text == "\uF400"

    def test_init_with_one_music_char(self):
        mtext = MusicText(
            (Unit(5), Unit(6)), self.staff, MusicChar(self.staff.music_font, "brace", 1)
        )
        assert mtext.text == "\uF400"

    def test_init_with_multiple_chars_in_list(self):
        mtext = MusicText(
            (Unit(5), Unit(6)), self.staff, ["accidentalFlat", ("brace", 1)]
        )
        assert mtext.text == "\ue260\uF400"

    def test_text_setter(self):
        mtext = MusicText((Unit(5), Unit(6)), self.staff, "accidentalSharp")
        assert mtext.text == "\ue262"
        mtext.text = "accidentalFlat"
        assert mtext.text == "\ue260"
        assert mtext.music_chars == [MusicChar(self.font, "accidentalFlat")]

    def test_music_chars_setter(self):
        mtext = MusicText((Unit(5), Unit(6)), self.staff, "accidentalSharp")
        assert mtext.music_chars == [MusicChar(self.font, "accidentalSharp")]
        assert mtext.text == "\ue262"
        new_chars = [MusicChar(self.font, "accidentalFlat")]
        mtext.music_chars = new_chars
        assert mtext.music_chars == new_chars
        # text should be updated too
        assert mtext.text == "\ue260"

    def test_breakable_passed_to_superclass(self):
        mtext = MusicText((Unit(5), Unit(6)), self.staff, "accidentalSharp")
        assert mtext.breakable == True
