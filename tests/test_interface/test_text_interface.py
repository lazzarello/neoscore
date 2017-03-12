import unittest

from brown.core import brown
from brown.interface.text_interface import TextInterface
from brown.interface.font_interface import FontInterface


class TestTextInterface(unittest.TestCase):

    def setUp(self):
        brown.setup()

    def test_init(self):
        test_font = FontInterface('Bravura', 12)
        test_object = TextInterface((5, 6), 'testing', test_font)
        assert(test_object.text == 'testing')
        assert(test_object._qt_object.text() == test_object.text)
        assert(test_object.font == test_font)
        assert(test_object._qt_object.font() == test_object.font._qt_object)

    def test_text_setter_changes_qt_object(self):
        test_font = FontInterface('Bravura', 12)
        test_object = TextInterface((5, 6), 'testing', test_font)
        test_object.text = 'new value'
        assert(test_object.text == 'new value')
        assert(test_object._qt_object.text() == 'new value')

    def test_font_setter_changes_qt_object(self):
        test_font = FontInterface('Bravura', 12)
        test_object = TextInterface((5, 6), 'testing', test_font)
        new_test_font = FontInterface('Bravura', 16)
        test_object.font = new_test_font
        assert(test_object.font == new_test_font)
        assert(test_object._qt_object.font() == new_test_font._qt_object)