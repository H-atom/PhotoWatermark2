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

# 应用样式表
APP_STYLESHEET = """
/* 主窗口样式 */
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #f5f7fa, stop: 1 #c3cfe2);
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

/* 卡片化效果 */
QGroupBox {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #2c3e50;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #6a11cb, stop: 1 #2575fc);
    color: white;
    border-radius: 6px;
}

/* 玻璃化效果 */
QFrame#preview_frame {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* 按钮样式 */
QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #6a11cb, stop: 1 #2575fc);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 8px 16px;
    font-weight: bold;
    margin: 2px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #2575fc, stop: 1 #6a11cb);
}

QPushButton:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #1a5fb4, stop: 1 #4a00e0);
}

/* 列表样式 */
QListWidget {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

QListWidget::item:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #6a11cb, stop: 1 #2575fc);
    color: white;
    border-radius: 4px;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.7);
}

QTabBar::tab {
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.9);
    border-color: rgba(255, 255, 255, 0.5);
}

/* 输入框样式 */
QLineEdit, QSpinBox, QComboBox {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #6a11cb;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #2c3e50;
    width: 0;
    height: 0;
}

/* 滑动条样式 */
QSlider::groove:horizontal {
    border: 1px solid rgba(255, 255, 255, 0.3);
    height: 6px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #6a11cb, stop:1 #2575fc);
    border: 1px solid rgba(255, 255, 255, 0.5);
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

/* 复选框样式 */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.7);
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #6a11cb, stop:1 #2575fc);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

QCheckBox::indicator:checked::image {
    width: 14px;
    height: 14px;
    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
}

/* 单选按钮样式 */
QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 9px;
    background: rgba(255, 255, 255, 0.7);
}

QRadioButton::indicator:checked {
    border: 5px solid #6a11cb;
    background: white;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    text-align: center;
    background: rgba(255, 255, 255, 0.5);
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #6a11cb, stop:1 #2575fc);
    border-radius: 3px;
}

/* 滚动区域样式 */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    border: none;
    background: rgba(255, 255, 255, 0.3);
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: rgba(106, 17, 203, 0.7);
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(106, 17, 203, 0.9);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

/* 标签样式 */
QLabel {
    color: #2c3e50;
}

QLabel#title_label {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
    padding: 10px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 8px;
    margin: 5px;
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
            "background-color: rgba(255, 255, 255, 0.7); border: 2px dashed #6a11cb; border-radius: 8px;")
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
        self.init_ui()
        self.load_settings()

        # 延迟更新预览的计时器
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview_delayed)

    def init_ui(self):
        self.setWindowTitle("高级图片水印工具 - 专业版")
        self.setGeometry(100, 100, 1400, 900)

        # 应用样式表
        self.setStyleSheet(APP_STYLESHEET)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 左侧图片列表区域
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧设置和预览区域
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)

        # 初始化状态
        self.current_image_index = -1
        self.images = []

        # 共享设置（所有图片共用）
        self.shared_settings = {
            "type": "text",
            "font_family": "Microsoft YaHei",  # 默认使用支持中文的字体
            "font_size": 200,
            "bold": False,
            "italic": False,
            "color": "#FFFFFF",
            "opacity": 80,
            "position": "bottom-right",
            "rotation": 0,
            "shadow": False,
            "shadow_color": "#000000",
            "shadow_offset": 2,
            "shadow_blur": 0,
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

        # 个性化设置（每张图片单独保存）
        self.per_image_settings = {}

        # 水印位置拖拽相关
        self.draggable_watermark = None
        self.custom_position_mode = False

        # 图片缓存
        self.image_cache = {}

    def create_left_panel(self):
        # 左侧面板 - 图片列表
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)
        layout.setSpacing(10)
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

        self.clear_btn = QPushButton("🗑️ 清空列表")
        self.clear_btn.clicked.connect(self.clear_images)
        import_layout.addWidget(self.clear_btn)

        layout.addLayout(import_layout)

        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.currentRowChanged.connect(self.on_image_selected)
        layout.addWidget(self.image_list)

        # 设置拖拽支持
        self.setAcceptDrops(True)
        self.image_list.setAcceptDrops(True)

        return left_widget

    def create_right_panel(self):
        # 右侧面板 - 设置和预览
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建标签页
        self.tabs = QTabWidget()

        # 参数设置标签页
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ 参数设置")

        # 导出设置标签页
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "📤 导出设置")

        # 模板管理标签页
        self.template_tab = self.create_template_tab()
        self.tabs.addTab(self.template_tab, "💾 模板管理")

        layout.addWidget(self.tabs)

        # 预览区域
        preview_group = QGroupBox("👁️ 预览")
        preview_layout = QVBoxLayout(preview_group)

        # 预览控制
        preview_control_layout = QHBoxLayout()

        # 参数类型选择
        preview_control_layout.addWidget(QLabel("参数类型:"))
        self.settings_type_combo = QComboBox()
        self.settings_type_combo.addItems(["共享设置", "个性化设置"])
        self.settings_type_combo.currentTextChanged.connect(self.on_settings_type_changed)
        preview_control_layout.addWidget(self.settings_type_combo)

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
        preview_layout.addLayout(preview_control_layout)

        # 预览图像区域
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("preview_frame")
        preview_frame_layout = QVBoxLayout(self.preview_frame)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
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
        self.export_btn.setStyleSheet("font-size: 14px; padding: 12px 24px;")
        export_btn_layout.addWidget(self.export_btn)

        export_btn_layout.addStretch()
        layout.addLayout(export_btn_layout)

        return right_widget

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # 创建堆叠窗口，用于切换共享/个性化设置
        self.settings_stack = QStackedWidget()

        # 共享设置页面
        self.shared_settings_widget = self.create_shared_settings_widget()
        self.settings_stack.addWidget(self.shared_settings_widget)

        # 个性化设置页面
        self.per_image_settings_widget = self.create_per_image_settings_widget()
        self.settings_stack.addWidget(self.per_image_settings_widget)

        layout.addWidget(self.settings_stack)

        return tab

    def create_shared_settings_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

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
        self.text_input.textChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.text_input, 0, 1)

        # 从EXIF获取日期按钮
        self.exif_date_btn = QPushButton("使用EXIF日期")
        self.exif_date_btn.clicked.connect(self.use_exif_date)
        text_layout.addWidget(self.exif_date_btn, 0, 2)

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

        self.font_combo.addItems(chinese_fonts[:20] + other_fonts[:30])  # 限制显示数量
        self.font_combo.setCurrentText("Microsoft YaHei")  # 默认使用微软雅黑
        self.font_combo.currentTextChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.font_combo, 1, 1)

        # 字体大小
        text_layout.addWidget(QLabel("字体大小:"), 1, 2)
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 500)
        self.font_size.setValue(200)
        self.font_size.valueChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.font_size, 1, 3)

        # 粗体和斜体
        self.bold_check = QCheckBox("粗体")
        self.bold_check.stateChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.bold_check, 2, 0)

        self.italic_check = QCheckBox("斜体")
        self.italic_check.stateChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.italic_check, 2, 1)

        # 颜色选择
        text_layout.addWidget(QLabel("颜色:"), 3, 0)
        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet("background-color: #FFFFFF; border-radius: 4px;")
        self.color_btn.clicked.connect(self.choose_color)
        text_layout.addWidget(self.color_btn, 3, 1)

        # 透明度
        text_layout.addWidget(QLabel("透明度:"), 3, 2)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.opacity_slider, 3, 3)

        # 阴影效果
        self.shadow_check = QCheckBox("阴影效果")
        self.shadow_check.stateChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.shadow_check, 4, 0)

        text_layout.addWidget(QLabel("阴影颜色:"), 4, 1)
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setStyleSheet("background-color: #000000; border-radius: 4px;")
        self.shadow_color_btn.clicked.connect(self.choose_shadow_color)
        text_layout.addWidget(self.shadow_color_btn, 4, 2)

        text_layout.addWidget(QLabel("阴影偏移:"), 4, 3)
        self.shadow_offset = QSpinBox()
        self.shadow_offset.setRange(1, 10)
        self.shadow_offset.setValue(2)
        self.shadow_offset.valueChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.shadow_offset, 4, 4)

        # 阴影模糊
        text_layout.addWidget(QLabel("阴影模糊:"), 5, 0)
        self.shadow_blur = QSpinBox()
        self.shadow_blur.setRange(0, 10)
        self.shadow_blur.setValue(0)
        self.shadow_blur.valueChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.shadow_blur, 5, 1)

        # 描边效果
        self.outline_check = QCheckBox("描边效果")
        self.outline_check.stateChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.outline_check, 6, 0)

        text_layout.addWidget(QLabel("描边颜色:"), 6, 1)
        self.outline_color_btn = QPushButton()
        self.outline_color_btn.setStyleSheet("background-color: #000000; border-radius: 4px;")
        self.outline_color_btn.clicked.connect(self.choose_outline_color)
        text_layout.addWidget(self.outline_color_btn, 6, 2)

        text_layout.addWidget(QLabel("描边宽度:"), 6, 3)
        self.outline_width = QSpinBox()
        self.outline_width.setRange(1, 10)
        self.outline_width.setValue(1)
        self.outline_width.valueChanged.connect(self.schedule_preview_update)
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
        self.image_scale.valueChanged.connect(self.schedule_preview_update)
        image_layout.addWidget(self.image_scale, 1, 1)

        # 透明度
        image_layout.addWidget(QLabel("透明度:"), 1, 2)
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 100)
        self.image_opacity_slider.setValue(80)
        self.image_opacity_slider.valueChanged.connect(self.schedule_preview_update)
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

        return widget

    def create_per_image_settings_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 个性化设置提示
        info_label = QLabel("个性化设置允许您为每张图片单独设置水印参数。\n\n选择左侧图片列表中的图片，然后调整以下设置。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background: rgba(255, 255, 255, 0.5); padding: 15px; border-radius: 8px;")
        layout.addWidget(info_label)

        # 个性化文本内容
        text_group = QGroupBox("个性化文本内容")
        text_layout = QVBoxLayout(text_group)

        self.per_image_text_input = QLineEdit()
        self.per_image_text_input.setPlaceholderText("为空时使用共享设置的文本内容")
        self.per_image_text_input.textChanged.connect(self.schedule_preview_update)
        text_layout.addWidget(self.per_image_text_input)

        layout.addWidget(text_group)

        # 个性化位置偏移
        position_group = QGroupBox("个性化位置偏移")
        position_layout = QGridLayout(position_group)

        position_layout.addWidget(QLabel("水平偏移:"), 0, 0)
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-1000, 1000)
        self.offset_x_spin.setValue(0)
        self.offset_x_spin.valueChanged.connect(self.schedule_preview_update)
        position_layout.addWidget(self.offset_x_spin, 0, 1)

        position_layout.addWidget(QLabel("垂直偏移:"), 1, 0)
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-1000, 1000)
        self.offset_y_spin.setValue(0)
        self.offset_y_spin.valueChanged.connect(self.schedule_preview_update)
        position_layout.addWidget(self.offset_y_spin, 1, 1)

        layout.addWidget(position_group)

        # 个性化大小调整
        size_group = QGroupBox("个性化大小调整")
        size_layout = QGridLayout(size_group)

        size_layout.addWidget(QLabel("字体大小调整:"), 0, 0)
        self.font_size_adjust = QSpinBox()
        self.font_size_adjust.setRange(-100, 100)
        self.font_size_adjust.setValue(0)
        self.font_size_adjust.setSuffix("%")
        self.font_size_adjust.valueChanged.connect(self.schedule_preview_update)
        size_layout.addWidget(self.font_size_adjust, 0, 1)

        layout.addWidget(size_group)

        layout.addStretch()

        return widget

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
        self.prefix_input.textChanged.connect(self.schedule_preview_update)
        naming_layout.addWidget(self.prefix_input, 0, 1)

        naming_layout.addWidget(QLabel("后缀:"), 1, 0)
        self.suffix_input = QLineEdit("_watermarked")
        self.suffix_input.textChanged.connect(self.schedule_preview_update)
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
        self.resize_percent.valueChanged.connect(self.schedule_preview_update)
        resize_layout.addWidget(self.resize_percent, 2, 1)

        # 尺寸调整
        resize_layout.addWidget(QLabel("宽度:"), 3, 0)
        self.resize_width = QSpinBox()
        self.resize_width.setRange(1, 10000)
        self.resize_width.setValue(800)
        self.resize_width.setSuffix(" px")
        self.resize_width.setEnabled(False)
        self.resize_width.valueChanged.connect(self.schedule_preview_update)
        resize_layout.addWidget(self.resize_width, 3, 1)

        resize_layout.addWidget(QLabel("高度:"), 3, 2)
        self.resize_height = QSpinBox()
        self.resize_height.setRange(1, 10000)
        self.resize_height.setValue(600)
        self.resize_height.setSuffix(" px")
        self.resize_height.setEnabled(False)
        self.resize_height.valueChanged.connect(self.schedule_preview_update)
        resize_layout.addWidget(self.resize_height, 3, 3)

        # 保持宽高比
        self.keep_aspect_check = QCheckBox("保持宽高比")
        self.keep_aspect_check.setChecked(True)
        self.keep_aspect_check.stateChanged.connect(self.schedule_preview_update)
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

    def on_settings_type_changed(self, text):
        # 切换共享/个性化设置界面
        if text == "共享设置":
            self.settings_stack.setCurrentIndex(0)
            # 应用共享设置到UI
            self.apply_shared_settings_to_ui()
        else:
            self.settings_stack.setCurrentIndex(1)
            # 应用个性化设置到UI
            self.apply_per_image_settings_to_ui()

        self.update_preview()

    def on_watermark_type_changed(self, text):
        is_text = text == "文本水印"
        self.text_group.setVisible(is_text)
        self.image_group.setVisible(not is_text)
        self.schedule_preview_update()

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
        self.schedule_preview_update()

    def on_resize_method_changed(self, button, checked):
        if not checked:
            return

        is_percent = button == self.resize_percent_radio
        self.resize_percent.setEnabled(is_percent and self.resize_check.isChecked())
        self.resize_width.setEnabled(not is_percent and self.resize_check.isChecked())
        self.resize_height.setEnabled(not is_percent and self.resize_check.isChecked())
        self.keep_aspect_check.setEnabled(not is_percent and self.resize_check.isChecked())
        self.schedule_preview_update()

    def on_position_changed(self, position):
        if position == "自定义拖拽":
            self.enable_custom_position()
        else:
            self.disable_custom_position()
            self.schedule_preview_update()

    def on_rotation_changed(self, value):
        self.rotation_value.setText(f"{value}°")
        self.schedule_preview_update()

    def on_zoom_changed(self, value):
        self.zoom_label.setText(f"{value}%")
        self.schedule_preview_update()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
            self.schedule_preview_update()

    def choose_shadow_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.shadow_color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
            self.schedule_preview_update()

    def choose_outline_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.outline_color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px;")
            self.schedule_preview_update()

    def select_watermark_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "",
                                              "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if path:
            self.image_path_label.setText(os.path.basename(path))
            self.shared_settings["image_path"] = path
            self.schedule_preview_update()

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

                # 为每张图片初始化个性化设置
                self.per_image_settings[path] = {
                    "text": "",
                    "offset_x": 0,
                    "offset_y": 0,
                    "font_size_adjust": 0
                }

                # 创建列表项
                item = QListWidgetItem()
                item.setText(os.path.basename(path))

                # 创建缩略图
                try:
                    # 使用PIL处理图片，确保正确显示
                    image = self.load_and_fix_image(path)
                    if image:
                        # 转换为QPixmap
                        image_rgb = image.convert("RGB")
                        data = image_rgb.tobytes("raw", "RGB")
                        qimage = QImage(data, image_rgb.size[0], image_rgb.size[1], QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qimage)

                        # 缩放缩略图
                        thumb = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item.setIcon(QIcon(thumb))
                except Exception as e:
                    print(f"创建缩略图错误: {str(e)}")
                    # 如果无法加载图片，跳过缩略图

                self.image_list.addItem(item)

        # 如果有图片，选择第一个
        if self.images and self.current_image_index == -1:
            self.image_list.setCurrentRow(0)

    def load_and_fix_image(self, path):
        """加载并修复图片（处理方向、模式等问题）"""
        try:
            # 检查缓存
            if path in self.image_cache:
                return self.image_cache[path].copy()

            # 打开图片
            image = Image.open(path)

            # 修复方向问题（处理EXIF方向信息）
            image = self.fix_image_orientation(image)

            # 确保图片是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # 缓存图片
            self.image_cache[path] = image.copy()

            return image
        except Exception as e:
            print(f"加载图片错误: {str(e)}")
            return None

    def fix_image_orientation(self, image):
        """修复图片方向（处理EXIF方向信息）"""
        try:
            # 获取EXIF信息
            exif = image._getexif()
            if exif:
                # 获取方向标签
                orientation_tag = 274  # EXIF方向标签
                if orientation_tag in exif:
                    orientation = exif[orientation_tag]

                    # 根据方向值旋转图片
                    if orientation == 2:
                        # 水平翻转
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        # 旋转180度
                        image = image.rotate(180)
                    elif orientation == 4:
                        # 垂直翻转
                        image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    elif orientation == 5:
                        # 水平翻转并旋转270度
                        image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(270)
                    elif orientation == 6:
                        # 旋转270度
                        image = image.rotate(270)
                    elif orientation == 7:
                        # 水平翻转并旋转90度
                        image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(90)
                    elif orientation == 8:
                        # 旋转90度
                        image = image.rotate(90)
        except Exception as e:
            print(f"修复图片方向错误: {str(e)}")

        return image

    def clear_images(self):
        self.images.clear()
        self.image_list.clear()
        self.current_image_index = -1
        self.per_image_settings.clear()
        self.image_cache.clear()
        self.preview_label.setText("🎨 导入图片后预览将显示在这里")
        if self.draggable_watermark:
            self.draggable_watermark.setParent(None)
            self.draggable_watermark = None

    def on_image_selected(self, index):
        if index >= 0 and index < len(self.images):
            self.current_image_index = index
            # 更新个性化设置UI
            self.apply_per_image_settings_to_ui()
            self.update_preview()

    def preview_mouse_press(self, event):
        if event.button() == Qt.LeftButton and self.custom_position_mode:
            # 在点击位置添加可拖拽水印
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

        # 设置水印文本
        watermark_type = self.watermark_type.currentText()
        if watermark_type == "文本水印":
            text = self.get_current_text()
            self.draggable_watermark.setText(text)

            # 设置字体样式
            font_size = self.get_current_font_size()
            font = QFont(self.font_combo.currentText(), min(font_size // 10, 50))  # 限制预览字体大小
            font.setBold(self.bold_check.isChecked())
            font.setItalic(self.italic_check.isChecked())
            self.draggable_watermark.setFont(font)

            # 设置颜色
            color = self.color_btn.styleSheet().split(": ")[1].split(";")[0]
            self.draggable_watermark.setStyleSheet(
                f"color: {color}; background-color: rgba(255, 255, 255, 0.7); border: 2px dashed #6a11cb; border-radius: 8px;")
        else:
            # 图片水印
            if self.shared_settings["image_path"] and os.path.exists(self.shared_settings["image_path"]):
                try:
                    pixmap = QPixmap(self.shared_settings["image_path"])
                    if not pixmap.isNull():
                        # 缩放图片
                        scale = self.image_scale.value() / 100.0
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
        # 更新水印位置设置
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            self.per_image_settings[image_path]["offset_x"] = x
            self.per_image_settings[image_path]["offset_y"] = y

    def schedule_preview_update(self):
        # 延迟更新预览，避免频繁操作导致的卡顿
        self.preview_timer.start(300)  # 300毫秒后更新

    def update_preview_delayed(self):
        self.update_preview()

    def update_preview(self):
        if self.current_image_index < 0 or self.current_image_index >= len(self.images):
            return

        image_path = self.images[self.current_image_index]

        try:
            # 打开并修复原始图片
            original_image = self.load_and_fix_image(image_path)
            if original_image is None:
                return

            # 调整图片尺寸（如果启用）
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
                        # 保持宽高比
                        original_ratio = original_image.size[0] / original_image.size[1]
                        if width / height > original_ratio:
                            # 以高度为准
                            new_width = int(height * original_ratio)
                            new_height = height
                        else:
                            # 以宽度为准
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

    def add_watermark_to_image(self, image):
        # 创建一个副本，避免修改原图
        result = image.copy()

        # 获取水印类型
        watermark_type = self.watermark_type.currentText()

        if watermark_type == "文本水印":
            result = self.add_text_watermark(result)
        else:
            result = self.add_image_watermark(result)

        return result

    def get_current_text(self):
        """获取当前文本（考虑个性化设置）"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            per_image_text = self.per_image_settings[image_path]["text"]
            if per_image_text:
                return per_image_text
        return self.text_input.text()

    def get_current_font_size(self):
        """获取当前字体大小（考虑个性化设置）"""
        base_size = self.font_size.value()
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            size_adjust = self.per_image_settings[image_path]["font_size_adjust"]
            adjusted_size = base_size * (1 + size_adjust / 100)
            return int(adjusted_size)
        return base_size

    def get_current_offset(self):
        """获取当前偏移量（考虑个性化设置）"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            return (
                self.per_image_settings[image_path]["offset_x"],
                self.per_image_settings[image_path]["offset_y"]
            )
        return (0, 0)

    def add_text_watermark(self, image):
        # 确保图像是RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 获取文本设置
        text = self.get_current_text()
        if not text:  # 如果文本为空，直接返回原图
            return image

        font_family = self.font_combo.currentText()
        font_size = self.get_current_font_size()

        # 创建字体 - 修复中文显示问题
        try:
            # 尝试加载系统字体
            font_path = self.get_font_path(font_family)
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 如果找不到字体文件，尝试使用默认中文字体
                try:
                    # 尝试几种常见的中文字体
                    for fallback_font in ["simhei.ttf", "msyh.ttc", "simsun.ttc"]:
                        try:
                            font = ImageFont.truetype(fallback_font, font_size)
                            break
                        except:
                            continue
                    else:
                        # 如果都失败了，使用默认字体
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
        except:
            # 如果失败，使用默认字体
            font = ImageFont.load_default()

        # 创建临时图像来计算文本尺寸
        temp_image = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_image)

        # 获取文本尺寸
        try:
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # 旧版本PIL兼容
            text_width, text_height = temp_draw.textsize(text, font=font)

        # 计算水印位置
        position = self.position_combo.currentText()
        img_width, img_height = image.size

        if position == "自定义拖拽" and self.draggable_watermark:
            # 使用自定义位置
            offset_x, offset_y = self.get_current_offset()
            x = offset_x
            y = offset_y

            # 转换坐标（从预览坐标到实际图像坐标）
            if self.preview_label.pixmap():
                preview_pixmap = self.preview_label.pixmap()
                pixmap_width = preview_pixmap.width()
                pixmap_height = preview_pixmap.height()

                if pixmap_width > 0 and pixmap_height > 0:
                    # 计算实际图像与预览图像的比例
                    scale_x = img_width / pixmap_width
                    scale_y = img_height / pixmap_height
                    x = int(x * scale_x)
                    y = int(y * scale_y)
        else:
            # 使用预设位置
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
            else:  # 默认右下角
                x, y = img_width - text_width - 10, img_height - text_height - 10

            # 应用个性化偏移
            offset_x, offset_y = self.get_current_offset()
            x += offset_x
            y += offset_y

        # 获取颜色和透明度
        color = self.color_btn.styleSheet().split(": ")[1].split(";")[0]
        opacity = self.opacity_slider.value()

        # 创建带透明度的颜色
        from PIL import ImageColor
        rgb = ImageColor.getrgb(color)

        # 应用旋转
        rotation_angle = self.rotation_slider.value()

        if rotation_angle != 0:
            # 创建一个临时图像来旋转文本
            text_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_image)

            # 如果有描边效果
            if self.outline_check.isChecked():
                outline_color = self.outline_color_btn.styleSheet().split(": ")[1].split(";")[0]
                outline_width = self.outline_width.value()
                outline_rgb = ImageColor.getrgb(outline_color)

                # 绘制描边（在多个位置绘制文本模拟描边）
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            text_draw.text((x + dx, y + dy), text, font=font, fill=outline_rgb)

            # 如果有阴影效果
            if self.shadow_check.isChecked():
                shadow_color = self.shadow_color_btn.styleSheet().split(": ")[1].split(";")[0]
                shadow_offset = self.shadow_offset.value()
                shadow_rgb = ImageColor.getrgb(shadow_color)

                # 绘制阴影
                text_draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_rgb)

            # 绘制文本
            text_draw.text((x, y), text, font=font, fill=rgb + (int(255 * opacity / 100),))

            # 旋转文本图像
            rotated_text = text_image.rotate(rotation_angle, resample=Image.BICUBIC, expand=False, center=(x, y))

            # 将旋转后的文本合并到原图
            image = Image.alpha_composite(image.convert('RGBA'), rotated_text).convert('RGB')
        else:
            # 不旋转的情况，直接绘制到原图
            draw = ImageDraw.Draw(image)

            # 如果有描边效果
            if self.outline_check.isChecked():
                outline_color = self.outline_color_btn.styleSheet().split(": ")[1].split(";")[0]
                outline_width = self.outline_width.value()
                outline_rgb = ImageColor.getrgb(outline_color)

                # 绘制描边（在多个位置绘制文本模拟描边）
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=outline_rgb)

            # 如果有阴影效果
            if self.shadow_check.isChecked():
                shadow_color = self.shadow_color_btn.styleSheet().split(": ")[1].split(";")[0]
                shadow_offset = self.shadow_offset.value()
                shadow_rgb = ImageColor.getrgb(shadow_color)

                # 绘制阴影
                draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_rgb)

            # 绘制文本
            draw.text((x, y), text, font=font, fill=rgb)

        return image

    def add_image_watermark(self, image):
        # 获取水印图片路径
        watermark_path = self.shared_settings["image_path"]
        if not watermark_path or not os.path.exists(watermark_path):
            return image

        try:
            # 打开水印图片
            watermark = Image.open(watermark_path)

            # 如果有透明通道，保持透明
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')

            # 缩放水印
            scale = self.image_scale.value() / 100.0
            new_width = int(watermark.width * scale)
            new_height = int(watermark.height * scale)
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 设置透明度
            opacity = self.image_opacity_slider.value()
            if opacity < 100:
                # 调整透明度
                alpha = watermark.split()[3]
                alpha = alpha.point(lambda p: p * opacity / 100)
                watermark.putalpha(alpha)

            # 计算水印位置
            position = self.position_combo.currentText()
            img_width, img_height = image.size
            wm_width, wm_height = watermark.size

            if position == "自定义拖拽" and self.draggable_watermark:
                # 使用自定义位置
                offset_x, offset_y = self.get_current_offset()
                x = offset_x
                y = offset_y

                # 转换坐标（从预览坐标到实际图像坐标）
                if self.preview_label.pixmap():
                    preview_pixmap = self.preview_label.pixmap()
                    pixmap_width = preview_pixmap.width()
                    pixmap_height = preview_pixmap.height()

                    if pixmap_width > 0 and pixmap_height > 0:
                        # 计算实际图像与预览图像的比例
                        scale_x = img_width / pixmap_width
                        scale_y = img_height / pixmap_height
                        x = int(x * scale_x)
                        y = int(y * scale_y)
            else:
                # 使用预设位置
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
                else:  # 默认右下角
                    x, y = img_width - wm_width - 10, img_height - wm_height - 10

                # 应用个性化偏移
                offset_x, offset_y = self.get_current_offset()
                x += offset_x
                y += offset_y

            # 应用旋转
            rotation_angle = self.rotation_slider.value()
            if rotation_angle != 0:
                # 计算旋转中心（水印中心）
                center_x = x + wm_width // 2
                center_y = y + wm_height // 2

                # 旋转水印
                watermark = watermark.rotate(rotation_angle, resample=Image.BICUBIC, expand=True)

                # 更新水印尺寸
                wm_width, wm_height = watermark.size

                # 重新计算位置，使旋转后的水印中心保持不变
                x = center_x - wm_width // 2
                y = center_y - wm_height // 2

            # 确保水印位置在图像范围内
            x = max(0, min(x, img_width - wm_width))
            y = max(0, min(y, img_height - wm_height))

            # 如果原图没有透明通道，转换为RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # 合并水印
            image.paste(watermark, (x, y), watermark)

            return image.convert("RGB")  # 转换回RGB

        except Exception as e:
            print(f"图片水印错误: {str(e)}")
            return image

    def get_font_path(self, font_family):
        # 尝试查找字体文件路径
        # 这是一个简化的实现，实际应用中可能需要更复杂的字体查找逻辑
        if sys.platform == "win32":
            font_paths = [
                os.path.join(os.environ['WINDIR'], 'Fonts'),
                os.path.join(os.environ['SYSTEMROOT'], 'Fonts')
            ]
        elif sys.platform == "darwin":  # macOS
            font_paths = [
                '/Library/Fonts',
                '/System/Library/Fonts',
                os.path.expanduser('~/Library/Fonts')
            ]
        else:  # Linux
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
        # 从共享设置更新UI控件
        self.watermark_type.setCurrentText(self.shared_settings["type"])
        self.text_input.setText("水印")  # 默认文本
        self.font_combo.setCurrentText(self.shared_settings["font_family"])
        self.font_size.setValue(self.shared_settings["font_size"])
        self.bold_check.setChecked(self.shared_settings["bold"])
        self.italic_check.setChecked(self.shared_settings["italic"])

        color = self.shared_settings["color"]
        self.color_btn.setStyleSheet(f"background-color: {color}; border-radius: 4px;")

        self.opacity_slider.setValue(self.shared_settings["opacity"])
        self.position_combo.setCurrentText(self.shared_settings["position"])
        self.rotation_slider.setValue(self.shared_settings["rotation"])
        self.shadow_check.setChecked(self.shared_settings["shadow"])

        shadow_color = self.shared_settings["shadow_color"]
        self.shadow_color_btn.setStyleSheet(f"background-color: {shadow_color}; border-radius: 4px;")

        self.shadow_offset.setValue(self.shared_settings["shadow_offset"])
        self.shadow_blur.setValue(self.shared_settings["shadow_blur"])
        self.outline_check.setChecked(self.shared_settings["outline"])

        outline_color = self.shared_settings["outline_color"]
        self.outline_color_btn.setStyleSheet(f"background-color: {outline_color}; border-radius: 4px;")

        self.outline_width.setValue(self.shared_settings["outline_width"])
        self.image_path_label.setText(
            os.path.basename(self.shared_settings["image_path"]) if self.shared_settings["image_path"] else "未选择")
        self.image_scale.setValue(self.shared_settings["image_scale"])
        self.image_opacity_slider.setValue(80)  # 默认值

    def apply_per_image_settings_to_ui(self):
        """应用个性化设置到UI"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            settings = self.per_image_settings[image_path]

            self.per_image_text_input.setText(settings["text"])
            self.offset_x_spin.setValue(settings["offset_x"])
            self.offset_y_spin.setValue(settings["offset_y"])
            self.font_size_adjust.setValue(settings["font_size_adjust"])

    def save_shared_settings_from_ui(self):
        """从UI保存共享设置"""
        self.shared_settings.update({
            "type": self.watermark_type.currentText(),
            "font_family": self.font_combo.currentText(),
            "font_size": self.font_size.value(),
            "bold": self.bold_check.isChecked(),
            "italic": self.italic_check.isChecked(),
            "color": self.color_btn.styleSheet().split(": ")[1].split(";")[0],
            "opacity": self.opacity_slider.value(),
            "position": self.position_combo.currentText(),
            "rotation": self.rotation_slider.value(),
            "shadow": self.shadow_check.isChecked(),
            "shadow_color": self.shadow_color_btn.styleSheet().split(": ")[1].split(";")[0],
            "shadow_offset": self.shadow_offset.value(),
            "shadow_blur": self.shadow_blur.value(),
            "outline": self.outline_check.isChecked(),
            "outline_color": self.outline_color_btn.styleSheet().split(": ")[1].split(";")[0],
            "outline_width": self.outline_width.value(),
            "image_path": self.shared_settings["image_path"],  # 保持不变
            "image_scale": self.image_scale.value(),
        })

    def save_per_image_settings_from_ui(self):
        """从UI保存个性化设置"""
        if self.current_image_index >= 0:
            image_path = self.images[self.current_image_index]
            self.per_image_settings[image_path].update({
                "text": self.per_image_text_input.text(),
                "offset_x": self.offset_x_spin.value(),
                "offset_y": self.offset_y_spin.value(),
                "font_size_adjust": self.font_size_adjust.value()
            })

    def use_exif_date(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, "提示", "请先选择一张图片")
            return

        image_path = self.images[self.current_image_index]
        date = self.get_exif_date(image_path)
        if date:
            if self.settings_type_combo.currentText() == "共享设置":
                self.text_input.setText(date)
            else:
                self.per_image_text_input.setText(date)
            self.schedule_preview_update()

    def get_exif_date(self, image_path):
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()

            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal' and value:
                        # 格式: "YYYY:MM:DD HH:MM:SS"
                        date_part = value.split()[0]
                        return date_part.replace(":", "-")  # "YYYY-MM-DD"

        except:
            pass

        # 如果EXIF中没有日期，使用文件修改时间
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

        # 检查输出文件夹是否是原文件夹
        for image_path in self.images:
            if os.path.dirname(image_path) == output_path:
                reply = QMessageBox.question(self, "确认",
                                             "输出文件夹与原文件夹相同，这可能会覆盖原文件。是否继续？",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                break

        # 创建进度对话框
        self.progress_dialog = QProgressDialog("正在导出图片...", "取消", 0, len(self.images), self)
        self.progress_dialog.setWindowTitle("导出进度")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # 使用线程进行导出，避免界面冻结
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
            # 打开并修复原始图片
            original_image = self.load_and_fix_image(image_path)
            if original_image is None:
                raise Exception("无法加载图片")

            # 调整图片尺寸（如果启用）
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
                        # 保持宽高比
                        original_ratio = original_image.size[0] / original_image.size[1]
                        if width / height > original_ratio:
                            # 以高度为准
                            new_width = int(height * original_ratio)
                            new_height = height
                        else:
                            # 以宽度为准
                            new_width = width
                            new_height = int(width / original_ratio)
                    else:
                        new_width = width
                        new_height = height

                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 添加水印
            watermarked_image = self.add_watermark_to_image(original_image)

            # 生成输出文件名
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)

            prefix = self.prefix_input.text()
            suffix = self.suffix_input.text()

            output_filename = f"{prefix}{name}{suffix}{ext}"
            output_filepath = os.path.join(output_path, output_filename)

            # 确保输出目录存在
            os.makedirs(output_path, exist_ok=True)

            # 保存图片
            format = self.format_combo.currentText()
            if format == "JPEG":
                quality = self.quality_slider.value()
                watermarked_image.save(output_filepath, format, quality=quality, optimize=True)
            else:
                watermarked_image.save(output_filepath, format, optimize=True)
        except Exception as e:
            raise Exception(f"处理图片 {os.path.basename(image_path)} 时出错: {str(e)}")

    def save_template(self):
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if ok and name:
            # 保存共享设置
            self.save_shared_settings_from_ui()

            # 收集当前设置
            template = {
                "shared_settings": self.shared_settings.copy()
            }

            # 保存到文件
            templates_dir = os.path.join(os.path.expanduser("~"), ".watermark_templates")
            os.makedirs(templates_dir, exist_ok=True)

            template_path = os.path.join(templates_dir, f"{name}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)

            # 更新模板列表
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

            # 应用模板设置
            if "shared_settings" in template:
                self.shared_settings.update(template["shared_settings"])
                self.apply_shared_settings_to_ui()

            # 更新预览
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
                    template_name = file[:-5]  # 去掉.json扩展名
                    self.template_list.addItem(template_name)

    def reset_rotation(self):
        self.rotation_slider.setValue(0)

    def load_settings(self):
        # 加载应用设置
        settings_path = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # 应用设置
                self.auto_load_check.setChecked(settings.get("auto_load_last", False))
                if settings.get("auto_load_last", False):
                    # 加载上次使用的模板
                    last_template = settings.get("last_template")
                    if last_template and os.path.exists(
                            os.path.join(os.path.expanduser("~"), ".watermark_templates", f"{last_template}.json")):
                        self.load_template_by_name(last_template)

            except:
                pass  # 如果设置文件损坏，忽略错误

    def save_settings(self):
        # 保存应用设置
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
        # 保存设置
        self.save_settings()
        event.accept()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]

        # 过滤出图片文件
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        image_paths = [path for path in paths if any(path.lower().endswith(ext) for ext in extensions)]

        if image_paths:
            self.add_images(image_paths)
        else:
            QMessageBox.warning(self, "警告", "拖放的文件中没有支持的图片格式")

        event.acceptProposedAction()


# 运行应用
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    window = WatermarkApp()
    window.show()

    sys.exit(app.exec_())