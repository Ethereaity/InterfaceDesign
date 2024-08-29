from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication,QPlainTextEdit,QPushButton,QVBoxLayout
import sys



class SaveE(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('saveE.ui', self)
        self.resize(600, 400)

        self.button = self.findChild(QPushButton, 'button')
        self.text_edit = self.findChild(QPlainTextEdit, 'edit')
        self.text_edit.setPlaceholderText('请输入异常信息')
        if self.button:
            self.button.clicked.connect(self.save)

    def save(self):
        if self.text_edit:
            text = self.text_edit.toPlainText()
            with open('exception.txt', 'a') as f:
                f.write(text)
            self.close()
        else:
            print("Error: QTextEdit not found when trying to save.")


from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class ShowE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("异常信息")
        self.resize(400, 700)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        self.edit = QPlainTextEdit()
        self.btn = QPushButton("save")
        layout.addWidget(self.edit)
        layout.addWidget(self.btn)

        self.btn.clicked.connect(self.save)

        with open('exception.txt', 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.edit.setPlainText(self.text)

    def save(self):
        self.text = self.edit.toPlainText()
        with open('exception.txt', 'w', encoding='utf-8') as f:
            f.write(self.text)
        self.close()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    '''
    window = SaveE()
    window.show()
    '''
    window=ShowE()
    window.show()
    sys.exit(app.exec_())

