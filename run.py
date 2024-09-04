import sys
from PyQt5 import QtWidgets, QtCore
from logwindows import save_log, InfoLog  # 导入 save_log 函数和 InfoLog 类

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_content = "这里是日志内容"
        self.logArea = QtWidgets.QTextEdit()  # 确保你在这里初始化 logArea

    def closeEvent(self, event):
        log_content = self.logArea.toPlainText()
        print("关闭事件被触发")
        try:
            save_log(log_content)  # 调用 logwindows.py 中的 save_log 函数
        except Exception as e:
            print(f"保存日志时出错: {e}")
        event.accept()

if __name__ == "__main__":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    import mainwindows

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    window = mainwindows.MyApp()

    # 根据需要使用不同的日志窗口类
    log_window = InfoLog()  # 或者使用 ErrorLog() 或 WarningLog()

    window.showlogSignal.connect(log_window.show_log)
    window.showMaximized()
    sys.exit(app.exec_())
