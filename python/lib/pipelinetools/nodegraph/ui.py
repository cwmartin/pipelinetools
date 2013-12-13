from PySide import QtCore
from PySide import QtGui
from PySide import QtOpenGL
import sys

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        """
        """
        super(MainWindow, self).__init__()

if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec_())
