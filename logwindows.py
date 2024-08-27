import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QScrollArea, QWidget, QLineEdit, QTextEdit, QMenu, QApplication
from PyQt5.QtCore import Qt, QDateTime, QRegularExpression, QFile
from PyQt5.QtGui import QPixmap, QTextCharFormat, QTextCursor, QIcon

class Log(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('logwindows.ui', self)
        # 初始化图片展示区域和控制按钮
        self.init_image_viewer_and_controls()
        # 槽函数初始化
        self.init_signal_slots()

    def show_log(self):
        """显示弹出界面并加载日志内容"""
        filenames = 'log.txt'
        try:
            with open(filenames, 'r') as f:
                log_data = f.read()
                self.logArea.setText(log_data)
        except FileNotFoundError:
            self.logArea.setText("日志文件未找到。")
        self.show()

    def init_image_viewer_and_controls(self):
        """初始化控件"""
        self.searchBar = self.findChild(QLineEdit, "searchBar")
        self.logArea = self.findChild(QTextEdit, "logArea")
        self.saveButton = self.findChild(QPushButton, "saveButton")
        self.exportButton = self.findChild(QPushButton, "exportButton")

    def init_signal_slots(self):
        """初始化信号槽连接"""
        if self.searchBar:
            self.searchBar.textChanged.connect(self.searchLog)
        if self.saveButton:
            self.saveButton.clicked.connect(self.saveLog)
        if self.exportButton:
            self.exportButton.clicked.connect(self.exportLog)

    def searchLog(self, text):
        """在日志区域中搜索并高亮显示文本"""
        # 获取整个日志内容
        document = self.logArea.document()

        # 定义高亮格式
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(Qt.yellow)

        # 清除之前的高亮
        cursor = QTextCursor(document)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        # 查找匹配文本并高亮显示
        if text:
            regex = QRegularExpression(text)
            cursor = QTextCursor(document)
            while not cursor.isNull() and not cursor.atEnd():
                cursor = document.find(regex, cursor)
                if not cursor.isNull():
                    cursor.mergeCharFormat(highlight_format)

    def saveLog(self):
        """保存当前日志内容到文件"""
        try:
            with open('log.txt', 'w') as f:
                log_data = self.logArea.toPlainText()
                f.write(log_data)
        except Exception as e:
            print(f"保存日志时发生错误: {e}")

    def exportLog(self):
        """导出日志内容到指定文件"""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "导出日志", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            try:
                with open(filename, 'w') as f:
                    log_data = self.logArea.toPlainText()
                    f.write(log_data)
            except Exception as e:
                print(f"导出日志时发生错误: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    log_window = Log()
    log_window.show_log()
    sys.exit(app.exec_())
