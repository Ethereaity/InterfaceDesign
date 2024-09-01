
import sys
from PyQt5 import QtWidgets, QtCore
import savelog  # 引入刚才编写的 savelog.py


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化你的主窗口
        self.log_content = "这里是日志内容"  # 假设这是你的日志内容

    def closeEvent(self, event):
        # 在主程序关闭时保存日志
        savelog.save_log(self.log_content)
        event.accept()


if __name__ == "__main__":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    import mainwindows
    import logwindows

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    window = mainwindows.MyApp()
    log_window = logwindows.Log()
    window.showlogSignal.connect(log_window.show_log)
    window.showMaximized()
    sys.exit(app.exec_())