import os
import sys
import json
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from PIL.ExifTags import TAGS
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem, QTabWidget,
                             QGroupBox, QComboBox, QSpinBox, QSlider, QLineEdit, QColorDialog,
                             QFileDialog, QCheckBox, QMessageBox, QGridLayout, QSplitter,
                             QScrollArea, QFrame, QDoubleSpinBox, QProgressBar, QInputDialog,
                             QProgressDialog, QToolButton, QSizePolicy, QRadioButton, QButtonGroup,
                             QStackedWidget)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot, QPoint, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor, QFont, QPainter, QDragEnterEvent, QDropEvent, QFontDatabase, \
    QImage

# 应用样式表 - 优化版
APP_STYLESHEET = """
/* 主窗口样式 */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #f8f9fa, stop: 1 #e9ecef);
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* 卡片化效果 */
QGroupBox {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 12px;
    margin-top: 10px;
    padding-top: 12px;
    font-weight: bold;
    color: #2c3e50;
    font-size: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 4px 12px;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #7b68ee, stop: 1 #5f9ea0);
    color: white;
    border-radius: 8px;
    font-size: 14px;
}

/* 玻璃化效果 */
QFrame#preview_frame {
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* 按钮样式 - 更柔和的颜色 */
QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #7b68ee, stop: 1 #5f9ea0);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 10px 18px;
    font-weight: bold;
    margin: 3px;
    font-size: 14px;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #6a5acd, stop: 1 #4682b4);
}

QPushButton:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #5d4ac1, stop: 1 #3a6a8c);
}

/* 列表样式 */
QListWidget {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 8px;
    outline: none;
    font-size: 14px;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    font-size: 14px;
}

QListWidget::item:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #7b68ee, stop: 1 #5f9ea0);
    color: white;
    border-radius: 6px;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.75);
}

QTabBar::tab {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 18px;
    margin-right: 2px;
    font-size: 14px;
}

QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(255, 255, 255, 0.6);
}

/* 输入框样式 */
QLineEdit, QSpinBox, QComboBox {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #7b68ee;
    font-size: 14px;
    min-height: 20px;
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #2c3e50;
    width: 0;
    height: 0;
}

/* 滑动条样式 */
QSlider::groove:horizontal {
    border: 1px solid rgba(255, 255, 255, 0.4);
    height: 8px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #7b68ee, stop:1 #5f9ea0);
    border: 1px solid rgba(255, 255, 255, 0.6);
    width: 20px;
    margin: -8px 0;
    border-radius: 10px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 8px;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.8);
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #7b68ee, stop:1 #5f9ea0);
    border: 1px solid rgba(255, 255, 255, 0.6);
}

QCheckBox::indicator:checked::image {
    width: 16px;
    height: 16px;
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
}

/* 单选按钮样式 */
QRadioButton {
    spacing: 8px;
    font-size: 14px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.8);
}

QRadioButton::indicator:checked {
    border: 6px solid #7b68ee;
    background: white;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 5px;
    text-align: center;
    background: rgba(255, 255, 255, 0.6);
    font-size: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #7b68ee, stop:1 #5f9ea0);
    border-radius: 4px;
}

/* 滚动区域样式 */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    border: none;
    background: rgba(255, 255, 255, 0.4);
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(123, 104, 238, 0.7);
    border-radius: 6px;
    min-height: 25px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(123, 104, 238, 0.9);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* 标签样式 */
QLabel {
    color: #2c3e50;
    font-size: 14px;
}

QLabel#title_label {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
    padding: 12px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    margin: 6px;
}
"""


class WatermarkThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, app, output_path):
        super().__init__()
        self.app = app
        self.output_path = output_path
        self.canceled = False

    def run(self):
        total = len(self.app.images)
        for i, image_path in enumerate(self.app.images):
            if self.canceled:
                break
            try:
                self.app.export_single_image(image_path, self.output_path)
            except Exception as e:
                self.error.emit(f"导出图片 {os.path.basename(image_path)} 失败: {str(e)}")
            self.progress.emit(i + 1)
        self.finished.emit()

    def cancel(self):
        self.canceled = True


class DraggableLabel(QLabel):
    positionChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.7); border: 2px dashed #7b68ee; border-radius: 8px; font-size: 14px;")
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and (event.buttons() & Qt.LeftButton):
            self.move(self.mapToParent(event.pos() - self.offset))
            self.positionChanged.emit(self.x(), self.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)


class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化关键变量
        self.images = []
        self.current_image_index = -1
        self.per_image_settings = {}
        self.image_cache = {}
        self.current_settings_type = "shared"  # 默认使用共享设置
        self.draggable_watermark = None
        self.custom_position_mode = False

        # 默认共享设置
        self.default_shared_settings = {
            "type": "text",
            "text": "水印",
            "font_family": "Microsoft YaHei",
            "font_size": 40,
            "bold": False,
            "italic": False,
            "color": "#FFFFFF",
            "opacity": 80,
            "position": "右下角",
            "rotation": 0,
            "shadow": False,
            "shadow_color": "#000000",
            "shadow_offset": 2,
            "shadow_blur": 2,
            "outline": False,
            "outline_color": "#000000",
            "outline_width": 1,
            "image_path": "",
            "image_scale": 100,
            "output_format": "JPEG",
            "quality": 90,
            "resize_enabled": False,
            "resize_width": 0,
            "resize_height": 0,
            "resize_percent": 100,
            "naming_prefix": "",
            "naming_suffix": "_watermarked"
        }

        # 默认个性化设置
        self.default_per_image_settings = {
            "type": "text",
            "text": "",  # 为空时使用共享设置的文本
            "font_family": "Microsoft YaHei",
            "font_size": 40,
            "bold": False,
            "italic": False,
            "color": "#FFFFFF",
            "opacity": 80,
            "rotation": 0,
            "shadow": False,
            "shadow_color": "#000000",
            "shadow_offset": 2,
            "shadow_blur": 2,
            "outline": False,
            "outline_color": "#000000",
            "outline_width": 1,
            "image_path": "",
            "image_scale": 100,
            "offset_x": 0,
            "offset_y": 0
        }

        # 初始化共享设置
        self.shared_settings = self.default_shared_settings.copy()

        try:
            self.init_ui()
            self.load_settings()

            # 延迟更新预览的计时器
            self.preview_timer = QTimer()
            self.preview_timer.setSingleShot(True)
            self.preview_timer.timeout.connect(self.update_preview_delayed)
        except Exception as e:
            print(f"初始化错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def init_ui(self):
        self.setWindowTitle("高级图片水印工具 - 专业版")
        self.setGeometry(100, 100, 1600, 900)  # 增加窗口宽度以适应三栏布局

        # 应用样式表
        self.setStyleSheet(APP_STYLESHEET)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 使用水平布局分为三部分
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 左侧：图片列表区域 (20%)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)  # 比例2

        # 中间：预览区域 (50%)
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 5)  # 比例5

        # 右侧：参数设置区域 (30%)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)  # 比例3

    def create_left_panel(self):
        # 左侧面板 - 图片列表
        left_widget = QWidget()
        left_widget.setMaximumWidth(400)  # 限制最大宽度
        layout = QVBoxLayout(left_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel("📷 图片列表")
        title_label.setObjectName("title_label")
        layout.addWidget(title_label)

        # 导入按钮
        import_layout = QHBoxLayout()
        self.import_btn = QPushButton("📁 导入图片")
        self.import_btn.clicked.connect(self.import_images)
        import_layout.addWidget(self.import_btn)

        self.import_folder_btn = QPushButton("📂 导入文件夹")
        self.import_folder_btn.clicked.connect(self.import_folder)
        import_layout.addWidget(self.import_folder_btn)

        layout.addLayout(import_layout)

        # 清空按钮
        self.clear_btn = QPushButton("🗑️ 清空列表")
        self.clear_btn.clicked.connect(self.clear_images)
        layout.addWidget(self.clear_btn)

        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.currentRowChanged.connect(self.on_image_selected)
        layout.addWidget(self.image_list)

        return left_widget

    def create_center_panel(self):
        # 中间面板 - 预览区域
        center_widget = QWidget()
        layout = QVBoxLayout(center_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 预览控制
        preview_control_layout = QHBoxLayout()

        # 水印位置控制
        preview_control_layout.addWidget(QLabel("水印位置:"))
        self.position_combo = QComboBox()
        self.position_combo.addItems(["左上角", "中上", "右上角", "左中", "居中", "右中", "左下角", "中下", "右下角", "自定义拖拽"])
        self.position_combo.currentTextChanged.connect(self.on_position_changed)
        preview_control_layout.addWidget(self.position_combo)

        # 预览缩放
        preview_control_layout.addWidget(QLabel("预览缩放:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        preview_control_layout.addWidget(self.zoom_slider)

        self.zoom_label = QLabel("100%")
        preview_control_layout.addWidget(self.zoom_label)

        preview_control_layout.addStretch()
        layout.addLayout(preview_control_layout)

        # 预览图像区域
        preview_group = QGroupBox("👁️ 实时预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("preview_frame")
        preview_frame_layout = QVBoxLayout(self.preview_frame)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(500, 400)
        self.preview_label.setText("🎨 导入图片后预览将显示在这里")
        self.preview_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")

        # 设置预览标签可以接收拖拽
        self.preview_label.setAcceptDrops(True)
        self.preview_label.mousePressEvent = self.preview_mouse_press

        self.preview_scroll.setWidget(self.preview_label)
        preview_frame_layout.addWidget(self.preview_scroll)

        preview_layout.addWidget(self.preview_frame)
        layout.addWidget(preview_group)

        # 导出按钮
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addStretch()

        self.export_btn = QPushButton("🚀 导出所有图片")
        self.export_btn.clicked.connect(self.export_all_images)
        self.export_btn.setStyleSheet("font-size: 16px; padding: 14px 28px;")
        export_btn_layout.addWidget(self.export_btn)

        export_btn_layout.addStretch()
        layout.addLayout(export_btn_layout)

        return center_widget

    def create_right_panel(self):
        # 右侧面板 - 参数设置
        right_widget = QWidget()
        right_widget.setMaximumWidth(500)  # 限制最大宽度
        layout = QVBoxLayout(right_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)  # 连接标签页切换信号

        # 共享设置标签页
        self.shared_tab = self.create_shared_tab()
        self.tabs.addTab(self.shared_tab, "⚙️ 共享设置")

        # 个性化设置标签页
        self.per_image_tab = self.create_per_image_tab()
        self.tabs.addTab(self.per_image_tab, "🎨 个性化设置")

        # 导出设置标签页
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "📤 导出设置")

        # 模板管理标签页
        self.template_tab = self.create_template_tab()
        self.tabs.addTab(self.template_tab, "💾 模板管理")

        layout.addWidget(self.tabs)

        return right_widget

    def create_shared_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 水印类型选择
        type_group = QGroupBox("水印类型")
        type_layout = QHBoxLayout(type_group)

        self.watermark_type = QComboBox()
        self.watermark_type.addItems(["文本水印", "图片水印"])
        self.watermark_type.currentTextChanged.connect(self.on_watermark_type_changed)
        type_layout.addWidget(QLabel("类型:"))
        type_layout.addWidget(self.watermark_type)
        type_layout.addStretch()

        layout.addWidget(type_group)

        # 文本水印设置
        self.text_group = QGroupBox("文本水印设置")
        text_layout = QGridLayout(self.text_group)

        # 文本内容
        text_layout.addWidget(QLabel("文本内容:"), 0, 0)
        self.text_input = QLineEdit()
        self.text_input.setText("水印")
        self.text_input.textChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.text_input, 0, 1, 1, 2)

        # 从EXIF获取日期按钮
        self.exif_date_btn = QPushButton("使用EXIF日期")
        self.exif_date_btn.clicked.connect(self.use_exif_date)
        text_layout.addWidget(self.exif_date_btn, 0, 3)

        # 字体设置
        text_layout.addWidget(QLabel("字体:"), 1, 0)
        self.font_combo = QComboBox()
        # 获取系统所有字体，优先显示中文字体
        font_db = QFontDatabase()
        fonts = font_db.families()

        # 优先显示中文字体
        chinese_fonts = [f for f in fonts if any(char in f for char in '宋体黑体微软雅黑苹方') or
                         any(keyword in f.lower() for keyword in ['simsun', 'simhei', 'microsoft', 'pingfang'])]
        other_fonts = [f for f in fonts if f not in chinese_fonts]

        self.font_combo.addItems(chinese_fonts[:20] + other_fonts[:30])
        self.font_combo.setCurrentText("Microsoft YaHei")
        self.font_combo.currentTextChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.font_combo, 1, 1, 1, 3)

        # 字体大小
        text_layout.addWidget(QLabel("字体大小:"), 2, 0)
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 500)
        self.font_size.setValue(40)  # 减小默认值
        self.font_size.valueChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.font_size, 2, 1)

        # 粗体和斜体
        self.bold_check = QCheckBox("粗体")
        self.bold_check.stateChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.bold_check, 2, 2)

        self.italic_check = QCheckBox("斜体")
        self.italic_check.stateChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.italic_check, 2, 3)

        # 颜色选择
        text_layout.addWidget(QLabel("颜色:"), 3, 0)
        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet("background-color: #FFFFFF; border-radius: 4px; min-height: 20px;")
        self.color_btn.clicked.connect(self.choose_color)
        text_layout.addWidget(self.color_btn, 3, 1)

        # 透明度
        text_layout.addWidget(QLabel("透明度:"), 3, 2)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.opacity_slider, 3, 3)

        # 阴影效果
        self.shadow_check = QCheckBox("阴影效果")
        self.shadow_check.stateChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.shadow_check, 4, 0)

        text_layout.addWidget(QLabel("阴影颜色:"), 4, 1)
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setStyleSheet("background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.shadow_color_btn.clicked.connect(self.choose_shadow_color)
        text_layout.addWidget(self.shadow_color_btn, 4, 2)

        text_layout.addWidget(QLabel("阴影偏移:"), 4, 3)
        self.shadow_offset = QSpinBox()
        self.shadow_offset.setRange(1, 10)
        self.shadow_offset.setValue(2)
        self.shadow_offset.valueChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.shadow_offset, 4, 4)

        # 阴影模糊
        text_layout.addWidget(QLabel("阴影模糊:"), 5, 0)
        self.shadow_blur = QSpinBox()
        self.shadow_blur.setRange(0, 10)
        self.shadow_blur.setValue(2)
        self.shadow_blur.valueChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.shadow_blur, 5, 1)

        # 描边效果
        self.outline_check = QCheckBox("描边效果")
        self.outline_check.stateChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.outline_check, 6, 0)

        text_layout.addWidget(QLabel("描边颜色:"), 6, 1)
        self.outline_color_btn = QPushButton()
        self.outline_color_btn.setStyleSheet("background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.outline_color_btn.clicked.connect(self.choose_outline_color)
        text_layout.addWidget(self.outline_color_btn, 6, 2)

        text_layout.addWidget(QLabel("描边宽度:"), 6, 3)
        self.outline_width = QSpinBox()
        self.outline_width.setRange(1, 10)
        self.outline_width.setValue(1)
        self.outline_width.valueChanged.connect(self.on_shared_parameter_changed)
        text_layout.addWidget(self.outline_width, 6, 4)

        layout.addWidget(self.text_group)

        # 图片水印设置
        self.image_group = QGroupBox("图片水印设置")
        self.image_group.setVisible(False)
        image_layout = QGridLayout(self.image_group)

        # 选择图片水印
        image_layout.addWidget(QLabel("水印图片:"), 0, 0)
        self.image_path_label = QLabel("未选择")
        image_layout.addWidget(self.image_path_label, 0, 1)

        self.select_image_btn = QPushButton("选择图片")
        self.select_image_btn.clicked.connect(self.select_watermark_image)
        image_layout.addWidget(self.select_image_btn, 0, 2)

        # 缩放设置
        image_layout.addWidget(QLabel("缩放比例:"), 1, 0)
        self.image_scale = QSpinBox()
        self.image_scale.setRange(10, 500)
        self.image_scale.setValue(100)
        self.image_scale.setSuffix("%")
        self.image_scale.valueChanged.connect(self.on_shared_parameter_changed)
        image_layout.addWidget(self.image_scale, 1, 1)

        # 透明度
        image_layout.addWidget(QLabel("透明度:"), 1, 2)
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 100)
        self.image_opacity_slider.setValue(80)
        self.image_opacity_slider.valueChanged.connect(self.on_shared_parameter_changed)
        image_layout.addWidget(self.image_opacity_slider, 1, 3)

        layout.addWidget(self.image_group)

        # 旋转设置
        rotation_group = QGroupBox("旋转")
        rotation_layout = QHBoxLayout(rotation_group)

        rotation_layout.addWidget(QLabel("旋转角度:"))
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.on_rotation_changed)
        rotation_layout.addWidget(self.rotation_slider)

        self.rotation_value = QLabel("0°")
        rotation_layout.addWidget(self.rotation_value)

        self.rotation_reset_btn = QPushButton("重置")
        self.rotation_reset_btn.clicked.connect(self.reset_rotation)
        rotation_layout.addWidget(self.rotation_reset_btn)

        layout.addWidget(rotation_group)

        layout.addStretch()

        return tab

    def create_per_image_tab(self):
        # 个性化设置标签页 - 与共享设置相同的功能
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 提示信息
        info_label = QLabel("⚠️ 个性化设置仅对当前选中的图片生效")
        info_label.setStyleSheet(
            "background: rgba(255, 235, 59, 0.3); padding: 10px; border-radius: 6px; font-weight: bold;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 水印类型选择
        type_group = QGroupBox("水印类型")
        type_layout = QHBoxLayout(type_group)

        self.per_image_watermark_type = QComboBox()
        self.per_image_watermark_type.addItems(["文本水印", "图片水印"])
        self.per_image_watermark_type.currentTextChanged.connect(self.on_per_image_watermark_type_changed)
        type_layout.addWidget(QLabel("类型:"))
        type_layout.addWidget(self.per_image_watermark_type)
        type_layout.addStretch()

        layout.addWidget(type_group)

        # 文本水印设置
        self.per_image_text_group = QGroupBox("文本水印设置")
        text_layout = QGridLayout(self.per_image_text_group)

        # 文本内容
        text_layout.addWidget(QLabel("文本内容:"), 0, 0)
        self.per_image_text_input = QLineEdit()
        self.per_image_text_input.setPlaceholderText("为空时使用共享设置的文本内容")
        self.per_image_text_input.textChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_text_input, 0, 1, 1, 2)

        # 从EXIF获取日期按钮
        self.per_image_exif_date_btn = QPushButton("使用EXIF日期")
        self.per_image_exif_date_btn.clicked.connect(self.use_exif_date_per_image)
        text_layout.addWidget(self.per_image_exif_date_btn, 0, 3)

        # 字体设置
        text_layout.addWidget(QLabel("字体:"), 1, 0)
        self.per_image_font_combo = QComboBox()
        font_db = QFontDatabase()
        fonts = font_db.families()
        chinese_fonts = [f for f in fonts if any(char in f for char in '宋体黑体微软雅黑苹方') or
                         any(keyword in f.lower() for keyword in ['simsun', 'simhei', 'microsoft', 'pingfang'])]
        other_fonts = [f for f in fonts if f not in chinese_fonts]
        self.per_image_font_combo.addItems(chinese_fonts[:20] + other_fonts[:30])
        self.per_image_font_combo.setCurrentText("Microsoft YaHei")
        self.per_image_font_combo.currentTextChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_font_combo, 1, 1, 1, 3)

        # 字体大小
        text_layout.addWidget(QLabel("字体大小:"), 2, 0)
        self.per_image_font_size = QSpinBox()
        self.per_image_font_size.setRange(10, 500)
        self.per_image_font_size.setValue(40)  # 减小默认值
        self.per_image_font_size.valueChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_font_size, 2, 1)

        # 粗体和斜体
        self.per_image_bold_check = QCheckBox("粗体")
        self.per_image_bold_check.stateChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_bold_check, 2, 2)

        self.per_image_italic_check = QCheckBox("斜体")
        self.per_image_italic_check.stateChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_italic_check, 2, 3)

        # 颜色选择
        text_layout.addWidget(QLabel("颜色:"), 3, 0)
        self.per_image_color_btn = QPushButton()
        self.per_image_color_btn.setStyleSheet("background-color: #FFFFFF; border-radius: 4px; min-height: 20px;")
        self.per_image_color_btn.clicked.connect(self.choose_per_image_color)
        text_layout.addWidget(self.per_image_color_btn, 3, 1)

        # 透明度
        text_layout.addWidget(QLabel("透明度:"), 3, 2)
        self.per_image_opacity_slider = QSlider(Qt.Horizontal)
        self.per_image_opacity_slider.setRange(0, 100)
        self.per_image_opacity_slider.setValue(80)
        self.per_image_opacity_slider.valueChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_opacity_slider, 3, 3)

        # 阴影效果
        self.per_image_shadow_check = QCheckBox("阴影效果")
        self.per_image_shadow_check.stateChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_shadow_check, 4, 0)

        text_layout.addWidget(QLabel("阴影颜色:"), 4, 1)
        self.per_image_shadow_color_btn = QPushButton()
        self.per_image_shadow_color_btn.setStyleSheet(
            "background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.per_image_shadow_color_btn.clicked.connect(self.choose_per_image_shadow_color)
        text_layout.addWidget(self.per_image_shadow_color_btn, 4, 2)

        text_layout.addWidget(QLabel("阴影偏移:"), 4, 3)
        self.per_image_shadow_offset = QSpinBox()
        self.per_image_shadow_offset.setRange(1, 10)
        self.per_image_shadow_offset.setValue(2)
        self.per_image_shadow_offset.valueChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_shadow_offset, 4, 4)

        # 阴影模糊
        text_layout.addWidget(QLabel("阴影模糊:"), 5, 0)
        self.per_image_shadow_blur = QSpinBox()
        self.per_image_shadow_blur.setRange(0, 10)
        self.per_image_shadow_blur.setValue(2)
        self.per_image_shadow_blur.valueChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_shadow_blur, 5, 1)

        # 描边效果
        self.per_image_outline_check = QCheckBox("描边效果")
        self.per_image_outline_check.stateChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_outline_check, 6, 0)

        text_layout.addWidget(QLabel("描边颜色:"), 6, 1)
        self.per_image_outline_color_btn = QPushButton()
        self.per_image_outline_color_btn.setStyleSheet(
            "background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.per_image_outline_color_btn.clicked.connect(self.choose_per_image_outline_color)
        text_layout.addWidget(self.per_image_outline_color_btn, 6, 2)

        text_layout.addWidget(QLabel("描边宽度:"), 6, 3)
        self.per_image_outline_width = QSpinBox()
        self.per_image_outline_width.setRange(1, 10)
        self.per_image_outline_width.setValue(1)
        self.per_image_outline_width.valueChanged.connect(self.on_per_image_parameter_changed)
        text_layout.addWidget(self.per_image_outline_width, 6, 4)

        layout.addWidget(self.per_image_text_group)

        # 图片水印设置
        self.per_image_image_group = QGroupBox("图片水印设置")
        self.per_image_image_group.setVisible(False)
        image_layout = QGridLayout(self.per_image_image_group)

        # 选择图片水印
        image_layout.addWidget(QLabel("水印图片:"), 0, 0)
        self.per_image_image_path_label = QLabel("未选择")
        image_layout.addWidget(self.per_image_image_path_label, 0, 1)

        self.per_image_select_image_btn = QPushButton("选择图片")
        self.per_image_select_image_btn.clicked.connect(self.select_per_image_watermark_image)
        image_layout.addWidget(self.per_image_select_image_btn, 0, 2)

        # 缩放设置
        image_layout.addWidget(QLabel("缩放比例:"), 1, 0)
        self.per_image_image_scale = QSpinBox()
        self.per_image_image_scale.setRange(10, 500)
        self.per_image_image_scale.setValue(100)
        self.per_image_image_scale.setSuffix("%")
        self.per_image_image_scale.valueChanged.connect(self.on_per_image_parameter_changed)
        image_layout.addWidget(self.per_image_image_scale, 1, 1)

        # 透明度
        image_layout.addWidget(QLabel("透明度:"), 1, 2)
        self.per_image_image_opacity_slider = QSlider(Qt.Horizontal)
        self.per_image_image_opacity_slider.setRange(0, 100)
        self.per_image_image_opacity_slider.setValue(80)
        self.per_image_image_opacity_slider.valueChanged.connect(self.on_per_image_parameter_changed)
        image_layout.addWidget(self.per_image_image_opacity_slider, 1, 3)

        layout.addWidget(self.per_image_image_group)

        # 旋转设置
        rotation_group = QGroupBox("旋转")
        rotation_layout = QHBoxLayout(rotation_group)

        rotation_layout.addWidget(QLabel("旋转角度:"))
        self.per_image_rotation_slider = QSlider(Qt.Horizontal)
        self.per_image_rotation_slider.setRange(0, 360)
        self.per_image_rotation_slider.setValue(0)
        self.per_image_rotation_slider.valueChanged.connect(self.on_per_image_rotation_changed)
        rotation_layout.addWidget(self.per_image_rotation_slider)

        self.per_image_rotation_value = QLabel("0°")
        rotation_layout.addWidget(self.per_image_rotation_value)

        self.per_image_rotation_reset_btn = QPushButton("重置")
        self.per_image_rotation_reset_btn.clicked.connect(self.reset_per_image_rotation)
        rotation_layout.addWidget(self.per_image_rotation_reset_btn)

        layout.addWidget(rotation_group)

        # 位置偏移设置
        offset_group = QGroupBox("位置偏移")
        offset_layout = QGridLayout(offset_group)

        offset_layout.addWidget(QLabel("水平偏移:"), 0, 0)
        self.per_image_offset_x = QSpinBox()
        self.per_image_offset_x.setRange(-500, 500)
        self.per_image_offset_x.setValue(0)
        self.per_image_offset_x.valueChanged.connect(self.on_per_image_parameter_changed)
        offset_layout.addWidget(self.per_image_offset_x, 0, 1)

        offset_layout.addWidget(QLabel("垂直偏移:"), 0, 2)
        self.per_image_offset_y = QSpinBox()
        self.per_image_offset_y.setRange(-500, 500)
        self.per_image_offset_y.setValue(0)
        self.per_image_offset_y.valueChanged.connect(self.on_per_image_parameter_changed)
        offset_layout.addWidget(self.per_image_offset_y, 0, 3)

        layout.addWidget(offset_group)

        layout.addStretch()

        return tab

    def create_export_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 输出格式
        format_group = QGroupBox("输出设置")
        format_layout = QGridLayout(format_group)

        format_layout.addWidget(QLabel("输出格式:"), 0, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo, 0, 1)

        # JPEG质量设置
        format_layout.addWidget(QLabel("JPEG质量:"), 0, 2)
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        format_layout.addWidget(self.quality_slider, 0, 3)

        self.quality_label = QLabel("90")
        format_layout.addWidget(self.quality_label, 0, 4)

        # 输出文件夹
        format_layout.addWidget(QLabel("输出文件夹:"), 1, 0)
        self.output_path_label = QLabel("未选择")
        format_layout.addWidget(self.output_path_label, 1, 1, 1, 2)

        self.select_output_btn = QPushButton("选择文件夹")
        self.select_output_btn.clicked.connect(self.select_output_folder)
        format_layout.addWidget(self.select_output_btn, 1, 3)

        layout.addWidget(format_group)

        # 文件命名规则
        naming_group = QGroupBox("文件命名")
        naming_layout = QGridLayout(naming_group)

        naming_layout.addWidget(QLabel("前缀:"), 0, 0)
        self.prefix_input = QLineEdit()
        self.prefix_input.textChanged.connect(self.on_shared_parameter_changed)
        naming_layout.addWidget(self.prefix_input, 0, 1)

        naming_layout.addWidget(QLabel("后缀:"), 1, 0)
        self.suffix_input = QLineEdit("_watermarked")
        self.suffix_input.textChanged.connect(self.on_shared_parameter_changed)
        naming_layout.addWidget(self.suffix_input, 1, 1)

        layout.addWidget(naming_group)

        # 图片尺寸调整
        resize_group = QGroupBox("图片尺寸调整")
        resize_layout = QGridLayout(resize_group)

        self.resize_check = QCheckBox("调整图片尺寸")
        self.resize_check.stateChanged.connect(self.on_resize_changed)
        resize_layout.addWidget(self.resize_check, 0, 0, 1, 2)

        # 尺寸调整方式
        resize_method_layout = QHBoxLayout()
        self.resize_method_group = QButtonGroup()

        self.resize_percent_radio = QRadioButton("按百分比")
        self.resize_percent_radio.setChecked(True)
        self.resize_method_group.addButton(self.resize_percent_radio)
        resize_method_layout.addWidget(self.resize_percent_radio)

        self.resize_dimension_radio = QRadioButton("按尺寸")
        self.resize_method_group.addButton(self.resize_dimension_radio)
        resize_method_layout.addWidget(self.resize_dimension_radio)

        self.resize_method_group.buttonToggled.connect(self.on_resize_method_changed)
        resize_layout.addLayout(resize_method_layout, 1, 0, 1, 4)

        # 百分比调整
        resize_layout.addWidget(QLabel("缩放百分比:"), 2, 0)
        self.resize_percent = QSpinBox()
        self.resize_percent.setRange(1, 500)
        self.resize_percent.setValue(100)
        self.resize_percent.setSuffix("%")
        self.resize_percent.valueChanged.connect(self.on_shared_parameter_changed)
        resize_layout.addWidget(self.resize_percent, 2, 1)

        # 尺寸调整
        resize_layout.addWidget(QLabel("宽度:"), 3, 0)
        self.resize_width = QSpinBox()
        self.resize_width.setRange(1, 10000)
        self.resize_width.setValue(800)
        self.resize_width.setSuffix(" px")
        self.resize_width.setEnabled(False)
        self.resize_width.valueChanged.connect(self.on_shared_parameter_changed)
        resize_layout.addWidget(self.resize_width, 3, 1)

        resize_layout.addWidget(QLabel("高度:"), 3, 2)
        self.resize_height = QSpinBox()
        self.resize_height.setRange(1, 10000)
        self.resize_height.setValue(600)
        self.resize_height.setSuffix(" px")
        self.resize_height.setEnabled(False)
        self.resize_height.valueChanged.connect(self.on_shared_parameter_changed)
        resize_layout.addWidget(self.resize_height, 3, 3)

        # 保持宽高比
        self.keep_aspect_check = QCheckBox("保持宽高比")
        self.keep_aspect_check.setChecked(True)
        self.keep_aspect_check.stateChanged.connect(self.on_shared_parameter_changed)
        resize_layout.addWidget(self.keep_aspect_check, 4, 0, 1, 2)

        layout.addWidget(resize_group)

        layout.addStretch()

        return tab

    def create_template_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 模板操作按钮
        template_btn_layout = QHBoxLayout()

        self.save_template_btn = QPushButton("保存当前设置为模板")
        self.save_template_btn.clicked.connect(self.save_template)
        template_btn_layout.addWidget(self.save_template_btn)

        self.load_template_btn = QPushButton("加载模板")
        self.load_template_btn.clicked.connect(self.load_template)
        template_btn_layout.addWidget(self.load_template_btn)

        self.delete_template_btn = QPushButton("删除模板")
        self.delete_template_btn.clicked.connect(self.delete_template)
        template_btn_layout.addWidget(self.delete_template_btn)

        layout.addLayout(template_btn_layout)

        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self.load_template_from_list)
        layout.addWidget(self.template_list)

        # 加载默认模板
        self.load_template_list()

        # 自动加载设置
        auto_load_group = QGroupBox("自动加载设置")
        auto_load_layout = QHBoxLayout(auto_load_group)

        self.auto_load_check = QCheckBox("启动时自动加载上次使用的设置")
        auto_load_layout.addWidget(self.auto_load_check)

        layout.addWidget(auto_load_group)

        layout.addStretch()

        return tab

    def on_tab_changed(self, index):
        """标签页切换时的处理"""
        if index == 0:  # 共享设置标签页
            self.current_settings_type = "shared"
        elif index == 1:  # 个性化设置标签页
            self.current_settings_type = "per_image"
            # 更新个性化设置UI
            if self.current_image_index >= 0:
                self.apply_per_image_settings_to_ui()

        # 更新预览
        self.update_preview()

    def on_shared_parameter_changed(self):
        """共享参数改变时的处理"""
        # 保存共享设置
        self.save_shared_settings_from_ui()

        # 如果当前使用的是共享设置，则更新预览
        if self.current_settings_type == "shared":
            self.schedule_preview_update()

    def on_per_image_parameter_changed(self):
        """个性化参数改变时的处理"""
        # 保存个性化设置
        self.save_per_image_settings_from_ui()

        # 如果当前使用的是个性化设置，则更新预览
        if self.current_settings_type == "per_image":
            self.schedule_preview_update()

    def on_watermark_type_changed(self, text):
        is_text = text == "文本水印"
        self.text_group.setVisible(is_text)
        self.image_group.setVisible(not is_text)
        self.on_shared_parameter_changed()

    def on_per_image_watermark_type_changed(self, text):
        is_text = text == "文本水印"
        self.per_image_text_group.setVisible(is_text)
        self.per_image_image_group.setVisible(not is_text)
        self.on_per_image_parameter_changed()

    def on_format_changed(self, text):
        is_jpeg = text == "JPEG"
        self.quality_slider.setEnabled(is_jpeg)
        self.quality_label.setEnabled(is_jpeg)

    def on_quality_changed(self, value):
        self.quality_label.setText(str(value))

    def on_resize_changed(self, state):
        enabled = state == Qt.Checked
        self.resize_percent.setEnabled(enabled and self.resize_percent_radio.isChecked())
        self.resize_width.setEnabled(enabled and self.resize_dimension_radio.isChecked())
        self.resize_height.setEnabled(enabled and self.resize_dimension_radio.isChecked())
        self.keep_aspect_check.setEnabled(enabled and self.resize_dimension_radio.isChecked())
        self.on_shared_parameter_changed()

    def on_resize_method_changed(self, button, checked):
        if not checked:
            return

        is_percent = button == self.resize_percent_radio
        self.resize_percent.setEnabled(is_percent and self.resize_check.isChecked())
        self.resize_width.setEnabled(not is_percent and self.resize_check.isChecked())
        self.resize_height.setEnabled(not is_percent and self.resize_check.isChecked())
        self.keep_aspect_check.setEnabled(not is_percent and self.resize_check.isChecked())
        self.on_shared_parameter_changed()

    def on_position_changed(self, position):
        if position == "自定义拖拽":
            self.enable_custom_position()
        else:
            self.disable_custom_position()
            self.schedule_preview_update()

    def on_rotation_changed(self, value):
        self.rotation_value.setText(f"{value}°")
        self.on_shared_parameter_changed()

    def on_per_image_rotation_changed(self, value):
        self.per_image_rotation_value.setText(f"{value}°")
        self.on_per_image_parameter_changed()

    def on_zoom_changed(self, value):
        self.zoom_label.setText(f"{value}%")
        self.update_preview()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            self.on_shared_parameter_changed()

    def choose_per_image_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.per_image_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            # 更新个性化设置中的颜色
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                self.per_image_settings[image_path]["color"] = color.name()
            self.on_per_image_parameter_changed()

    def choose_shadow_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.shadow_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            self.on_shared_parameter_changed()

    def choose_per_image_shadow_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.per_image_shadow_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            # 更新个性化设置中的阴影颜色
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                self.per_image_settings[image_path]["shadow_color"] = color.name()
            self.on_per_image_parameter_changed()

    def choose_outline_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.outline_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            self.on_shared_parameter_changed()

    def choose_per_image_outline_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.per_image_outline_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border-radius: 4px; min-height: 20px;")
            # 更新个性化设置中的描边颜色
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                self.per_image_settings[image_path]["outline_color"] = color.name()
            self.on_per_image_parameter_changed()

    def select_watermark_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "",
                                              "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if path:
            self.image_path_label.setText(os.path.basename(path))
            self.shared_settings["image_path"] = path
            self.on_shared_parameter_changed()

    def select_per_image_watermark_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "",
                                              "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if path:
            self.per_image_image_path_label.setText(os.path.basename(path))
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                self.per_image_settings[image_path]["image_path"] = path
            self.on_per_image_parameter_changed()

    def select_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_path_label.setText(path)

    def import_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "选择图片", "",
                                                "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if paths:
            self.add_images(paths)

    def import_folder(self):
        path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if path:
            # 获取文件夹中所有支持的图片文件
            extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
            image_paths = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        image_paths.append(os.path.join(root, file))

            if image_paths:
                self.add_images(image_paths)
            else:
                QMessageBox.warning(self, "警告", "选择的文件夹中没有找到支持的图片文件")

    def add_images(self, paths):
        for path in paths:
            if path not in self.images:
                self.images.append(path)

                # 为每张图片初始化个性化设置（使用默认值）
                self.per_image_settings[path] = self.default_per_image_settings.copy()

                # 创建列表项
                item = QListWidgetItem()
                item.setText(os.path.basename(path))

                # 创建缩略图
                try:
                    image = self.load_and_fix_image(path)
                    if image:
                        # 确保图片是RGB模式
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image_rgb = image
                        data = image_rgb.tobytes("raw", "RGB")
                        qimage = QImage(data, image_rgb.size[0], image_rgb.size[1], QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qimage)

                        # 缩放缩略图
                        thumb = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item.setIcon(QIcon(thumb))
                except Exception as e:
                    print(f"创建缩略图错误: {str(e)}")

                self.image_list.addItem(item)

        # 如果有图片，选择第一个
        if self.images and self.current_image_index == -1:
            self.image_list.setCurrentRow(0)

    def load_and_fix_image(self, path):
        """加载并修复图片（处理方向、模式等问题）"""
        try:
            if path in self.image_cache:
                return self.image_cache[path].copy()

            image = Image.open(path)
            image = self.fix_image_orientation(image)

            if image.mode != 'RGB':
                image = image.convert('RGB')

            self.image_cache[path] = image.copy()
            return image
        except Exception as e:
            print(f"加载图片错误: {str(e)}")
            return None

    def fix_image_orientation(self, image):
        """修复图片方向（处理EXIF方向信息）"""
        try:
            exif = image._getexif()
            if exif:
                orientation_tag = 274
                if orientation_tag in exif:
                    orientation = exif[orientation_tag]

                    if orientation == 2:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        image = image.rotate(180)
                    elif orientation == 4:
                        image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    elif orientation == 5:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(270)
                    elif orientation == 6:
                        image = image.rotate(270)
                    elif orientation == 7:
                        image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(90)
                    elif orientation == 8:
                        image = image.rotate(90)
        except Exception as e:
            print(f"修复图片方向错误: {str(e)}")

        return image

    def clear_images(self):
        """清空图片列表并重置所有参数"""
        self.images.clear()
        self.image_list.clear()
        self.current_image_index = -1
        self.per_image_settings.clear()
        self.image_cache.clear()

        # 重置共享设置为默认值
        self.shared_settings = self.default_shared_settings.copy()

        # 重置UI控件为默认值
        self.apply_shared_settings_to_ui()

        # 重置个性化设置UI为默认值
        self.reset_per_image_ui_to_default()

        self.preview_label.setText("🎨 导入图片后预览将显示在这里")
        if self.draggable_watermark:
            self.draggable_watermark.setParent(None)
            self.draggable_watermark = None

        # 重置当前设置类型
        self.current_settings_type = "shared"
        self.tabs.setCurrentIndex(0)

    def reset_per_image_ui_to_default(self):
        """重置个性化设置UI为默认值"""
        self.per_image_watermark_type.setCurrentText("文本水印")
        self.per_image_text_input.clear()
        self.per_image_font_combo.setCurrentText("Microsoft YaHei")
        self.per_image_font_size.setValue(40)
        self.per_image_bold_check.setChecked(False)
        self.per_image_italic_check.setChecked(False)
        self.per_image_color_btn.setStyleSheet("background-color: #FFFFFF; border-radius: 4px; min-height: 20px;")
        self.per_image_opacity_slider.setValue(80)
        self.per_image_rotation_slider.setValue(0)
        self.per_image_shadow_check.setChecked(False)
        self.per_image_shadow_color_btn.setStyleSheet(
            "background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.per_image_shadow_offset.setValue(2)
        self.per_image_shadow_blur.setValue(2)
        self.per_image_outline_check.setChecked(False)
        self.per_image_outline_color_btn.setStyleSheet(
            "background-color: #000000; border-radius: 4px; min-height: 20px;")
        self.per_image_outline_width.setValue(1)
        self.per_image_image_path_label.setText("未选择")
        self.per_image_image_scale.setValue(100)
        self.per_image_image_opacity_slider.setValue(80)
        self.per_image_offset_x.setValue(0)
        self.per_image_offset_y.setValue(0)

    def on_image_selected(self, index):
        if index >= 0 and index < len(self.images):
            self.current_image_index = index
            # 切换到个性化设置标签页
            self.tabs.setCurrentIndex(1)
            self.current_settings_type = "per_image"
            # 更新个性化设置UI
            self.apply_per_image_settings_to_ui()
            self.update_preview()

    def preview_mouse_press(self, event):
        if event.button() == Qt.LeftButton and self.custom_position_mode:
            self.add_draggable_watermark(event.pos())

    def enable_custom_position(self):
        self.custom_position_mode = True
        self.preview_label.setText("👆 点击图片放置水印，然后拖拽调整位置")
        self.preview_label.setCursor(Qt.CrossCursor)

    def disable_custom_position(self):
        self.custom_position_mode = False
        self.preview_label.setCursor(Qt.ArrowCursor)
        if self.draggable_watermark:
            self.draggable_watermark.setParent(None)
            self.draggable_watermark = None

    def add_draggable_watermark(self, pos):
        if self.draggable_watermark:
            self.draggable_watermark.setParent(None)

        self.draggable_watermark = DraggableLabel(self.preview_label)

        # 获取当前设置类型
        if self.current_settings_type == "shared":
            watermark_type = self.watermark_type.currentText()
        else:
            watermark_type = self.per_image_watermark_type.currentText()

        if watermark_type == "文本水印":
            if self.current_settings_type == "shared":
                text = self.text_input.text()
                font_size = self.font_size.value()
                font_family = self.font_combo.currentText()
                bold = self.bold_check.isChecked()
                italic = self.italic_check.isChecked()
                color_btn = self.color_btn
            else:
                text = self.get_current_per_image_text()
                font_size = self.per_image_font_size.value()
                font_family = self.per_image_font_combo.currentText()
                bold = self.per_image_bold_check.isChecked()
                italic = self.per_image_italic_check.isChecked()
                color_btn = self.per_image_color_btn

            self.draggable_watermark.setText(text)

            font = QFont(font_family, min(font_size // 10, 50))
            font.setBold(bold)
            font.setItalic(italic)
            self.draggable_watermark.setFont(font)

            # 修复颜色获取逻辑
            color_style = color_btn.styleSheet()
            if "background-color:" in color_style:
                color = color_style.split("background-color:")[1].split(";")[0].strip()
            else:
                color = "#FFFFFF"  # 默认白色

            self.draggable_watermark.setStyleSheet(
                f"color: {color}; background-color: rgba(255, 255, 255, 0.7); border: 2px dashed #7b68ee; border-radius: 8px; font-size: 14px;")
        else:
            if self.current_settings_type == "shared":
                image_path = self.shared_settings["image_path"]
                scale = self.image_scale.value()
            else:
                image_path = self.get_current_per_image_path()
                scale = self.per_image_image_scale.value()

            if image_path and os.path.exists(image_path):
                try:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        scale = scale / 100.0
                        new_size = QSize(int(pixmap.width() * scale), int(pixmap.height() * scale))
                        pixmap = pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.draggable_watermark.setPixmap(pixmap)
                except:
                    pass

        self.draggable_watermark.adjustSize()
        self.draggable_watermark.move(pos)
        self.draggable_watermark.show()
        self.draggable_watermark.positionChanged.connect(self.on_watermark_dragged)

    def on_watermark_dragged(self, x, y):
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            self.per_image_settings[image_path]["offset_x"] = x
            self.per_image_settings[image_path]["offset_y"] = y
            self.schedule_preview_update()

    def schedule_preview_update(self):
        self.preview_timer.start(300)

    def update_preview_delayed(self):
        self.update_preview()

    def update_preview(self):
        if self.current_image_index < 0 or self.current_image_index >= len(self.images):
            return

        image_path = self.images[self.current_image_index]

        try:
            original_image = self.load_and_fix_image(image_path)
            if original_image is None:
                self.preview_label.setText("无法加载图片")
                return

            # 调整图片尺寸
            if self.resize_check.isChecked():
                if self.resize_percent_radio.isChecked():
                    percent = self.resize_percent.value()
                    new_width = int(original_image.size[0] * percent / 100)
                    new_height = int(original_image.size[1] * percent / 100)
                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    width = self.resize_width.value()
                    height = self.resize_height.value()

                    if self.keep_aspect_check.isChecked():
                        original_ratio = original_image.size[0] / original_image.size[1]
                        if width / height > original_ratio:
                            new_width = int(height * original_ratio)
                            new_height = height
                        else:
                            new_width = width
                            new_height = int(width / original_ratio)
                    else:
                        new_width = width
                        new_height = height

                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 添加水印
            watermarked_image = self.add_watermark_to_image(original_image)

            # 转换为QPixmap并显示
            watermarked_image = watermarked_image.convert("RGB")
            data = watermarked_image.tobytes("raw", "RGB")
            qimage = QImage(data, watermarked_image.size[0], watermarked_image.size[1], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # 缩放以适应预览区域
            zoom_factor = self.zoom_slider.value() / 100.0
            preview_size = self.preview_label.size()
            scaled_width = int(preview_size.width() * zoom_factor)
            scaled_height = int(preview_size.height() * zoom_factor)

            scaled_pixmap = pixmap.scaled(scaled_width, scaled_height,
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"预览更新错误: {str(e)}")
            import traceback
            traceback.print_exc()
            self.preview_label.setText(f"预览错误: {str(e)}")

    def add_watermark_to_image(self, image):
        result = image.copy()

        # 根据当前设置类型选择参数
        if self.current_settings_type == "shared":
            # 使用共享设置
            watermark_type = self.watermark_type.currentText()
        else:
            # 使用个性化设置
            watermark_type = self.per_image_watermark_type.currentText()

        if watermark_type == "文本水印":
            result = self.add_text_watermark(result)
        else:
            result = self.add_image_watermark(result)

        return result

    def get_current_text(self):
        """获取当前文本"""
        if self.current_settings_type == "shared":
            return self.text_input.text()
        else:
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                per_image_text = self.per_image_settings[image_path].get("text", "")
                # 如果个性化文本为空，则使用共享文本
                return per_image_text if per_image_text else self.text_input.text()
            return self.text_input.text()

    def get_current_per_image_text(self):
        """获取个性化文本"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            return self.per_image_settings[image_path].get("text", "")
        return ""

    def get_current_per_image_path(self):
        """获取个性化图片路径"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            return self.per_image_settings[image_path].get("image_path", "")
        return ""

    def get_current_font_size(self):
        """获取当前字体大小"""
        if self.current_settings_type == "shared":
            return self.font_size.value()
        else:
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                return self.per_image_settings[image_path].get("font_size", self.font_size.value())
            return self.font_size.value()

    def get_current_offset(self):
        """获取当前偏移量"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            return (
                self.per_image_settings[image_path].get("offset_x", 0),
                self.per_image_settings[image_path].get("offset_y", 0)
            )
        return (0, 0)

    def add_text_watermark(self, image):
        if image.mode != 'RGB':
            image = image.convert('RGB')

        text = self.get_current_text()
        if not text:
            return image

        # 获取字体设置
        if self.current_settings_type == "shared":
            font_family = self.font_combo.currentText()
            font_size = self.font_size.value()
            bold = self.bold_check.isChecked()
            italic = self.italic_check.isChecked()

            # 修复颜色获取逻辑
            color_style = self.color_btn.styleSheet()
            if "background-color:" in color_style:
                color = color_style.split("background-color:")[1].split(";")[0].strip()
            else:
                color = "#FFFFFF"

            opacity = self.opacity_slider.value()
            shadow = self.shadow_check.isChecked()

            shadow_style = self.shadow_color_btn.styleSheet()
            if "background-color:" in shadow_style:
                shadow_color = shadow_style.split("background-color:")[1].split(";")[0].strip()
            else:
                shadow_color = "#000000"

            shadow_offset = self.shadow_offset.value()
            outline = self.outline_check.isChecked()

            outline_style = self.outline_color_btn.styleSheet()
            if "background-color:" in outline_style:
                outline_color = outline_style.split("background-color:")[1].split(";")[0].strip()
            else:
                outline_color = "#000000"

            outline_width = self.outline_width.value()
            rotation = self.rotation_slider.value()
        else:
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                settings = self.per_image_settings[image_path]
                font_family = settings.get("font_family", self.font_combo.currentText())
                font_size = settings.get("font_size", self.font_size.value())
                bold = settings.get("bold", False)
                italic = settings.get("italic", False)
                opacity = settings.get("opacity", 80)
                shadow = settings.get("shadow", False)
                shadow_offset = settings.get("shadow_offset", 2)
                outline = settings.get("outline", False)
                outline_width = settings.get("outline_width", 1)
                rotation = settings.get("rotation", 0)

                # 颜色需要特殊处理
                color = settings.get("color", "#FFFFFF")
                shadow_color = settings.get("shadow_color", "#000000")
                outline_color = settings.get("outline_color", "#000000")
            else:
                return image

        # 创建字体
        try:
            font_path = self.get_font_path(font_family)
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                try:
                    for fallback_font in ["simhei.ttf", "msyh.ttc", "simsun.ttc"]:
                        try:
                            font = ImageFont.truetype(fallback_font, font_size)
                            break
                        except:
                            continue
                    else:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # 计算文本尺寸
        temp_image = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)

        try:
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 如果textbbox不可用，使用旧方法
            try:
                text_width, text_height = temp_draw.textsize(text, font=font)
            except:
                # 如果都失败，使用估计值
                text_width = len(text) * font_size // 2
                text_height = font_size

        # 如果计算出的尺寸为0，使用默认值
        if text_width == 0 or text_height == 0:
            text_width = 100
            text_height = 50

        # 计算水印位置
        position = self.position_combo.currentText()
        img_width, img_height = image.size

        # 获取偏移量 - 修复水平偏移问题
        offset_x, offset_y = self.get_current_offset()

        if position == "自定义拖拽" and self.draggable_watermark:
            x = offset_x
            y = offset_y

            if self.preview_label.pixmap():
                preview_pixmap = self.preview_label.pixmap()
                pixmap_width = preview_pixmap.width()
                pixmap_height = preview_pixmap.height()

                if pixmap_width > 0 and pixmap_height > 0:
                    scale_x = img_width / pixmap_width
                    scale_y = img_height / pixmap_height
                    x = int(x * scale_x)
                    y = int(y * scale_y)
        else:
            if position == "左上角":
                x, y = 10, 10
            elif position == "中上":
                x, y = (img_width - text_width) // 2, 10
            elif position == "右上角":
                x, y = img_width - text_width - 10, 10
            elif position == "左中":
                x, y = 10, (img_height - text_height) // 2
            elif position == "居中":
                x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
            elif position == "右中":
                x, y = img_width - text_width - 10, (img_height - text_height) // 2
            elif position == "左下角":
                x, y = 10, img_height - text_height - 10
            elif position == "中下":
                x, y = (img_width - text_width) // 2, img_height - text_height - 10
            elif position == "右下角":
                x, y = img_width - text_width - 10, img_height - text_height - 10
            else:
                x, y = img_width - text_width - 10, img_height - text_height - 10

            # 应用偏移量 - 修复水平偏移
            x += offset_x
            y += offset_y

        # 确保位置在图片范围内
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))

        # 获取颜色
        try:
            # 直接使用PIL的ImageColor模块，不需要额外导入
            rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) if color.startswith('#') else (255, 255, 255)
            shadow_rgb = tuple(int(shadow_color[i:i + 2], 16) for i in (1, 3, 5)) if shadow_color.startswith('#') else (
                0, 0, 0)
            outline_rgb = tuple(int(outline_color[i:i + 2], 16) for i in (1, 3, 5)) if outline_color.startswith(
                '#') else (0, 0, 0)
        except:
            # 如果颜色解析失败，使用默认值
            rgb = (255, 255, 255)
            shadow_rgb = (0, 0, 0)
            outline_rgb = (0, 0, 0)

        # 修复旋转问题：统一使用图层方法处理所有效果
        try:
            # 创建足够大的文本图层（考虑旋转后的尺寸）
            rotation_margin = int(max(text_width, text_height) * 0.5)
            text_layer_width = text_width + 2 * rotation_margin
            text_layer_height = text_height + 2 * rotation_margin

            text_layer = Image.new('RGBA', (text_layer_width, text_layer_height), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_layer)

            # 在文本图层中心绘制文本
            text_x = rotation_margin
            text_y = rotation_margin

            # 处理粗体和斜体效果
            if bold or italic:
                # 创建临时图层来处理文本样式
                temp_text_layer = Image.new('RGBA', (text_layer_width, text_layer_height), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_text_layer)

                # 绘制描边效果
                if outline and outline_width > 0:
                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            if dx != 0 or dy != 0:
                                temp_draw.text((text_x + dx, text_y + dy), text, font=font,
                                               fill=outline_rgb + (int(255 * opacity / 100),))

                # 绘制主文本 - 处理粗体和斜体
                if bold:
                    # 模拟粗体：轻微偏移绘制多次
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            temp_draw.text((text_x + dx, text_y + dy), text, font=font,
                                           fill=rgb + (int(255 * opacity / 100),))

                # 绘制主文本
                temp_draw.text((text_x, text_y), text, font=font, fill=rgb + (int(255 * opacity / 100),))

                # 处理斜体效果
                if italic:
                    # 应用斜体变换
                    shear_factor = 0.2
                    temp_text_layer = temp_text_layer.transform(
                        temp_text_layer.size, Image.AFFINE,
                        (1, shear_factor, 0, 0, 1, 0),
                        resample=Image.BICUBIC, fill=(0, 0, 0, 0)
                    )

                # 合并到主文本图层
                text_layer = Image.alpha_composite(text_layer, temp_text_layer)
            else:
                # 没有粗体斜体时的正常绘制
                # 绘制描边效果
                if outline and outline_width > 0:
                    for dx in range(-outline_width, outline_width + 1):
                        for dy in range(-outline_width, outline_width + 1):
                            if dx != 0 or dy != 0:
                                text_draw.text((text_x + dx, text_y + dy), text, font=font,
                                               fill=outline_rgb + (int(255 * opacity / 100),))

                # 绘制主文本
                text_draw.text((text_x, text_y), text, font=font, fill=rgb + (int(255 * opacity / 100),))

            # 绘制阴影效果
            if shadow:
                shadow_layer = Image.new('RGBA', (text_layer_width, text_layer_height), (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow_layer)
                shadow_draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font,
                                 fill=shadow_rgb + (int(255 * opacity / 100),))

                # 应用模糊效果
                if hasattr(ImageFilter, 'GaussianBlur'):
                    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=1))

                # 合并阴影图层（放在文本下面）
                text_layer = Image.alpha_composite(shadow_layer, text_layer)

            # 应用旋转
            if rotation != 0:
                rotated_text = text_layer.rotate(rotation, resample=Image.BICUBIC, expand=True)

                # 计算旋转后文本的位置（保持中心点不变）
                rot_width, rot_height = rotated_text.size
                new_x = x + text_width // 2 - rot_width // 2
                new_y = y + text_height // 2 - rot_height // 2
            else:
                rotated_text = text_layer
                new_x = x - rotation_margin
                new_y = y - rotation_margin

            # 将文本粘贴到原图
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            image.paste(rotated_text, (new_x, new_y), rotated_text)
            result = image.convert('RGB')

        except Exception as e:
            print(f"水印绘制错误: {str(e)}")
            # 如果复杂效果失败，使用简单绘制
            draw = ImageDraw.Draw(image)
            draw.text((x, y), text, font=font, fill=rgb)
            result = image

        return result

    def add_image_watermark(self, image):
        if self.current_settings_type == "shared":
            watermark_path = self.shared_settings["image_path"]
            scale = self.image_scale.value() / 100.0
            opacity = self.image_opacity_slider.value()  # 使用图片水印专用的透明度设置
            rotation = self.rotation_slider.value()
        else:
            if self.current_image_index >= 0:
                image_path = self.images[self.current_image_index]
                settings = self.per_image_settings[image_path]
                watermark_path = settings.get("image_path", "")
                scale = settings.get("image_scale", 100) / 100.0
                opacity = self.per_image_image_opacity_slider.value()  # 使用个性化设置的图片水印透明度
                rotation = settings.get("rotation", 0)
            else:
                return image

        if not watermark_path or not os.path.exists(watermark_path):
            return image

        try:
            watermark = Image.open(watermark_path)

            # 确保水印图片是RGBA模式以支持透明度
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')

            new_width = int(watermark.width * scale)
            new_height = int(watermark.height * scale)
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 应用透明度设置
            if opacity < 100:
                # 创建一个新的alpha通道，应用透明度
                alpha = watermark.split()[3]
                # 将透明度转换为0-255范围的值
                opacity_value = int(255 * opacity / 100)
                # 调整alpha通道
                alpha = alpha.point(lambda p: int(p * opacity / 100))
                watermark.putalpha(alpha)

            position = self.position_combo.currentText()
            img_width, img_height = image.size
            wm_width, wm_height = watermark.size

            if position == "自定义拖拽" and self.draggable_watermark:
                offset_x, offset_y = self.get_current_offset()
                x = offset_x
                y = offset_y

                if self.preview_label.pixmap():
                    preview_pixmap = self.preview_label.pixmap()
                    pixmap_width = preview_pixmap.width()
                    pixmap_height = preview_pixmap.height()

                    if pixmap_width > 0 and pixmap_height > 0:
                        scale_x = img_width / pixmap_width
                        scale_y = img_height / pixmap_height
                        x = int(x * scale_x)
                        y = int(y * scale_y)
            else:
                if position == "左上角":
                    x, y = 10, 10
                elif position == "中上":
                    x, y = (img_width - wm_width) // 2, 10
                elif position == "右上角":
                    x, y = img_width - wm_width - 10, 10
                elif position == "左中":
                    x, y = 10, (img_height - wm_height) // 2
                elif position == "居中":
                    x, y = (img_width - wm_width) // 2, (img_height - wm_height) // 2
                elif position == "右中":
                    x, y = img_width - wm_width - 10, (img_height - wm_height) // 2
                elif position == "左下角":
                    x, y = 10, img_height - wm_height - 10
                elif position == "中下":
                    x, y = (img_width - wm_width) // 2, img_height - wm_height - 10
                elif position == "右下角":
                    x, y = img_width - wm_width - 10, img_height - wm_height - 10
                else:
                    x, y = img_width - wm_width - 10, img_height - wm_height - 10

                offset_x, offset_y = self.get_current_offset()
                x += offset_x
                y += offset_y

            if rotation != 0:
                # 计算旋转中心
                center_x = x + wm_width // 2
                center_y = y + wm_height // 2

                # 创建新的透明图层来包含旋转后的水印
                rotated_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))

                # 旋转水印
                rotated_watermark = watermark.rotate(
                    rotation,
                    resample=Image.BICUBIC,
                    expand=True
                )

                # 计算旋转后的位置
                rotated_width, rotated_height = rotated_watermark.size
                new_x = center_x - rotated_width // 2
                new_y = center_y - rotated_height // 2

                # 将旋转后的水印粘贴到新图层
                rotated_layer.paste(rotated_watermark, (new_x, new_y), rotated_watermark)
                watermark = rotated_layer

                # 合并图层
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                result = Image.alpha_composite(image, watermark).convert('RGB')
                return result
            else:
                # 如果没有旋转，直接使用原水印
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                image.paste(watermark, (x, y), watermark)
                return image.convert("RGB")

        except Exception as e:
            print(f"图片水印错误: {str(e)}")
            return image

    def get_font_path(self, font_family):
        if sys.platform == "win32":
            font_paths = [
                os.path.join(os.environ['WINDIR'], 'Fonts'),
                os.path.join(os.environ['SYSTEMROOT'], 'Fonts')
            ]
        elif sys.platform == "darwin":
            font_paths = [
                '/Library/Fonts',
                '/System/Library/Fonts',
                os.path.expanduser('~/Library/Fonts')
            ]
        else:
            font_paths = [
                '/usr/share/fonts',
                '/usr/local/share/fonts',
                os.path.expanduser('~/.fonts')
            ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                for file in os.listdir(font_path):
                    if file.lower().endswith(('.ttf', '.otf', '.ttc')) and font_family.lower() in file.lower():
                        return os.path.join(font_path, file)

        return None

    def apply_shared_settings_to_ui(self):
        """应用共享设置到UI"""
        self.watermark_type.setCurrentText("文本水印" if self.shared_settings["type"] == "text" else "图片水印")
        self.text_input.setText(self.shared_settings["text"])
        self.font_combo.setCurrentText(self.shared_settings["font_family"])
        self.font_size.setValue(self.shared_settings["font_size"])
        self.bold_check.setChecked(self.shared_settings["bold"])
        self.italic_check.setChecked(self.shared_settings["italic"])

        color = self.shared_settings["color"]
        self.color_btn.setStyleSheet(f"background-color: {color}; border-radius: 4px; min-height: 20px;")

        self.opacity_slider.setValue(self.shared_settings["opacity"])
        self.position_combo.setCurrentText(self.shared_settings["position"])
        self.rotation_slider.setValue(self.shared_settings["rotation"])
        self.shadow_check.setChecked(self.shared_settings["shadow"])

        shadow_color = self.shared_settings["shadow_color"]
        self.shadow_color_btn.setStyleSheet(f"background-color: {shadow_color}; border-radius: 4px; min-height: 20px;")

        self.shadow_offset.setValue(self.shared_settings["shadow_offset"])
        self.shadow_blur.setValue(self.shared_settings["shadow_blur"])
        self.outline_check.setChecked(self.shared_settings["outline"])

        outline_color = self.shared_settings["outline_color"]
        self.outline_color_btn.setStyleSheet(
            f"background-color: {outline_color}; border-radius: 4px; min-height: 20px;")

        self.outline_width.setValue(self.shared_settings["outline_width"])
        self.image_path_label.setText(
            os.path.basename(self.shared_settings["image_path"]) if self.shared_settings["image_path"] else "未选择")
        self.image_scale.setValue(self.shared_settings["image_scale"])
        self.image_opacity_slider.setValue(self.shared_settings["opacity"])

        # 导出设置
        self.format_combo.setCurrentText(self.shared_settings["output_format"])
        self.quality_slider.setValue(self.shared_settings["quality"])
        self.prefix_input.setText(self.shared_settings["naming_prefix"])
        self.suffix_input.setText(self.shared_settings["naming_suffix"])
        self.resize_check.setChecked(self.shared_settings["resize_enabled"])
        self.resize_percent.setValue(self.shared_settings["resize_percent"])
        self.resize_width.setValue(self.shared_settings["resize_width"])
        self.resize_height.setValue(self.shared_settings["resize_height"])

    def apply_per_image_settings_to_ui(self):
        """应用个性化设置到UI"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            settings = self.per_image_settings[image_path]

            # 设置水印类型
            self.per_image_watermark_type.setCurrentText("文本水印" if settings.get("type", "text") == "text" else "图片水印")

            # 文本设置
            self.per_image_text_input.setText(settings.get("text", ""))
            self.per_image_font_combo.setCurrentText(settings.get("font_family", "Microsoft YaHei"))
            self.per_image_font_size.setValue(settings.get("font_size", 40))
            self.per_image_bold_check.setChecked(settings.get("bold", False))
            self.per_image_italic_check.setChecked(settings.get("italic", False))

            color = settings.get("color", "#FFFFFF")
            self.per_image_color_btn.setStyleSheet(f"background-color: {color}; border-radius: 4px; min-height: 20px;")

            self.per_image_opacity_slider.setValue(settings.get("opacity", 80))
            self.per_image_rotation_slider.setValue(settings.get("rotation", 0))
            self.per_image_shadow_check.setChecked(settings.get("shadow", False))

            shadow_color = settings.get("shadow_color", "#000000")
            self.per_image_shadow_color_btn.setStyleSheet(
                f"background-color: {shadow_color}; border-radius: 4px; min-height: 20px;")

            self.per_image_shadow_offset.setValue(settings.get("shadow_offset", 2))
            self.per_image_shadow_blur.setValue(settings.get("shadow_blur", 2))
            self.per_image_outline_check.setChecked(settings.get("outline", False))

            outline_color = settings.get("outline_color", "#000000")
            self.per_image_outline_color_btn.setStyleSheet(
                f"background-color: {outline_color}; border-radius: 4px; min-height: 20px;")

            self.per_image_outline_width.setValue(settings.get("outline_width", 1))

            # 图片水印设置
            self.per_image_image_path_label.setText(
                os.path.basename(settings.get("image_path", "")) if settings.get("image_path") else "未选择")
            self.per_image_image_scale.setValue(settings.get("image_scale", 100))
            self.per_image_image_opacity_slider.setValue(settings.get("opacity", 80))

            # 位置偏移
            self.per_image_offset_x.setValue(settings.get("offset_x", 0))
            self.per_image_offset_y.setValue(settings.get("offset_y", 0))

    def save_shared_settings_from_ui(self):
        """从UI保存共享设置"""
        # 修复颜色获取逻辑
        color_style = self.color_btn.styleSheet()
        if "background-color:" in color_style:
            color = color_style.split("background-color:")[1].split(";")[0].strip()
        else:
            color = "#FFFFFF"

        shadow_style = self.shadow_color_btn.styleSheet()
        if "background-color:" in shadow_style:
            shadow_color = shadow_style.split("background-color:")[1].split(";")[0].strip()
        else:
            shadow_color = "#000000"

        outline_style = self.outline_color_btn.styleSheet()
        if "background-color:" in outline_style:
            outline_color = outline_style.split("background-color:")[1].split(";")[0].strip()
        else:
            outline_color = "#000000"

        self.shared_settings.update({
            "type": "text" if self.watermark_type.currentText() == "文本水印" else "image",
            "text": self.text_input.text(),
            "font_family": self.font_combo.currentText(),
            "font_size": self.font_size.value(),
            "bold": self.bold_check.isChecked(),
            "italic": self.italic_check.isChecked(),
            "color": color,
            "opacity": self.opacity_slider.value(),
            "position": self.position_combo.currentText(),
            "rotation": self.rotation_slider.value(),
            "shadow": self.shadow_check.isChecked(),
            "shadow_color": shadow_color,
            "shadow_offset": self.shadow_offset.value(),
            "shadow_blur": self.shadow_blur.value(),
            "outline": self.outline_check.isChecked(),
            "outline_color": outline_color,
            "outline_width": self.outline_width.value(),
            "image_path": self.shared_settings["image_path"],  # 保持不变
            "image_scale": self.image_scale.value(),
            "output_format": self.format_combo.currentText(),
            "quality": self.quality_slider.value(),
            "resize_enabled": self.resize_check.isChecked(),
            "resize_percent": self.resize_percent.value(),
            "resize_width": self.resize_width.value(),
            "resize_height": self.resize_height.value(),
            "naming_prefix": self.prefix_input.text(),
            "naming_suffix": self.suffix_input.text()
        })

    def save_per_image_settings_from_ui(self):
        """从UI保存个性化设置"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]

            # 修复颜色获取逻辑
            color_style = self.per_image_color_btn.styleSheet()
            if "background-color:" in color_style:
                color = color_style.split("background-color:")[1].split(";")[0].strip()
            else:
                color = "#FFFFFF"

            shadow_style = self.per_image_shadow_color_btn.styleSheet()
            if "background-color:" in shadow_style:
                shadow_color = shadow_style.split("background-color:")[1].split(";")[0].strip()
            else:
                shadow_color = "#000000"

            outline_style = self.per_image_outline_color_btn.styleSheet()
            if "background-color:" in outline_style:
                outline_color = outline_style.split("background-color:")[1].split(";")[0].strip()
            else:
                outline_color = "#000000"

            self.per_image_settings[image_path].update({
                "type": "text" if self.per_image_watermark_type.currentText() == "文本水印" else "image",
                "text": self.per_image_text_input.text(),
                "font_family": self.per_image_font_combo.currentText(),
                "font_size": self.per_image_font_size.value(),
                "bold": self.per_image_bold_check.isChecked(),
                "italic": self.per_image_italic_check.isChecked(),
                "color": color,
                "opacity": self.per_image_opacity_slider.value(),
                "rotation": self.per_image_rotation_slider.value(),
                "shadow": self.per_image_shadow_check.isChecked(),
                "shadow_color": shadow_color,
                "shadow_offset": self.per_image_shadow_offset.value(),
                "shadow_blur": self.per_image_shadow_blur.value(),
                "outline": self.per_image_outline_check.isChecked(),
                "outline_color": outline_color,
                "outline_width": self.per_image_outline_width.value(),
                "image_path": self.per_image_settings[image_path].get("image_path", ""),
                "image_scale": self.per_image_image_scale.value(),
                "offset_x": self.per_image_offset_x.value(),
                "offset_y": self.per_image_offset_y.value()
            })

    def use_exif_date(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, "提示", "请先选择一张图片")
            return

        image_path = self.images[self.current_image_index]
        date = self.get_exif_date(image_path)
        if date:
            self.text_input.setText(date)
            self.on_shared_parameter_changed()

    def use_exif_date_per_image(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, "提示", "请先选择一张图片")
            return

        image_path = self.images[self.current_image_index]
        date = self.get_exif_date(image_path)
        if date:
            self.per_image_text_input.setText(date)
            self.on_per_image_parameter_changed()

    def get_exif_date(self, image_path):
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()

            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal' and value:
                        date_part = value.split()[0]
                        return date_part.replace(":", "-")

        except:
            pass

        try:
            mod_time = os.path.getmtime(image_path)
            from datetime import datetime
            return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d")
        except:
            return "Unknown-Date"

    def export_all_images(self):
        if not self.images:
            QMessageBox.warning(self, "警告", "没有图片可导出")
            return

        output_path = self.output_path_label.text()
        if output_path == "未选择":
            QMessageBox.warning(self, "警告", "请先选择输出文件夹")
            return

        for image_path in self.images:
            if os.path.dirname(image_path) == output_path:
                reply = QMessageBox.question(self, "确认",
                                             "输出文件夹与原文件夹相同，这可能会覆盖原文件。是否继续？",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                break

        self.progress_dialog = QProgressDialog("正在导出图片...", "取消", 0, len(self.images), self)
        self.progress_dialog.setWindowTitle("导出进度")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        self.export_thread = WatermarkThread(self, output_path)
        self.export_thread.progress.connect(self.progress_dialog.setValue)
        self.export_thread.finished.connect(self.export_finished)
        self.export_thread.error.connect(self.export_error)
        self.progress_dialog.canceled.connect(self.export_thread.cancel)
        self.export_thread.start()

    def export_finished(self):
        self.progress_dialog.close()
        QMessageBox.information(self, "完成", f"已成功导出 {len(self.images)} 张图片")

    def export_error(self, error_msg):
        QMessageBox.warning(self, "导出错误", error_msg)

    def export_single_image(self, image_path, output_path):
        try:
            original_image = self.load_and_fix_image(image_path)
            if original_image is None:
                raise Exception("无法加载图片")

            if self.resize_check.isChecked():
                if self.resize_percent_radio.isChecked():
                    percent = self.resize_percent.value()
                    new_width = int(original_image.size[0] * percent / 100)
                    new_height = int(original_image.size[1] * percent / 100)
                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    width = self.resize_width.value()
                    height = self.resize_height.value()

                    if self.keep_aspect_check.isChecked():
                        original_ratio = original_image.size[0] / original_image.size[1]
                        if width / height > original_ratio:
                            new_width = int(height * original_ratio)
                            new_height = height
                        else:
                            new_width = width
                            new_height = int(width / original_ratio)
                    else:
                        new_width = width
                        new_height = height

                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 关键修改：在导出时根据图片是否有个性化设置来决定使用哪种设置
            # 保存当前设置类型
            current_settings_backup = self.current_settings_type

            # 检查该图片是否有个性化设置
            if image_path in self.per_image_settings and self.has_per_image_settings(image_path):
                # 使用个性化设置
                self.current_settings_type = "per_image"
                # 设置当前图片索引以便正确获取个性化设置
                self.current_image_index = self.images.index(image_path)
            else:
                # 使用共享设置
                self.current_settings_type = "shared"

            # 添加水印
            watermarked_image = self.add_watermark_to_image(original_image)

            # 恢复原来的设置类型
            self.current_settings_type = current_settings_backup

            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)

            prefix = self.prefix_input.text()
            suffix = self.suffix_input.text()

            output_filename = f"{prefix}{name}{suffix}{ext}"
            output_filepath = os.path.join(output_path, output_filename)

            os.makedirs(output_path, exist_ok=True)

            format = self.format_combo.currentText()
            if format == "JPEG":
                quality = self.quality_slider.value()
                watermarked_image.save(output_filepath, format, quality=quality, optimize=True)
            else:
                watermarked_image.save(output_filepath, format, optimize=True)
        except Exception as e:
            raise Exception(f"处理图片 {os.path.basename(image_path)} 时出错: {str(e)}")

    def has_per_image_settings(self, image_path):
        """检查图片是否有有效的个性化设置"""
        if image_path not in self.per_image_settings:
            return False

        settings = self.per_image_settings[image_path]

        # 检查是否有任何个性化设置与默认值不同
        for key, value in settings.items():
            if key in self.default_per_image_settings:
                default_value = self.default_per_image_settings[key]
                if value != default_value:
                    return True

        # 特别检查文本内容是否设置
        if settings.get("text", ""):
            return True

        return False

    def save_template(self):
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if ok and name:
            self.save_shared_settings_from_ui()

            template = {
                "shared_settings": self.shared_settings.copy()
            }

            templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
            os.makedirs(templates_dir, exist_ok=True)

            template_path = os.path.join(templates_dir, f"{name}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)

            self.load_template_list()
            QMessageBox.information(self, "成功", "模板已保存")

    def load_template(self):
        if self.template_list.currentItem():
            template_name = self.template_list.currentItem().text()
            self.load_template_by_name(template_name)
        else:
            QMessageBox.warning(self, "警告", "请先选择一个模板")

    def load_template_from_list(self, item):
        template_name = item.text()
        self.load_template_by_name(template_name)

    def load_template_by_name(self, name):
        templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
        template_path = os.path.join(templates_dir, f"{name}.json")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)

            if "shared_settings" in template:
                self.shared_settings.update(template["shared_settings"])
                self.apply_shared_settings_to_ui()

            self.update_preview()
            QMessageBox.information(self, "成功", f"已加载模板: {name}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法加载模板: {str(e)}")

    def delete_template(self):
        if self.template_list.currentItem():
            template_name = self.template_list.currentItem().text()

            reply = QMessageBox.question(self, "确认", f"确定要删除模板 '{template_name}' 吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
                template_path = os.path.join(templates_dir, f"{template_name}.json")

                try:
                    os.remove(template_path)
                    self.load_template_list()
                    QMessageBox.information(self, "成功", "模板已删除")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"无法删除模板: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个模板")

    def load_template_list(self):
        self.template_list.clear()

        templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
        if os.path.exists(templates_dir):
            for file in os.listdir(templates_dir):
                if file.endswith(".json"):
                    template_name = file[:-5]
                    self.template_list.addItem(template_name)

    def reset_rotation(self):
        self.rotation_slider.setValue(0)

    def reset_per_image_rotation(self):
        self.per_image_rotation_slider.setValue(0)

    def load_settings(self):
        settings_path = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                self.auto_load_check.setChecked(settings.get("auto_load_last", False))
                if settings.get("auto_load_last", False):
                    last_template = settings.get("last_template")
                    if last_template and os.path.exists(
                            os.path.join(os.path.expanduser("~"), ".watermark_templates", f"{last_template}.json")):
                        self.load_template_by_name(last_template)

            except:
                pass

    def save_settings(self):
        last_template = None
        if self.template_list.currentItem():
            last_template = self.template_list.currentItem().text()

        settings = {
            "auto_load_last": self.auto_load_check.isChecked(),
            "last_template": last_template
        }

        settings_path = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]

        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        image_paths = [path for path in paths if any(path.lower().endswith(ext) for ext in extensions)]

        if image_paths:
            self.add_images(image_paths)
        else:
            QMessageBox.warning(self, "警告", "拖放的文件中没有支持的图片格式")

        event.acceptProposedAction()


# 运行应用
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        window = WatermarkApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"程序运行错误: {str(e)}")
        import traceback

        traceback.print_exc()