import sys
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QTextEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRegularExpression
from PyQt5.QtGui import QTextCharFormat, QTextCursor

class Log(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('logwindows.ui', self)
        self.init_image_viewer_and_controls()
        self.init_signal_slots()
        # 初始化动画
        self.init_animations()

    def show_log(self):
        """显示日志内容"""
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
            self.saveButton.clicked.connect(lambda: self.animate_button(self.saveButton))
            self.saveButton.clicked.connect(self.saveLog)  # 连接保存按钮
        if self.exportButton:
            self.exportButton.clicked.connect(lambda: self.animate_button(self.exportButton, self.exportLog))

    def init_animations(self):
        """初始化动画设置"""
        self.animations = {}

    def animate_button(self, button, callback=None):
        """按钮点击时的缩放动画"""
        # 如果按钮正在执行动画，则取消该动画
        if button in self.animations:
            self.animations[button].stop()

        # 放大动画
        enlarge_animation = QPropertyAnimation(button, b"size")
        enlarge_animation.setDuration(50)
        enlarge_animation.setStartValue(button.size())
        enlarge_animation.setEndValue(button.size() + QtCore.QSize(3, 3))
        enlarge_animation.setEasingCurve(QEasingCurve.OutBounce)

        # 缩小动画
        shrink_animation = QPropertyAnimation(button, b"size")
        shrink_animation.setDuration(50)
        shrink_animation.setStartValue(button.size() + QtCore.QSize(3, 3))
        shrink_animation.setEndValue(button.size())
        shrink_animation.setEasingCurve(QEasingCurve.InBounce)

        # 动画链
        enlarge_animation.finished.connect(lambda: shrink_animation.start())

        # 缩小动画结束后调用回调函数
        if callback:
            shrink_animation.finished.connect(callback)

        # 启动放大动画
        self.animations[button] = enlarge_animation
        enlarge_animation.start()

    def searchLog(self, text):
        """在日志区域中搜索并高亮显示文本"""
        document = self.logArea.document()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(Qt.yellow)
        cursor = QTextCursor(document)
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())

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
    log_window.show()
    sys.exit(app.exec_())


