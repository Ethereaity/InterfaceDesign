import sys

import mainwindows
import logwindows
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt,QSize,QDateTime
from PyQt5.QtCore import pyqtSignal

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindows.MyApp()
    log_window = logwindows.Log()
    window.showlogSignal.connect(log_window.show_log)
    window.show()
    sys.exit(app.exec_())

