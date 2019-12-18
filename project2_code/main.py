import glob
import os
import sys

from PySide2.QtWidgets import QApplication

from src.drawing_component import DrawingComponent
from src.user_interface import UserInterface

if __name__ == "__main__":
    temporaries = glob.glob('temp/*')
    for f in temporaries:
        os.remove(f)
    temporary_nucleons = glob.glob('nucleons/*')
    for f in temporary_nucleons:
        os.remove(f)
    drawer = DrawingComponent()

    app_window = QApplication(sys.argv)
    widget = UserInterface(drawer)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app_window.exec_())
