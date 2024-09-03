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

        # ��ʼ��ע���б�
        self.annotations = []

        # Ĭ�ϵ�ע������
        self.annotation_color = Qt.red
        self.annotation_pen_width = 2
        self.isDrawing = False
        self.current_annotation = None
        self.current_annotation_type = 'Line'
        self.current_text = ''

        # ��ʼ���û�����ؼ�
        self.init_controls()

        # �����źźͲ�
        self.startDrawingButton.clicked.connect(self.start_drawing)  # ��ʼ���ư�ť
        self.addAnnotationButton.clicked.connect(self.add_annotation)  # ���ע�Ͱ�ť
        self.saveAnnotationsButton.clicked.connect(self.save_annotations)  # ����ע�Ͱ�ť
        self.loadAnnotationsButton.clicked.connect(self.load_annotations)  # ����ע�Ͱ�ť
        self.clearAnnotationsButton.clicked.connect(self.clear_annotations)  # ���ע�Ͱ�ť
        self.colorButton.clicked.connect(self.choose_color)  # ѡ����ɫ��ť
        self.penWidthSpinBox.valueChanged.connect(self.update_pen_width)  # �ʿ�仯
        self.annotationTypeComboBox.currentIndexChanged.connect(self.change_annotation_type)  # ע�����͸ı�
        self.textEdit.textChanged.connect(self.update_text)  # �ı����ݸı�

    def init_controls(self):
        """
        ��ʼ���ؼ�����ť��SpinBox��ComboBox�ȣ��������ò��֡�
        """
        # �����ؼ�
        self.startDrawingButton = QPushButton('��ʼ����')
        self.addAnnotationButton = QPushButton('���ע��')
        self.saveAnnotationsButton = QPushButton('����ע��')
        self.loadAnnotationsButton = QPushButton('����ע��')
        self.clearAnnotationsButton = QPushButton('���ע��')
        self.colorButton = QPushButton('ѡ����ɫ')
        self.penWidthSpinBox = QSpinBox()
        self.annotationTypeComboBox = QComboBox()
        self.textEdit = QLineEdit()

        # ���ñʿ�SpinBox
        self.penWidthSpinBox.setRange(1, 10)
        self.penWidthSpinBox.setValue(self.annotation_pen_width)

        # ����ע������ComboBox
        self.annotationTypeComboBox.addItems(['��', '����', '��Բ', '�ı�'])

        # ���ò���
        controlLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        # ����ť�Ϳؼ���ӵ�������
        buttonLayout.addWidget(self.startDrawingButton)
        buttonLayout.addWidget(self.addAnnotationButton)
        buttonLayout.addWidget(self.saveAnnotationsButton)
        buttonLayout.addWidget(self.loadAnnotationsButton)
        buttonLayout.addWidget(self.clearAnnotationsButton)
        buttonLayout.addWidget(self.colorButton)
        buttonLayout.addWidget(QLabel('�ʿ�:'))
        buttonLayout.addWidget(self.penWidthSpinBox)
        buttonLayout.addWidget(QLabel('ע������:'))
        buttonLayout.addWidget(self.annotationTypeComboBox)
        buttonLayout.addWidget(QLabel('�ı�:'))
        buttonLayout.addWidget(self.textEdit)

        controlLayout.addLayout(buttonLayout)
        self.setLayout(controlLayout)

    def change_annotation_type(self):
        """
        ���ĵ�ǰ��ע�����͡�
        """
        self.current_annotation_type = self.annotationTypeComboBox.currentText()

    def update_text(self):
        """
        �����ı����ݡ�
        """
        self.current_text = self.textEdit.text()

    def start_drawing(self):
        """
        ��ʼ����ע�͡�
        """
        self.isDrawing = True

    def add_annotation(self):
        """
        ���ע�͵��б��У������õ�ǰע�����á�
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
            self.update()  # �ػ�ͼ������ʾע��

    def save_annotations(self):
        """
        ��ע�ͱ��浽�ļ��С�
        """
        file_name, _ = QFileDialog.getSaveFileName(self, '����ע��', '', 'JSON �ļ� (*.json)')
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(self.annotations, f)

    def load_annotations(self):
        """
        ���ļ��м���ע�͡�
        """
        file_name, _ = QFileDialog.getOpenFileName(self, '����ע��', '', 'JSON �ļ� (*.json)')
        if file_name:
            with open(file_name, 'r') as f:
                self.annotations = json.load(f)
                self.update()  # �ػ�ͼ������ʾ���ص�ע��

    def clear_annotations(self):
        """
        �������ע�͡�
        """
        self.annotations = []
        self.update()  # �ػ�ͼ�����Ƴ�ע��

    def paintEvent(self, event):
        """
        �����¼�������ע�͵�ͼ���ϡ�
        """
        super().paintEvent(event)  # ȷ�����û���� paintEvent

        painter = QPainter(self)
        for annotation in self.annotations:
            pen = QPen(QColor(annotation['color']), annotation['pen_width'])
            painter.setPen(pen)

            # ����ע�����ͻ��Ʋ�ͬ��ע��
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

            # ���ݵ�ǰע�����ͻ������ڻ��Ƶ�ע��
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
        ��갴���¼�����ʼ��ע�͵���ʼλ�á�
        """
        if self.isDrawing:
            if self.current_annotation_type in ['Line', 'Rectangle', 'Ellipse']:
                self.current_annotation = [event.pos(), event.pos()]
            elif self.current_annotation_type == 'Text':
                self.current_annotation = [event.pos()]
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        ����ƶ��¼������µ�ǰע�͵Ľ���λ�á�
        """
        if self.isDrawing and self.current_annotation:
            if self.current_annotation_type in ['Line', 'Rectangle', 'Ellipse']:
                self.current_annotation[1] = event.pos()
            elif self.current_annotation_type == 'Text':
                # �����ı�������Ҫ������ƶ�ʱ�����κ�����
                pass
            self.update()  # �ػ�ͼ������ʾ��ǰ��ע��
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        ����ͷ��¼������ע�͵Ļ��ƣ�����ע����ӵ��б��С�
        """
        if self.isDrawing and self.current_annotation:
            if self.current_annotation_type == 'Text':
                self.current_annotation.append(self.current_text)
            else:
                self.current_annotation[1] = event.pos()
            self.add_annotation()
        super().mouseReleaseEvent(event)

# �����ϸ���ã�
# AnnotationApp ��̳��� MyApp �࣬��չ��ע�͹��ܡ����������û���ͼ���ϻ��Ʋ�ͬ���͵�ע�ͣ��������������Ρ���Բ���ı�����
# �û�����ѡ��ע�͵���ɫ�ͱʿ��ı�ע�����ͣ������ı����ݣ���ͨ������ؼ�����ť���������ı���ȣ����в�����
# ע�Ϳ��Ա����浽 JSON �ļ��У�Ҳ���Դ� JSON �ļ��м��أ�֧���������ע�Ͳ����¿�ʼ���ơ�
