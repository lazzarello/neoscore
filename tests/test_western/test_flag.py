import pytest

from neoscore.models.duration import Duration
from neoscore.utils.point import ORIGIN
from neoscore.utils.units import Mm
from neoscore.western.flag import Flag, NoFlagNeededError
from neoscore.western.staff import Staff

from ..helpers import AppTest


class TestFlag(AppTest):
    def setUp(self):
        super().setUp()
        self.staff = Staff((Mm(0), Mm(0)), None, length=Mm(100))

    def test_glyphnames(self):
        # All flags with durations in the following denominations should
        # be init-able without error.
        for i in [1024, 512, 256, 128, 64, 32, 16, 8]:
            Flag(ORIGIN, self.staff, Duration(1, i), 1)
            Flag(ORIGIN, self.staff, Duration(1, i), -1)

    def test_vertical_offset_needed(self):
        assert Flag.vertical_offset_needed(Duration(1, 4)) == 0
        assert Flag.vertical_offset_needed(Duration(1, 8)) == 1
        assert Flag.vertical_offset_needed(Duration(1, 16)) == 1

    def test_raises_no_flag_needed_error(self):
        # Test valid durations
        Flag(ORIGIN, self.staff, Duration(1, 16), 1)
        Flag(ORIGIN, self.staff, Duration(1, 8), 1)

        # Test invalid durations
        with pytest.raises(NoFlagNeededError):
            Flag(ORIGIN, self.staff, Duration(1, 4), 1)
        with pytest.raises(NoFlagNeededError):
            Flag(ORIGIN, self.staff, Duration(1, 2), 1)
        with pytest.raises(NoFlagNeededError):
            Flag(ORIGIN, self.staff, Duration(1, 1), 1)
