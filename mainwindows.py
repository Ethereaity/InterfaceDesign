from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow,QTextEdit, QFileDialog, QWidget
from PyQt5.QtCore import Qt,QSize,QDateTime
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap

class ImageViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片查看器")
        self.setGeometry(100, 100, 800, 600)
        self.setLayout(QVBoxLayout())

        # Create a label for displaying the image
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.imageLabel)

        # Create buttons for zooming
        self.zoomInButton = QPushButton("+", self)
        self.zoomOutButton = QPushButton("-", self)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)

        # Add buttons to layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.zoomInButton)
        buttonLayout.addWidget(self.zoomOutButton)
        self.layout().addLayout(buttonLayout)

        self.image = None
        self.scaleFactor = 1.0

    def set_image(self, pixmap):
        self.image = QPixmap(pixmap)  # Ensure we have a QPixmap object
        self.scaleFactor = 1.0  # Reset scale factor when setting a new image
        self.update_image()

    def update_image(self):
        if self.image:
            scaled_pixmap = self.image.scaled(self.imageLabel.size() * self.scaleFactor, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imageLabel.setPixmap(scaled_pixmap)
            self.imageLabel.adjustSize()

    def zoomIn(self):
        self.scaleFactor *= 1.1
        self.update_image()

    def zoomOut(self):
        if self.scaleFactor > 0.5:  # Add a limit to prevent excessive zooming out
            self.scaleFactor /= 1.1
            self.update_image()

class MainWindow(QMainWindow):
    def add_log(self, message):
        """
        向日志区域添加一条新的日志信息。
        """
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")
        formatted_message = f"[{timestamp}] {message}"
        self.logArea.append(formatted_message)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 1000, 600)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        # Initialize UI components
        self.label = QLabel("logo")
        self.pushButton = QPushButton("导入图片")
        self.pushButton_4 = QPushButton("元件检测效果")
        self.pushButton_5 = QPushButton("结构检测效果")
        self.pushButton_6 = QPushButton("轮廓检测效果")
        self.label_2 = QLabel("图片")
        self.label_3 = QLabel("文本信息")
        self.pushButton_2 = QPushButton("展示原图")
        self.pushButton_3 = QPushButton("保存异常信息")
        self.logArea = QTextEdit()
        self.logArea.setReadOnly(True)

        # Set a fixed size for buttons
        button_size = QSize(150, 30)  # Adjusted button size
        for button in [self.pushButton, self.pushButton_4, self.pushButton_5, self.pushButton_6, self.pushButton_2, self.pushButton_3]:
            button.setFixedSize(button_size)

        # Create layouts
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()

        # Adding widgets to right layout
        self.rightLayout.addWidget(self.label_2)
        self.rightLayout.addWidget(self.logArea)

        # Set layout for central widget
        self.centralLayout = QHBoxLayout()
        self.centralLayout.setSpacing(0)  # No extra spacing between widgets
        self.centralLayout.addLayout(self.leftLayout)
        self.centralLayout.addLayout(self.rightLayout)
        self.centralwidget.setLayout(self.centralLayout)

        # Add buttons to left layout
        for button in [self.label, self.pushButton, self.pushButton_4, self.pushButton_5, self.pushButton_6, self.pushButton_2, self.pushButton_3]:
            self.leftLayout.addWidget(button)

        # Connect buttons to slots
        self.pushButton.clicked.connect(self.openImage)
        self.pushButton_2.clicked.connect(self.showOriginalImage)

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
                label_size = self.label_2.size()
                # Adjust image size for better fit
                scaled_pixmap = self.pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_2.setPixmap(scaled_pixmap)
                self.add_log(f"加载了图片: {imgName}")  # 使用新的日志接口
            else:
                self.add_log(f"加载了图片: {imgName}")  # 使用新的日志接口
        except Exception as e:
            self.logArea.append(f"加载图片时出现错误: {e}")

    def showOriginalImage(self):
        if hasattr(self, 'pixmap'):
            viewer = ImageViewer(self)
            viewer.set_image(self.pixmap)
            viewer.exec_()
        else:
            self.add_log("请先导入一张图片")  # 使用新的日志接口

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())