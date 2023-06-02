from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.Qsci import *
from PyQt5.QtGui import *



class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        # Body 
        self.setWindowTitle("Emerald")
        self.resize(1300, 900)

        self.window_font = QFont("Fire Code")