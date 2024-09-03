import sys
import json
from PyQt5.QtWidgets import QSpinBox, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QLineEdit, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtCore import pyqtSignal
from mainwindows import MyApp

class AnnotationApp(MyApp):
    def __init__(self):
        super().__init__()

        # 初始化注释列表
        self.annotations = []

        # 默认的注释设置
        self.annotation_color = Qt.red
        self.annotation_pen_width = 2
        self.isDrawing = False
        self.current_annotation = None
        self.current_annotation_type = 'Line'
        self.current_text = ''

        # 初始化用户界面控件
        self.init_controls()

        # 连接信号和槽
        self.startDrawingButton.clicked.connect(self.start_drawing)  # 开始绘制按钮
        self.addAnnotationButton.clicked.connect(self.add_annotation)  # 添加注释按钮
        self.saveAnnotationsButton.clicked.connect(self.save_annotations)  # 保存注释按钮
        self.loadAnnotationsButton.clicked.connect(self.load_annotations)  # 加载注释按钮
        self.clearAnnotationsButton.clicked.connect(self.clear_annotations)  # 清除注释按钮
        self.colorButton.clicked.connect(self.choose_color)  # 选择颜色按钮
        self.penWidthSpinBox.valueChanged.connect(self.update_pen_width)  # 笔宽变化
        self.annotationTypeComboBox.currentIndexChanged.connect(self.change_annotation_type)  # 注释类型改变
        self.textEdit.textChanged.connect(self.update_text)  # 文本内容改变

    def init_controls(self):
        """
        初始化控件（按钮、SpinBox、ComboBox等），并设置布局。
        """
        # 创建控件
        self.startDrawingButton = QPushButton('开始绘制')
        self.addAnnotationButton = QPushButton('添加注释')
        self.saveAnnotationsButton = QPushButton('保存注释')
        self.loadAnnotationsButton = QPushButton('加载注释')
        self.clearAnnotationsButton = QPushButton('清除注释')
        self.colorButton = QPushButton('选择颜色')
        self.penWidthSpinBox = QSpinBox()
        self.annotationTypeComboBox = QComboBox()
        self.textEdit = QLineEdit()

        # 设置笔宽SpinBox
        self.penWidthSpinBox.setRange(1, 10)
        self.penWidthSpinBox.setValue(self.annotation_pen_width)

        # 设置注释类型ComboBox
        self.annotationTypeComboBox.addItems(['线', '矩形', '椭圆', '文本'])

        # 设置布局
        controlLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        # 将按钮和控件添加到布局中
        buttonLayout.addWidget(self.startDrawingButton)
        buttonLayout.addWidget(self.addAnnotationButton)
        buttonLayout.addWidget(self.saveAnnotationsButton)
        buttonLayout.addWidget(self.loadAnnotationsButton)
        buttonLayout.addWidget(self.clearAnnotationsButton)
        buttonLayout.addWidget(self.colorButton)
        buttonLayout.addWidget(QLabel('笔宽:'))
        buttonLayout.addWidget(self.penWidthSpinBox)
        buttonLayout.addWidget(QLabel('注释类型:'))
        buttonLayout.addWidget(self.annotationTypeComboBox)
        buttonLayout.addWidget(QLabel('文本:'))
        buttonLayout.addWidget(self.textEdit)

        controlLayout.addLayout(buttonLayout)
        self.setLayout(controlLayout)

    def change_annotation_type(self):
        """
        更改当前的注释类型。
        """
        self.current_annotation_type = self.annotationTypeComboBox.currentText()

    def update_text(self):
        """
        更新文本内容。
        """
        self.current_text = self.textEdit.text()

    def start_drawing(self):
        """
        开始绘制注释。
        """
        self.isDrawing = True

    def add_annotation(self):
        """
        添加注释到列表中，并重置当前注释设置。
        """
        if self.current_annotation:
            self.annotations.append({
                'type': self.current_annotation_type,
                'data': self.current_annotation,
                'color': self.annotation_color.name(),
                'pen_width': self.annotation_pen_width,
                'text': self.current_text
            })
            self.current_annotation = None
            self.isDrawing = False
            self.current_text = ''
            self.textEdit.clear()
            self.update()  # 重绘图像以显示注释

    def save_annotations(self):
        """
        将注释保存到文件中。
        """
        file_name, _ = QFileDialog.getSaveFileName(self, '保存注释', '', 'JSON 文件 (*.json)')
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(self.annotations, f)

    def load_annotations(self):
        """
        从文件中加载注释。
        """
        file_name, _ = QFileDialog.getOpenFileName(self, '加载注释', '', 'JSON 文件 (*.json)')
        if file_name:
            with open(file_name, 'r') as f:
                self.annotations = json.load(f)
                self.update()  # 重绘图像以显示加载的注释

    def clear_annotations(self):
        """
        清除所有注释。
        """
        self.annotations = []
        self.update()  # 重绘图像以移除注释

    def paintEvent(self, event):
        """
        绘制事件，绘制注释到图像上。
        """
        super().paintEvent(event)  # 确保调用基类的 paintEvent

        painter = QPainter(self)
        for annotation in self.annotations:
            pen = QPen(QColor(annotation['color']), annotation['pen_width'])
            painter.setPen(pen)

            # 根据注释类型绘制不同的注释
            if annotation['type'] == 'Line':
                start, end = annotation['data']
                painter.drawLine(QPointF(*start), QPointF(*end))
            elif annotation['type'] == 'Rectangle':
                rect = QRectF(QPointF(*annotation['data'][0]), QPointF(*annotation['data'][1]))
                painter.drawRect(rect)
            elif annotation['type'] == 'Ellipse':
                rect = QRectF(QPointF(*annotation['data'][0]), QPointF(*annotation['data'][1]))
                painter.drawEllipse(rect)
            elif annotation['type'] == 'Text':
                pos, text = annotation['data']
                painter.drawText(QPointF(*pos), text)

        if self.isDrawing and self.current_annotation:
            pen = QPen(self.annotation_color, self.annotation_pen_width)
            painter.setPen(pen)

            # 根据当前注释类型绘制正在绘制的注释
            if self.current_annotation_type == 'Line':
                painter.drawLine(self.current_annotation[0], self.current_annotation[1])
            elif self.current_annotation_type == 'Rectangle':
                rect = QRectF(self.current_annotation[0], self.current_annotation[1])
                painter.drawRect(rect)
            elif self.current_annotation_type == 'Ellipse':
                rect = QRectF(self.current_annotation[0], self.current_annotation[1])
                painter.drawEllipse(rect)
            elif self.current_annotation_type == 'Text':
                painter.drawText(self.current_annotation[0], self.current_text)

    def mousePressEvent(self, event):
        """
        鼠标按下事件，初始化注释的起始位置。
        """
        if self.isDrawing:
            if self.current_annotation_type in ['Line', 'Rectangle', 'Ellipse']:
                self.current_annotation = [event.pos(), event.pos()]
            elif self.current_annotation_type == 'Text':
                self.current_annotation = [event.pos()]
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，更新当前注释的结束位置。
        """
        if self.isDrawing and self.current_annotation:
            if self.current_annotation_type in ['Line', 'Rectangle', 'Ellipse']:
                self.current_annotation[1] = event.pos()
            elif self.current_annotation_type == 'Text':
                # 对于文本，不需要在鼠标移动时更新任何内容
                pass
            self.update()  # 重绘图像以显示当前的注释
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件，完成注释的绘制，并将注释添加到列表中。
        """
        if self.isDrawing and self.current_annotation:
            if self.current_annotation_type == 'Text':
                self.current_annotation.append(self.current_text)
            else:
                self.current_annotation[1] = event.pos()
            self.add_annotation()
        super().mouseReleaseEvent(event)

# 类的详细作用：
# AnnotationApp 类继承自 MyApp 类，扩展了注释功能。该类允许用户在图像上绘制不同类型的注释（包括线条、矩形、椭圆和文本）。
# 用户可以选择注释的颜色和笔宽，改变注释类型，输入文本内容，并通过界面控件（按钮、下拉框、文本框等）进行操作。
# 注释可以被保存到 JSON 文件中，也可以从 JSON 文件中加载，支持清除所有注释并重新开始绘制。
