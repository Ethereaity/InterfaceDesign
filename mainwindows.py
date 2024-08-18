from PyQt5 import QtWidgets
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QFileDialog, QWidget, QApplication, QDialog, QLabel, QVBoxLayout, \
    QPushButton, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import Qt, QSize, QDateTime, QRegularExpression
from PyQt5.QtGui import QPixmap, QTransform



class ImageViewer(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片查看器")
        self.setGeometry(100, 100, 800, 600)
        self.setLayout(QVBoxLayout())

        # Initialize rotation angle
        self.rotationAngle = 0

        # Create a label for displaying the image
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.imageLabel)

        # Create buttons for zooming and rotating
        self.zoomInButton = QPushButton("+", self)
        self.zoomOutButton = QPushButton("-", self)
        self.rotateClockwiseButton = QPushButton("顺时针旋转", self)
        self.rotateCounterclockwiseButton = QPushButton("逆时针旋转", self)

        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.rotateClockwiseButton.clicked.connect(self.rotateClockwise)
        self.rotateCounterclockwiseButton.clicked.connect(self.rotateCounterclockwise)

        # Add buttons to layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.zoomInButton)
        buttonLayout.addWidget(self.zoomOutButton)
        buttonLayout.addWidget(self.rotateClockwiseButton)
        buttonLayout.addWidget(self.rotateCounterclockwiseButton)
        self.layout().addLayout(buttonLayout)

        self.image = pixmap
        self.scaleFactor = 1.0
        # Enable minimize, maximize, and close buttons
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        self.update_image(init=True)  # 初始化时直接显示图片

    def update_image(self, init=False):
        if self.image:
            if init:
                # Initial scaling: fit to window
                scaled_pixmap = self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                # Rotate and scale the image based on the current rotation angle and scale factor
                transform = QTransform().rotate(self.rotationAngle)
                rotated_pixmap = self.image.transformed(transform, Qt.SmoothTransformation)
                scaled_pixmap = rotated_pixmap.scaled(self.imageLabel.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                                      Qt.SmoothTransformation)

            self.imageLabel.setPixmap(scaled_pixmap)
            self.imageLabel.adjustSize()

    def zoomIn(self):
        if self.scaleFactor * 1.1 <= 4.0:  # 限制最大放大倍数
            self.scaleFactor *= 1.1
            self.update_image()

    def zoomOut(self):
        if self.scaleFactor > 0.5:  # Add a limit to prevent excessive zooming out
            self.scaleFactor /= 1.1
            self.update_image()

    def rotateClockwise(self):
        """顺时针旋转90度"""
        self.rotationAngle += 90
        self.update_image()

    def rotateCounterclockwise(self):
        """逆时针旋转90度"""
        self.rotationAngle -= 90
        self.update_image()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoomIn()
        elif event.key() == Qt.Key_Minus:
            self.zoomOut()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("线束分析工具")
        self.setGeometry(100, 100, 1200, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        # Initialize UI components
        self.label = QLabel("线束分析工具")
        self.pushButton = QPushButton("导入图片")
        self.viewSelector = QComboBox()  # 用于选择视图
        self.viewSelector.addItems(["原图", "元件检测效果", "结构检测效果", "轮廓检测效果", "缺陷检测效果"])
        self.searchBar = QLineEdit()  # 搜索栏
        self.searchBar.setPlaceholderText("搜索日志...")
        self.pushButton_2 = QPushButton("展示选定视图")
        self.pushButton_3 = QPushButton("保存异常信息")
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)

        # Set a fixed size for buttons
        button_size = QSize(150, 30)
        for button in [self.pushButton, self.pushButton_2, self.pushButton_3]:
            button.setFixedSize(button_size)

        # Create layouts
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()

        # Adding widgets to right layout
        self.rightLayout.addWidget(self.searchBar)
        self.rightLayout.addWidget(self.logArea)

        # Set layout for central widget
        self.centralLayout = QHBoxLayout()
        self.centralLayout.setSpacing(10)  # Adjust spacing for better aesthetics
        self.centralLayout.addLayout(self.leftLayout)
        self.centralLayout.addLayout(self.rightLayout)
        self.centralwidget.setLayout(self.centralLayout)

        # Add components to left layout
        self.leftLayout.addWidget(self.label)
        self.leftLayout.addWidget(self.pushButton)
        self.leftLayout.addWidget(self.viewSelector)
        self.leftLayout.addWidget(self.pushButton_2)
        self.leftLayout.addWidget(self.pushButton_3)

        # Connect buttons to slots
        self.pushButton.clicked.connect(self.openImage)
        self.pushButton_2.clicked.connect(self.showSelectedView)
        self.searchBar.textChanged.connect(self.searchLog)

        self.setWindowFlags(
            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.setStyleSheet("QMainWindow {background-color: white;}")

    def openImage(self):
        try:
            imgName, _ = QFileDialog.getOpenFileName(
                self,
                "打开图片",
                "",
                "JPEG Files (*.jpg *.jpeg);;" +
                "PNG Files (*.png);;" +
                "BMP Files (*.bmp);;" +
                "GIF Files (*.gif);;" +
                "TIFF Files (*.tif *.tiff);;" +
                "WebP Files (*.webp);;" +
                "All Files (*)"
            )
            if imgName:
                self.pixmap = QPixmap(imgName)
                self.display_scaled_image(self.pixmap, self.label)
                self.add_log(f"加载了图片: {imgName}")
            else:
                self.add_log(f"未选择图片")
        except Exception as e:
            self.logArea.append(f"加载图片时出现错误: {e}")

    def display_scaled_image(self, pixmap, label):
        """等比例缩放图片，并显示在指定的QLabel上"""
        label_size = label.size()
        # Display the image as large and clear as possible, preserving the aspect ratio
        scaled_pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)

    def showSelectedView(self):
        if hasattr(self, 'pixmap'):
            viewer = ImageViewer(self.pixmap, self)
            viewer.exec_()
        else:
            self.add_log("请先导入一张图片")

    def add_log(self, message):
        """向日志区域添加一条新的日志信息。"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")
        formatted_message = f"[{timestamp}] {message}"
        self.logArea.append(formatted_message)

    def searchLog(self, text):
        cursor = self.logArea.textCursor()
        cursor.setPosition(0)
        format = cursor.charFormat()
        format.setBackground(Qt.yellow)

        # 取消之前的高亮
        self.logArea.moveCursor(cursor.Start)
        self.logArea.setTextCursor(cursor)
        self.logArea.setPlainText(self.logArea.toPlainText())

        # 搜索新文本
        pattern = text
        regex = QRegularExpression(pattern)
        match_iterator = regex.globalMatch(self.logArea.toPlainText())

        while match_iterator.hasNext():
            match = match_iterator.next()
            cursor.setPosition(match.capturedStart())
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(pattern))
            cursor.mergeCharFormat(format)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    import sys

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

