import unittest
from nose.tools import assert_raises

from brown.utils.point import Point
from brown.utils.anchored_point import AnchoredPoint


from brown.utils.units import Unit, Mm


class TestPoint(unittest.TestCase):

    def test_init_with_pair(self):
        test_point = Point(5, 6)
        assert(test_point.x == 5)
        assert(test_point.y == 6)

    def test_init_with_2_tuple(self):
        test_point = Point((5, 6))
        assert(test_point.x == 5)
        assert(test_point.y == 6)

    def test_init_with_existing_Point(self):
        existing_point = Point(5, 6)
        test_point = Point(existing_point)
        assert(test_point.x == 5)
        assert(test_point.y == 6)

    def test_init_with_existing_AnchoredPoint(self):
        existing_point = AnchoredPoint(5, 6, None)
        test_point = Point(existing_point)
        assert(test_point.x == 5)
        assert(test_point.y == 6)

    def test_init_with_unit(self):
        test_point = Point.with_unit(5, 6, unit=Unit)
        assert(isinstance(test_point.x, Unit))
        assert(isinstance(test_point.y, Unit))
        assert(test_point.x == Unit(5))
        assert(test_point.y == Unit(6))

    def test_with_unit_fails_if_unit_not_set(self):
        with assert_raises(TypeError):
            Point.with_unit(5, 6)

    def test_to_unit_from_int(self):
        test_point = Point(5, 6)
        test_point.to_unit(Unit)
        assert(isinstance(test_point.x, Unit))
        assert(isinstance(test_point.y, Unit))
        assert(test_point.x == Unit(5))
        assert(test_point.y == Unit(6))

    def test_to_unit_from_other_unit(self):
        test_point = Point(Unit(1), Unit(2))
        test_point.to_unit(Mm)
        assert(isinstance(test_point.x, Mm))
        assert(isinstance(test_point.y, Mm))
        self.assertAlmostEqual(test_point.x, Mm(Unit(1)))
        self.assertAlmostEqual(test_point.y, Mm(Unit(2)))

    def test_iteration(self):
        test_point = Point(5, 6)
        result = []
        for dimension in test_point:
            result.append(dimension)
        assert(result == [5, 6])

    def test_indexing(self):
        test_point = Point(5, 6)
        assert(test_point[0] == 5)
        assert(test_point[1] == 6)

    def test_indexing_with_invalid_raises_IndexError(self):
        test_point = Point(5, 6)
        with assert_raises(IndexError):
            test_point[3]
        with assert_raises(IndexError):
            test_point[-1]
        with assert_raises(TypeError):
            test_point['nonsense index']

    def test_setters_hook_setter_hook(self):

        class PointHolder:
            def __init__(self):
                self.point_setter_hook_called = False
                self.point = Point(0, 0)
                self.point.setters_hook = self.handle_hook

            def handle_hook(self):
                self.point_setter_hook_called = True

        test_instance = PointHolder()
        assert(test_instance.point.x == 0)
        test_instance.point.x = 1
        assert(test_instance.point_setter_hook_called is True)

    def test_setters_hook_setter_hook_with_same_value_set(self):

        class PointHolder:
            def __init__(self):
                self.point_setter_hook_called = False
                self.point = Point(0, 0)
                self.point.setters_hook = self.handle_hook

            def handle_hook(self):
                self.point_setter_hook_called = True

        test_instance = PointHolder()
        assert(test_instance.point.x == 0)
        test_instance.point.x = 0
        assert(test_instance.point_setter_hook_called is True)

    def test__eq__(self):
        p1 = Point(5, 6)
        p2 = Point(5, 6)
        p3 = Point(5, 7)
        assert(p1 == p2)
        assert(p1 != p3)
        assert(p1 != (5, 6))

    def test__add__(self):
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        assert(p1 + p2 == Point(4, 6))
        with assert_raises(TypeError):
            p1 + 1

    def test__sub__(self):
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        assert(p1 - p2 == Point(-2, -2))
        with assert_raises(TypeError):
            p1 - 1

    def test__mult__(self):
        p1 = Point(1, 2)
        assert(p1 * -1) == Point(-1, -2)
        p2 = Point(Unit(2), Unit(3))
        assert(p2 * Unit(-1) == Point(Unit(-2), Unit(-3)))