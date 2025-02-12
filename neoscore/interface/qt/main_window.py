import os
from time import time

from PyQt5 import QtCore, QtWidgets, uic

QT_PRECISE_TIMER = 0


class MainWindow(QtWidgets.QMainWindow):
    """The primary entry point for all UI code.

    This bootstraps the ``main_window.ui`` structure.
    """

    _ui_path = os.path.join(os.path.dirname(__file__), "main_window.ui")

    def __init__(self):
        super().__init__()
        uic.loadUi(MainWindow._ui_path, self)
        self.refresh_func = None
        self._frame = 0  # Frame counter used in debug mode

    def show(self):
        QtCore.QTimer.singleShot(0, QT_PRECISE_TIMER, self.refresh)  # noqa
        super().show()

    @QtCore.pyqtSlot()
    def refresh(self):
        start_time = time()
        if self.refresh_func:
            requested_delay_s = self.refresh_func(start_time)
            requested_delay_ms = int(requested_delay_s * 1000)
            QtCore.QTimer.singleShot(
                requested_delay_ms, QT_PRECISE_TIMER, self.refresh  # noqa
            )
            # if env.DEBUG:
            #     update_time = time() - start_time
            #     refresh_fps = int(1 / (time() - start_time))
            #     if self._frame % 30 == 0:
            #         print(
            #             f"Scene update took {int(update_time * 1000)} ms ({refresh_fps} / s)"
            #         )
            #         print(f"requested delay was {requested_delay_ms} ms")
            #     self._frame += 1
        # The viewport is unconditionally updated because we disable automatic updates
        self.graphicsView.viewport().update()
