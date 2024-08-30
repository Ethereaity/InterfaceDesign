from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QPushButton, QVBoxLayout, QComboBox, QWidget, QScrollArea
import sys

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QPlainTextEdit, QComboBox, QWidget, QScrollArea

class SaveE(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('saveE.ui', self)
        self.resize(600, 400)

        # 通过 findChild 找到 scroll area 和其内容部件
        self.scroll_area = self.findChild(QScrollArea, 'scrollArea')
        if not self.scroll_area:
            print("Error: QScrollArea not found.")
        self.scroll_area_widget = self.findChild(QWidget, 'scrollAreaWidget')
        if not self.scroll_area_widget:
            print("Error: scrollAreaWidget not found.")

        # 只有在 self.scroll_area_widget 被正确找到的情况下才设置布局
        if self.scroll_area_widget:
            self.layout = QVBoxLayout(self.scroll_area_widget)
            self.scroll_area_widget.setLayout(self.layout)

            # 在 scroll area 的内容部件中添加控件
            self.combo_box = self.findChild(QComboBox, 'comboBox')
            self.text_edit = self.findChild(QPlainTextEdit, 'edit')
            self.button = self.findChild(QPushButton, 'button1')

            # 先添加 comboBox，再添加 textEdit，最后添加 button
            if self.combo_box:
                self.layout.addWidget(self.combo_box)
            if self.text_edit:
                self.layout.addWidget(self.text_edit)
            if self.button:
                self.layout.addWidget(self.button)

            # 设置控件的占位文本
            if self.text_edit:
                self.text_edit.setPlaceholderText('请输入异常信息')

            # 连接按钮的点击信号
            if self.button:
                self.button.clicked.connect(self.save)
        else:
            print("Error: scrollAreaWidget was not properly initialized.")

    def save(self):
        if self.text_edit and self.combo_box:
            text = self.text_edit.toPlainText()
            selected_option = self.combo_box.currentText()
            with open('exception.txt', 'a', encoding='utf-8') as f:
                # 在异常信息前添加选择框的值
                f.write(f"[{selected_option}] {text}\n")
                f.write("="*40 + "\n")  # 分隔符
            self.close()
        else:
            print("Error: QPlainTextEdit or QComboBox not found when trying to save.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SaveE()  # 启动 SaveE 窗口
    window.show()
    sys.exit(app.exec_())