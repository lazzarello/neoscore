from brown.interface.invisible_object_interface import InvisibleObjectInterface
from brown.core.graphic_object import GraphicObject


class InvisibleObject(GraphicObject):

    _interface_class = InvisibleObjectInterface

    def __init__(self, pos, parent=None):
        """
        Args:
            pos (Point[GraphicUnit] or tuple): The position of the path root
                relative to the document.
            parent: The parent (core-level) object or None
        """
        super().__init__(pos, 0, None, None, parent)

    def _render_complete(self, pos):
        self._interface = self._interface_class(self.pos, parent=self.parent)
        self._interface.render()
