import sys
from PyQt5 import QtWidgets, QtCore
import savelog

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_content = "这里是日志内容"

    def closeEvent(self, event):
        savelog.save_log(self.log_content)
        event.accept()

if __name__ == "__main__":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    import mainwindows
    from logwindows import ErrorLog, WarningLog, InfoLog

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    window = mainwindows.MyApp()

    # 根据需要使用不同的日志窗口类
    log_window = InfoLog()  # 或者使用 ErrorLog() 或 WarningLog()

    window.showlogSignal.connect(log_window.show_log)
    window.showMaximized()
    sys.exit(app.exec_())
