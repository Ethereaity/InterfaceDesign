import sys

import mainwindows

from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QTextEdit, QFileDialog, QWidget
from PyQt5.QtCore import Qt,QSize,QDateTime
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindows.MainWindow()
    window.show()
    sys.exit(app.exec_())