import sys
import logo
import os
import savelog
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtGui import QPixmap, QTransform, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QFileDialog, QWidget, QApplication, QDialog, QLabel, QVBoxLayout, \
    QPushButton, QHBoxLayout, QComboBox, QLineEdit,QScrollArea,QMessageBox, QFileSystemModel,QTreeView
from PyQt5.QtCore import Qt, QSize, QDateTime, QRegularExpression, QModelIndex,QPoint
from PyQt5.QtGui import QPixmap, QTransform,QIcon
from PyQt5.QtCore import pyqtSignal,QDir,QModelIndex
import sys
import json
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QPen,QStandardItemModel
from PyQt5.QtGui import QTransform
from PyQt5.QtCore import QStorageInfo
import json


sys.path.insert(1,sys.path[0]+r'\yolov5')
sys.path.insert(2,sys.path[0]+r'\detectron')
sys.path.insert(3,sys.path[0]+r'\detectron\projects\PointRend')


#模型需要将以下三行取消注释
#from yolov5.detect import yolo_detect
#from detectron.detect import keypoint_detect
#from detectron.projects.PointRend.detect import pointrend_detect


from ewindows import SaveE
import copy
from Inflation_search import calculate_length,convert_to_images,re_ploy


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

        self.annotations = []  # 初始化批注列表
        self.isDragging = False  # 是否处于拖拽状态
        self.dragStartPos = None  # 拖拽开始位置
        self.labelStartPos = None  # QLabel的初始位置
        self.dragOffset = QtCore.QPoint(0, 0)  # 拖拽偏移量

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.label_image.underMouse():
            self.isDragging = True
            self.dragStartPos = event.pos()  # 记录鼠标按下时的位置
            self.labelStartPos = self.label_image.pos()  # 记录QLabel的初始位置
            self.scrollArea.setCursor(Qt.ClosedHandCursor)  # 设置鼠标为拖拽手势

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.isDragging:
            delta = event.pos() - self.dragStartPos
            self.dragOffset = delta
            new_pos = self.labelStartPos + delta
            self.label_image.move(new_pos)

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.isDragging:
            if not self.dragStartPos or not self.labelStartPos:
                return
            delta = event.pos() - self.dragStartPos
            self.dragOffset = delta
            new_pos = self.labelStartPos + delta
            self.label_image.move(new_pos)
            print(f"Drag Delta: {delta}, New Position: {new_pos}")
            print(f"Label Position: {self.label_image.pos()}")

    def adjust_viewport(self):
        """调整视图以确保图片完整显示"""
        if not self.label_image.pixmap():
            return

        # 获取图片的矩形区域
        pixmap_rect = self.label_image.pixmap().rect()
        print(f"Pixmap Rect: {pixmap_rect}")

        # 获取视图的矩形区域
        viewport_rect = self.scrollArea.viewport().rect()
        print(f"Viewport Rect: {viewport_rect}")

        # 计算图片的显示区域
        label_rect = self.label_image.rect()
        print(f"Label Rect: {label_rect}")

        # 计算需要调整的区域
        if label_rect.width() > viewport_rect.width():
            new_x = min(max(0, -self.label_image.x()), label_rect.width() - viewport_rect.width())
        else:
            new_x = (viewport_rect.width() - label_rect.width()) / 2

        if label_rect.height() > viewport_rect.height():
            new_y = min(max(0, -self.label_image.y()), label_rect.height() - viewport_rect.height())
        else:
            new_y = (viewport_rect.height() - label_rect.height()) / 2

        # 移动图片到调整后的位置
        self.label_image.move(new_x, new_y)
        print(f"Adjusted Label Position: {self.label_image.pos()}")

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

        self.addAnnotationButton = self.findChild(QPushButton, "addAnnotationButton")
        self.saveAnnotationsButton = self.findChild(QPushButton, "saveAnnotationsButton")
        self.loadAnnotationsButton = self.findChild(QPushButton, "loadAnnotationsButton")
        self.clearAnnotationsButton = self.findChild(QPushButton, "clearAnnotationsButton")
        self.convertImageFormatButton = self.findChild(QPushButton, "convertImageFormatButton")



        # 确保在使用这些按钮之前，它们已经被找到并且不是 None
        if None in [self.addAnnotationButton, self.saveAnnotationsButton, self.loadAnnotationsButton,
                    self.clearAnnotationsButton, self.convertImageFormatButton]:
            print("One or more buttons not found. Please check the object names in the .ui file.")
        self.treeView = self.findChild(QTreeView, "treeView")

        # 新添加的两个按钮
        self.newButton1 = self.findChild(QPushButton, "newButton1")
        self.newButton2 = self.findChild(QPushButton, "newButton2")

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

        with open('exception.txt','w',encoding='utf-8') as f:
            f.write("异常：\n")

        # 文件浏览
        self.updateDriveList()
        self._home = QDir.rootPath()  # 你可以替换为你实际想要展示的路径
        self.filemodel = QFileSystemModel()
        self.filemodel.setRootPath(self._home)
        self.treeView.setModel(self.filemodel)  # 设置 QTreeView 的 Model
        self.currentDriveIndex = 0
        # 设置表头模型
        self.headerModel = QStandardItemModel()
        self.headerModel.setColumnCount(1)  # 设置 model 的列数
        self.headerModel.setHeaderData(0, Qt.Horizontal, '文件名', Qt.DisplayRole)
        header = self.treeView.header()
        header.setModel(self.headerModel)  # 设置 QTreeView 的 Header 的 Model

        # 设置 RootIndex
        self.treeView.setRootIndex(self.filemodel.index(self._home))

    def updateDriveList(self):
        # 获取所有驱动器的信息
        drives = [info.rootPath() for info in QStorageInfo.mountedVolumes()]
        self.drives = drives
    def updateButtonState(self):
        """更新按钮状态"""
        if not self.drives:
            self.newButton1.setEnabled(False)
            self.newButton2.setEnabled(False)
        else:
            self.newButton1.setEnabled(len(self.drives) > 1)
            self.newButton2.setEnabled(len(self.drives) > 1)

    def handleNewButton1(self):
        """按字母倒序切换盘符"""
        if self.drives:
            self.currentDriveIndex = (self.currentDriveIndex - 1) % len(self.drives)
            self.showDrive()

    def handleNewButton2(self):
        """按字母顺序切换盘符"""
        if self.drives:
            self.currentDriveIndex = (self.currentDriveIndex + 1) % len(self.drives)
            self.showDrive()

    def showDrive(self):
        """显示当前盘符的内容"""
        currentDrive = self.drives[self.currentDriveIndex]
        QtWidgets.QMessageBox.information(self, "Current Drive", f"Current Drive: {currentDrive}")

        # 更新 treeView 的根索引为当前驱动器的路径
        self.treeView.setRootIndex(self.filemodel.index(currentDrive))

        # 更新按钮状态
        self.updateButtonState()

    def some_method(self):
        if not self.drives:
            QtWidgets.QMessageBox.warning(self, "警告", "没有可用的驱动器")
            return
    def init_signal_slots(self):
        """初始化信号槽连接"""

        self.rotateClockwiseButton.clicked.connect(self.rotateClockwise)
        self.rotateCounterclockwiseButton.clicked.connect(self.rotateCounterclockwise)
        self.newButton1.clicked.connect(self.handleNewButton1)
        self.newButton2.clicked.connect(self.handleNewButton2)

        self.pushButton_3.clicked.connect(self.save_e)
        self.pushButton_4.clicked.connect(self.show_yolo)
        self.pushButton_5.clicked.connect(self.show_maskrcnn)
        self.pushButton_6.clicked.connect(self.show_pointrend)
        self.treeView.clicked.connect(self.update_image)
        # 菜单栏槽函数
        self.Import.triggered.connect(self.openImage)
        self.log.triggered.connect(self.show_log)
        self.log_clear.triggered.connect(self.clear_log)

        self.addAnnotationButtons.triggered.connect(self.add_annotation)
        self.saveAnnotationButtons.triggered.connect(self.save_annotations)
        self.clearAnnotationButtons.triggered.connect(self.clear_annotations)
        self.loadAnnotationButtons.triggered.connect(self.load_annotations)
        self.convertImageFormatButtons.triggered.connect(self.convert_image_format)



    def update_image(self, index):
        new_imgName = self.filemodel.filePath(index)
        if new_imgName and new_imgName.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".JPG", ".JPEG", ".PNG", ".TIF", ".TIFF")):
            self.imgName = new_imgName
            self.pixmap = QPixmap(self.imgName)
            if self.pixmap.isNull():
                raise ValueError("Failed to load image.")
            self.display_scaled_image()
            self.add_log(f"加载了图片: {self.imgName}")

    def save_e(self):
        self.ewindow1=SaveE()
        self.ewindow1.show()


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
                directory_path = os.path.dirname(os.path.abspath(self.imgName))
                self.treeView.setRootIndex(self.filemodel.index(directory_path))  # 设置RootIndex
                '''
                self.yolo_detect()
                self.keypoint_detect()
                self.pointrend_detect()
                self.length_detect()
                '''
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
            if not self.label_image or self.label_image.size().width() == 0 or self.label_image.size().height() == 0:
                print("Error: label_image is not properly initialized or has zero size.")
                return

                # 计算当前的中心点
            old_center = self.label_image.rect().center()

            # 按比例缩放图片
            scaled_pixmap = self.pixmap.scaled(self.label_image.size() * self.scaleFactor, Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)

            # 设置旋转变换
            transform = QTransform().rotate(self.rotationAngle)
            rotated_pixmap = scaled_pixmap.transformed(transform, Qt.SmoothTransformation)

            # 设置缩放后的QPixmap
            self.label_image.setPixmap(rotated_pixmap)

            # 在图片上绘制批注
            painter = QPainter(self.label_image.pixmap())
            painter.setPen(QPen(Qt.red, 2))
            for ann in self.annotations:
                if ann['type'] == 'circle':
                    painter.drawEllipse(ann['x'], ann['y'], ann['radius'], ann['radius'])
            painter.end()

            self.label_image.adjustSize()

            # 确保标签的大小足够容纳缩放后的图片
            # self.label_image.setFixedSize(rotated_pixmap.size())

            # 计算新的中心点
            new_center = self.label_image.rect().center()

            # 计算偏移量并应用，使图片保持以原来位置的中心为放大缩小的中心
            delta = old_center - new_center
            self.label_image.move(self.label_image.pos() + delta)

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

    def closeEvent(self, event):
        log_content = self.logArea.toPlainText()
        print("关闭事件被触发")
        try:
            savelog.save_log(log_content)
        except Exception as e:
            print(f"保存日志时出错: {e}")
        event.accept()

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

    def add_annotation(self):
        """添加批注到图片"""
        try:
            if not self.imgName:
                QMessageBox.warning(self, "警告", "请先打开一张图片。")
                return

            # 假设批注为一个简单的列表，实际应用中可能会包含更多数据
            annotation = {'type': 'circle', 'x': 100, 'y': 100, 'radius': 50}
            self.annotations.append(annotation)
            self.display_scaled_image()
            self.add_log(f"添加了批注: {annotation}")
        except Exception as e:
            self.add_log(f"添加批注时出现错误: {e}")
            QMessageBox.critical(self, "错误", "添加批注时出现错误，请重试。")

    def save_annotations(self):
        """保存批注到 JSON 文件"""
        try:
            if not self.imgName:
                QMessageBox.warning(self, "警告", "请先打开一张图片。")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "保存批注", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, 'w') as file:
                    json.dump(self.annotations, file, indent=4)
                QMessageBox.information(self, "成功", "批注已保存。")
        except Exception as e:
            self.add_log(f"保存批注时出现错误: {e}")
            QMessageBox.critical(self, "错误", "保存批注时出现错误，请重试。")

    def load_annotations(self):
        """从 JSON 文件加载批注"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "打开批注文件", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, 'r') as file:
                    self.annotations = json.load(file)
                self.display_scaled_image()
                QMessageBox.information(self, "成功", "批注已加载。")
        except Exception as e:
            self.add_log(f"加载批注时出现错误: {e}")
            QMessageBox.critical(self, "错误", "加载批注时出现错误，请重试。")

    def convert_image_format(self):
        """转换图像格式"""
        try:
            if not self.imgName:
                QMessageBox.warning(self, "警告", "请先打开一张图片。")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "保存图像", "",
                                                       "JPEG Files (*.jpg *.jpeg);;PNG Files (*.png);;BMP Files (*.bmp);;TIFF Files (*.tif *.tiff);;All Files (*)")
            if file_name:
                self.pixmap.save(file_name)
                QMessageBox.information(self, "成功", "图像已保存。")
        except Exception as e:
            self.add_log(f"转换图像格式时出现错误: {e}")
            QMessageBox.critical(self, "错误", "转换图像格式时出现错误，请重试。")

    def clear_annotations(self):
        """清除所有批注"""
        try:
            self.annotations = []
            self.display_scaled_image()
            QMessageBox.information(self, "成功", "所有批注已清除。")
        except Exception as e:
            self.add_log(f"清除批注时出现错误: {e}")
            QMessageBox.critical(self, "错误", "清除批注时出现错误，请重试。")
