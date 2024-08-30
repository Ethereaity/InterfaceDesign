import sys
import logo
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap, QTransform, QTextCharFormat, QTextCursor, QIcon
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QFileDialog, QLabel, QVBoxLayout, \
    QPushButton, QLineEdit, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt, QSize, QDateTime, QRegularExpression, pyqtSignal
import json

# 导入其他需要的模块
sys.path.insert(1, sys.path[0] + r'\yolov5')
sys.path.insert(2, sys.path[0] + r'\detectron')
sys.path.insert(3, sys.path[0] + r'\detectron\projects\PointRend')
from yolov5.detect import yolo_detect
from detectron.detect import keypoint_detect
from detectron.projects.PointRend.detect import pointrend_detect
from Inflation_search import calculate_length, convert_to_images, re_ploy


class MyApp(QtWidgets.QMainWindow):
    showlogSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi('mainwindows.ui', self)

        # 初始化图片展示区域和控制按钮
        self.init_image_viewer_and_controls()

        # 槽函数初始化
        self.init_signal_slots()

        # 软件图标设置
        self.setWindowIcon(QIcon('logo2.png'))

        # 添加事件过滤器以捕获滚轮事件
        self.label_image.installEventFilter(self)

    def eventFilter(self, source, event):
        """事件过滤器，用于处理鼠标滚轮事件"""
        if event.type() == QtCore.QEvent.Wheel and source is self.label_image:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            return True
        return super().eventFilter(source, event)

    def init_image_viewer_and_controls(self):
        # 初始化控制图片的按钮和功能
        self.rotationAngle = 0
        self.scaleFactor = 1.0

        # 查找控件
        self.label = self.findChild(QLabel, "label")
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.pushButton_3 = self.findChild(QPushButton, "pushButton_3")
        self.pushButton_4 = self.findChild(QPushButton, "pushButton_4")
        self.pushButton_5 = self.findChild(QPushButton, "pushButton_5")
        self.pushButton_6 = self.findChild(QPushButton, "pushButton_6")
        self.scrollArea_external = self.findChild(QScrollArea, "scrollArea_external")
        self.scrollArea = self.findChild(QScrollArea, "scrollArea")
        self.label_image = self.findChild(QLabel, "label_image")
        self.searchBar = self.findChild(QLineEdit, "searchBar")
        self.logArea = self.findChild(QTextEdit, "logArea")
        self.zoomInButton = self.findChild(QPushButton, "zoomInButton")
        self.zoomOutButton = self.findChild(QPushButton, "zoomOutButton")
        self.rotateClockwiseButton = self.findChild(QPushButton, "rotateClockwiseButton")
        self.rotateCounterclockwiseButton = self.findChild(QPushButton, "rotateCounterclockwiseButton")

        # 设置 QLabel 居中显示
        self.label_image.setAlignment(Qt.AlignCenter)

        # 在左上角的label中显示 "logo图标.png" 的图片，并按比例缩放以适应label的大小
        logo_pixmap = QPixmap("logo图标.png")

        # 获取label的初始大小
        label_size = self.label.size()

        # 按比例缩放图片以适应label的大小，但保持图片的宽高比
        scaled_pixmap = logo_pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 将缩放后的图片设置到label中
        self.label.setPixmap(scaled_pixmap)

    def init_signal_slots(self):
        """初始化信号槽连接"""
        self.pushButton.clicked.connect(self.openImage)
        self.rotateClockwiseButton.clicked.connect(self.rotateClockwise)
        self.rotateCounterclockwiseButton.clicked.connect(self.rotateCounterclockwise)

        self.pushButton.clicked.connect(self.openImage)
        self.pushButton_4.clicked.connect(self.show_yolo)
        self.pushButton_5.clicked.connect(self.show_maskrcnn)
        self.pushButton_6.clicked.connect(self.show_pointrend)
        # 菜单栏槽函数
        self.Import.triggered.connect(self.openImage)
        self.log.triggered.connect(self.show_log)
        self.log_clear.triggered.connect(self.clear_log)

    def show_log(self):
        # 发射信号给弹出界面
        self.showlogSignal.emit()

    def clear_log(self):
        with open(r'log.txt', 'a+') as file:
            file.truncate(0)
        QMessageBox.information(self, "提示", "已清空日志")

    def openImage(self):
        try:
            self.imgName, _ = QFileDialog.getOpenFileName(
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
            if self.imgName:
                self.pixmap = QPixmap(self.imgName)
                if self.pixmap.isNull():
                    raise ValueError("Failed to load image.")
                self.display_scaled_image()
                self.add_log(f"加载了图片: {self.imgName}")
                self.yolo_detect()
                self.keypoint_detect()
                self.pointrend_detect()
                self.length_detect()
            else:
                self.add_log(f"未选择图片")
        except Exception as e:
            self.add_log(f"加载图片时出现错误: {e}")
            QMessageBox.critical(self, "错误", "加载图片时出现错误，请重试。")

    def display_scaled_image(self):
        """根据当前缩放比例和旋转角度显示图片"""
        if not self.pixmap:
            print("Error: No pixmap loaded.")
            return
        try:
            # 确保 label_image 是有效的对象，并且大小合理
            if not self.label_image or self.label_image.size().width() == 0 or self.label_image.size().height() == 0:
                print("Error: label_image is not properly initialized or has zero size.")
                return

            # 重新计算每次缩放的比例，确保缩放比例是基于初始图片大小的
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            print(f"Pixmap transformed with rotation angle: {self.rotationAngle}")

            # 使用新的缩放比例调整图片大小
            label_size = self.label_image.size()  # 获取 label 的当前大小
            scaled_pixmap = rotated_pixmap.scaled(label_size * self.scaleFactor, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            print(f"Pixmap scaled with scale factor: {self.scaleFactor}")

            self.label_image.setPixmap(scaled_pixmap)
            self.label_image.adjustSize()
            print(f"Image displayed with scale: {self.scaleFactor}, rotation: {self.rotationAngle}")
        except Exception as e:
            print(f"Error displaying image: {e}")
            self.add_log(f"Error displaying image: {e}")

    def zoomIn(self):
        try:
            if self.scaleFactor < 3.0:  # 最大放大倍数为3倍
                self.scaleFactor *= 1.05  # 适当放大
                self.display_scaled_image()
        except Exception as e:
            self.add_log(f"Zoom In 出现错误: {e}")
            print(f"Zoom In 出现错误: {e}")

    def zoomOut(self):
        try:
            if self.scaleFactor > 0.1:  # 最小缩小倍数为0.1
                self.scaleFactor /= 1.05  # 适当缩小
                self.display_scaled_image()
        except Exception as e:
            self.add_log(f"Zoom Out 出现错误: {e}")
            print(f"Zoom Out 出现错误: {e}")

    def rotateClockwise(self):
        """顺时针旋转90°"""
        try:
            self.rotationAngle += 90
            if self.rotationAngle >= 360:
                self.rotationAngle -= 360
            # 每次旋转后，将缩放比例重置为1，确保图片不变形
            self.display_scaled_image()
        except Exception as e:
            self.add_log(f"Rotate Clockwise 出现错误: {e}")
            print(f"Rotate Clockwise 出现错误: {e}")

    def rotateCounterclockwise(self):
        """逆时针旋转90°"""
        try:
            self.rotationAngle -= 90
            if self.rotationAngle <= -360:
                self.rotationAngle += 360
            # 每次旋转后，保持当前缩放比例
            self.display_scaled_image()
        except Exception as e:
            self.add_log(f"Rotate Counterclockwise 出现错误: {e}")
            print(f"Rotate Counterclockwise 出现错误: {e}")

    def add_log(self, message):
        """向日志区域添加一条新的日志信息。"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")
        formatted_message = f"[{timestamp}] {message}\n"
        self.logArea.append(formatted_message)
        with open('log.txt', 'a') as file:
            file.write(formatted_message)
            file.close()
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

    def yolo_detect(self):
        self.yolo_confs, self.yolo_components, self.yolo_time = yolo_detect(self.imgName)

    def keypoint_detect(self):
        self.keypoint_info, self.keypoint_time, self.keypoint_confinfo, self.line_box = keypoint_detect(self.imgName)

    def pointrend_detect(self):
        predictions, t = pointrend_detect(self.imgName)

    def length_detect(self):
        keypoint_info = self.keypoint_info
        keypoint_posinfo = {}
        for i, item in enumerate(keypoint_info):
            x, y, conf = item
            keypoint_posinfo[self.keypoint_names[i]] = [x, y]

    def show_yolo(self):
        if self.imgName:
            self.pixmap = QPixmap('results/yolo_detect.jpg')
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            scaled_pixmap = rotated_pixmap.scaled(self.label_image.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            self.label_image.setPixmap(scaled_pixmap)
            self.label_image.adjustSize()

    def show_maskrcnn(self):
        if self.imgName:
            self.pixmap = QPixmap('results/keypoint_detect.jpg')
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            scaled_pixmap = rotated_pixmap.scaled(self.label_image.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            self.label_image.setPixmap(scaled_pixmap)
            self.label_image.adjustSize()

    def show_pointrend(self):
        if self.imgName:
            self.pixmap = QPixmap('results/pointrend_detect.jpg')
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = self.pixmap.transformed(transform, Qt.SmoothTransformation)
            scaled_pixmap = rotated_pixmap.scaled(self.label_image.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                                  Qt.SmoothTransformation)
            self.label_image.setPixmap(scaled_pixmap)
            self.label_image.adjustSize()
