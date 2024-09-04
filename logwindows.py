import sys
import os
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QTextEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRegularExpression
from PyQt5.QtGui import QTextCharFormat, QTextCursor
from datetime import datetime

class BaseLog(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('logwindows.ui', self)
        self.init_image_viewer_and_controls()
        self.init_signal_slots()
        self.init_animations()

    def show_log(self):
        """显示日志内容"""
        filenames = 'log.txt'
        try:
            with open(filenames, 'r') as f:
                log_data = f.read()
                self.logArea.setText(log_data)
            self.show()
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
            self.saveButton.clicked.connect(self.saveLog)
        if self.exportButton:
            self.exportButton.clicked.connect(lambda: self.animate_button(self.exportButton, self.exportLog))

    def init_animations(self):
        """初始化动画设置"""
        self.animations = {}

    def animate_button(self, button, callback=None):
        """按钮点击时的缩放动画"""
        if button in self.animations:
            self.animations[button].stop()

        enlarge_animation = QPropertyAnimation(button, b"size")
        enlarge_animation.setDuration(50)
        enlarge_animation.setStartValue(button.size())
        enlarge_animation.setEndValue(button.size() + QtCore.QSize(3, 3))
        enlarge_animation.setEasingCurve(QEasingCurve.OutBounce)

        shrink_animation = QPropertyAnimation(button, b"size")
        shrink_animation.setDuration(50)
        shrink_animation.setStartValue(button.size() + QtCore.QSize(3, 3))
        shrink_animation.setEndValue(button.size())
        shrink_animation.setEasingCurve(QEasingCurve.InBounce)

        enlarge_animation.finished.connect(lambda: shrink_animation.start())

        if callback:
            shrink_animation.finished.connect(callback)

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
        filename, _ = QFileDialog.getSaveFileName(self, "导出日志", "", "Text Files (*.txt);;All Files (*)",
                                                  options=options)
        if filename:
            try:
                with open(filename, 'w') as f:
                    log_data = self.logArea.toPlainText()
                    f.write(log_data)
            except Exception as e:
                print(f"导出日志时发生错误: {e}")

class ErrorLog(BaseLog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error Log")
        self.logArea.setStyleSheet("background-color: lightpink;")

    def saveLog(self):
        """覆盖 BaseLog 类中的保存方法，指定默认日志级别为 ERROR"""
        log_data = f"[ERROR] {self.logArea.toPlainText()}"
        try:
            with open('log.txt', 'w') as f:
                f.write(log_data)
        except Exception as e:
            print(f"保存日志时发生错误: {e}")

class WarningLog(BaseLog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warning Log")
        self.logArea.setStyleSheet("background-color: lightyellow;")

    def saveLog(self):
        """覆盖 BaseLog 类中的保存方法，指定默认日志级别为 WARNING"""
        log_data = f"[WARNING] {self.logArea.toPlainText()}"
        try:
            with open('log.txt', 'w') as f:
                f.write(log_data)
        except Exception as e:
            print(f"保存日志时发生错误: {e}")

class InfoLog(BaseLog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Info Log")

    def saveLog(self):
        """覆盖 BaseLog 类中的保存方法，指定默认日志级别为 INFO"""
        log_data = f"[INFO] {self.logArea.toPlainText()}"
        try:
            with open('log.txt', 'w') as f:
                f.write(log_data)
        except Exception as e:
            print(f"保存日志时发生错误: {e}")

def save_log(log_content):
    logs_folder = 'logs'

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')

    destination_file = os.path.join(logs_folder, f'{timestamp}.txt')

    print(f"日志内容: {log_content}")

    with open(destination_file, 'w') as f:
        f.write(log_content)

    print(f'日志已保存到 {destination_file}')




