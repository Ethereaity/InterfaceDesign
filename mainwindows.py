import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget
from PyQt5.QtCore import Qt, QDateTime, QRegularExpression
from PyQt5.QtGui import QPixmap, QTransform, QTextCharFormat, QTextCursor

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindows.ui', self)

        # 初始化图片展示区域和控制按钮
        self.init_image_viewer_and_controls()

        # 槽函数在此添加
        self.pushButton.clicked.connect(self.openImage)
        self.searchBar.textChanged.connect(self.searchLog)

    def init_image_viewer_and_controls(self):
        # 初始化控制图片的按钮和功能
        self.rotationAngle = 0
        self.scaleFactor = 1.0

        # 创建一个 QScrollArea 用于展示图片
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # 在 QScrollArea 中添加 QLabel 用于显示图片
        self.label_image = QLabel(self)
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setScaledContents(True)  # 确保 QLabel 的内容按比例缩放
        self.scrollArea.setWidget(self.label_image)

        # 创建主布局
        mainLayout = QHBoxLayout()

        # 创建一个新的垂直布局用于中部区域
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(self.scrollArea)
        centralLayout.addWidget(self.searchBar)
        centralLayout.addWidget(self.logArea)

        # 添加中部区域布局
        mainLayout.addLayout(centralLayout)

        # 创建右侧控制按钮布局
        controlLayout = QVBoxLayout()
        self.zoomInButton = self.findChild(QPushButton, "zoomInButton")
        self.zoomOutButton = self.findChild(QPushButton, "zoomOutButton")
        self.rotateClockwiseButton = self.findChild(QPushButton, "rotateClockwiseButton")
        self.rotateCounterclockwiseButton = self.findChild(QPushButton, "rotateCounterclockwiseButton")

        if self.zoomInButton:
            controlLayout.addWidget(self.zoomInButton)
            self.zoomInButton.clicked.connect(self.zoomIn)
        if self.zoomOutButton:
            controlLayout.addWidget(self.zoomOutButton)
            self.zoomOutButton.clicked.connect(self.zoomOut)
        if self.rotateClockwiseButton:
            controlLayout.addWidget(self.rotateClockwiseButton)
            self.rotateClockwiseButton.clicked.connect(self.rotateClockwise)
        if self.rotateCounterclockwiseButton:
            controlLayout.addWidget(self.rotateCounterclockwiseButton)
            self.rotateCounterclockwiseButton.clicked.connect(self.rotateCounterclockwise)

        # 将控制按钮布局添加到主布局中
        mainLayout.addLayout(controlLayout)

        # 设置主布局
        self.centralWidget().setLayout(mainLayout)

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
                self.display_scaled_image()
                self.add_log(f"加载了图片: {imgName}")
            else:
                self.add_log(f"未选择图片")
        except Exception as e:
            self.add_log(f"加载图片时出现错误: {e}")

    def display_scaled_image(self):
        """根据当前缩放比例和旋转角度显示图片"""
        if self.pixmap:
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            scaled_pixmap = rotated_pixmap.scaled(self.label_image.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            self.label_image.setPixmap(scaled_pixmap)
            self.label_image.adjustSize()  # 确保 QLabel 大小与图片大小匹配

    def zoomIn(self):
        if self.scaleFactor * 1.1 <= 4.0:  # 限制最大放大倍数
            self.scaleFactor *= 1.1
            self.display_scaled_image()

    def zoomOut(self):
        if self.scaleFactor > 0.5:  # 限制最小缩放倍数
            self.scaleFactor /= 1.1
            self.display_scaled_image()

    def rotateClockwise(self):
        """顺时针旋转90°"""
        self.rotationAngle += 90
        if self.rotationAngle >= 360:
            self.rotationAngle -= 360
        self.display_scaled_image()

    def rotateCounterclockwise(self):
        """逆时针旋转90°"""
        self.rotationAngle -= 90
        if self.rotationAngle <= -360:
            self.rotationAngle += 360
        self.display_scaled_image()

    def add_log(self, message):
        """向日志区域添加一条新的日志信息。"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")
        formatted_message = f"[{timestamp}] {message}"
        self.logArea.append(formatted_message)

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

