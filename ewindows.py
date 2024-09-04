from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QPushButton, QVBoxLayout, QComboBox, QWidget, QScrollArea
import sys


class SaveE(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('saveE.ui', self)
        self.resize(600, 400)

        self.scroll_area = self.findChild(QScrollArea, 'scrollArea')
        if not self.scroll_area:
            print("Error: QScrollArea not found.")
        self.scroll_area_widget = self.findChild(QWidget, 'scrollAreaWidget')
        if not self.scroll_area_widget:
            print("Error: scrollAreaWidget not found.")

        if self.scroll_area_widget:
            self.layout = QVBoxLayout(self.scroll_area_widget)
            self.scroll_area_widget.setLayout(self.layout)

            self.combo_box = self.findChild(QComboBox, 'comboBox')
            self.text_edit = self.findChild(QPlainTextEdit, 'edit')
            self.button = self.findChild(QPushButton, 'button1')

            if self.combo_box:
                self.layout.addWidget(self.combo_box)
                self.combo_box.currentIndexChanged.connect(self.update_placeholder_text)
            if self.text_edit:
                self.layout.addWidget(self.text_edit)
            if self.button:
                self.layout.addWidget(self.button)

            self.set_default_text()

            if self.button:
                self.button.clicked.connect(self.save)

            # Call the print_message function
            self.print_message()
        else:
            print("Error: scrollAreaWidget was not properly initialized.")

    def set_default_text(self):
        # Set default placeholder text
        if self.text_edit:
            self.text_edit.setPlaceholderText('请选择你想要的错误类型！')

    def update_placeholder_text(self):
        # Update placeholder text based on the current combo box selection
        if self.text_edit and self.combo_box:
            current_text = self.combo_box.currentText()
            if current_text == '外观破损':
                self.text_edit.setPlaceholderText('外观破损：')
            elif current_text == '部件缺失':
                self.text_edit.setPlaceholderText('部件缺失：')
            elif current_text == '尺寸不达标':
                self.text_edit.setPlaceholderText('尺寸不达标：')
            elif current_text == '其他错误':
                self.text_edit.setPlaceholderText('其他错误：')

    def save(self):
        if self.text_edit and self.combo_box:
            text = self.text_edit.toPlainText()
            selected_option = self.combo_box.currentText()
            with open('exception.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{selected_option}] {text}\n")
                f.write("=" * 40 + "\n")
            self.close()
        else:
            print("Error: QPlainTextEdit or QComboBox not found when trying to save.")

    def print_message(self):
        # Default print message function
        print("有错误！！！")


class AppearanceDamage(SaveE):
    def __init__(self):
        super().__init__()
        if self.combo_box:
            self.combo_box.setCurrentText('外观破损')

    def print_message(self):
        # 改写父类的 print_message函数
        super().print_message()
        print("外观破损！")


class MissingParts(SaveE):
    def __init__(self):
        super().__init__()
        if self.combo_box:
            self.combo_box.setCurrentText('部件缺失')

    def print_message(self):
        # 改写父类的 print_message函数
        super().print_message()
        print("部件缺失！")


class SizeIssue(SaveE):
    def __init__(self):
        super().__init__()
        if self.combo_box:
            self.combo_box.setCurrentText('尺寸不达标')

    def print_message(self):
        # 改写父类的 print_message函数
        super().print_message()
        print("尺寸不达标！")


class OtherError(SaveE):
    def __init__(self):
        super().__init__()
        if self.combo_box:
            self.combo_box.setCurrentText('其他错误')

    def print_message(self):
        # 改写父类的 print_message函数
        super().print_message()
        print("有其他错误！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppearanceDamage()
    window.show()
    sys.exit(app.exec_())
