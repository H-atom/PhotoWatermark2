import os
import sys
import json
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem, QTabWidget,
                             QGroupBox, QComboBox, QSpinBox, QSlider, QLineEdit, QColorDialog,
                             QFileDialog, QCheckBox, QMessageBox, QGridLayout, QSplitter,
                             QScrollArea, QFrame, QDoubleSpinBox, QProgressBar)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor, QFont, QPainter, QDragEnterEvent, QDropEvent


class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("图片水印工具")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧图片列表区域
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧设置和预览区域
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)

        # 初始化状态
        self.current_image_index = -1
        self.images = []
        self.watermark_settings = {
            "type": "text",
            "text": "水印",
            "font_family": "Arial",
            "font_size": 40,
            "bold": False,
            "italic": False,
            "color": "#FFFFFF",
            "opacity": 80,
            "position": "bottom-right",
            "offset_x": 0,
            "offset_y": 0,
            "rotation": 0,
            "shadow": False,
            "shadow_color": "#000000",
            "shadow_offset": 2,
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

    def create_left_panel(self):
        # 左侧面板 - 图片列表
        left_widget = QWidget()
        layout = QVBoxLayout(left_widget)

        # 标题
        title_label = QLabel("图片列表")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # 导入按钮
        import_layout = QHBoxLayout()
        self.import_btn = QPushButton("导入图片")
        self.import_btn.clicked.connect(self.import_images)
        import_layout.addWidget(self.import_btn)

        self.import_folder_btn = QPushButton("导入文件夹")
        self.import_folder_btn.clicked.connect(self.import_folder)
        import_layout.addWidget(self.import_folder_btn)

        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_images)
        import_layout.addWidget(self.clear_btn)

        layout.addLayout(import_layout)

        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(100, 100))
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

        # 创建标签页
        self.tabs = QTabWidget()

        # 水印设置标签页
        self.watermark_tab = self.create_watermark_tab()
        self.tabs.addTab(self.watermark_tab, "水印设置")

        # 导出设置标签页
        self.export_tab = self.create_export_tab()
        self.tabs.addTab(self.export_tab, "导出设置")

        # 模板管理标签页
        self.template_tab = self.create_template_tab()
        self.tabs.addTab(self.template_tab, "模板管理")

        layout.addWidget(self.tabs)

        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)

        # 预览图像区域
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.preview_label.setText("导入图片后预览将显示在这里")
        preview_layout.addWidget(self.preview_label)

        # 水印位置控制
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("水印位置:"))

        self.position_combo = QComboBox()
        self.position_combo.addItems(["左上角", "中上", "右上角", "左中", "居中", "右中", "左下角", "中下", "右下角", "自定义"])
        self.position_combo.currentTextChanged.connect(self.update_preview)
        position_layout.addWidget(self.position_combo)

        position_layout.addStretch()
        preview_layout.addLayout(position_layout)

        layout.addWidget(preview_group)

        # 导出按钮
        export_btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("导出所有图片")
        self.export_btn.clicked.connect(self.export_all_images)
        self.export_btn.setStyleSheet("font-size: 14px; padding: 10px;")
        export_btn_layout.addWidget(self.export_btn)

        layout.addLayout(export_btn_layout)

        return right_widget

    def create_watermark_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

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
        self.text_input.textChanged.connect(self.update_preview)
        text_layout.addWidget(self.text_input, 0, 1)

        # 从EXIF获取日期按钮
        self.exif_date_btn = QPushButton("使用EXIF日期")
        self.exif_date_btn.clicked.connect(self.use_exif_date)
        text_layout.addWidget(self.exif_date_btn, 0, 2)

        # 字体设置
        text_layout.addWidget(QLabel("字体:"), 1, 0)
        self.font_combo = QComboBox()
        # 添加一些常见字体
        self.font_combo.addItems(["Arial", "Times New Roman", "Helvetica", "Courier New",
                                  "Verdana", "Georgia", "Palatino", "Garamond"])
        self.font_combo.currentTextChanged.connect(self.update_preview)
        text_layout.addWidget(self.font_combo, 1, 1)

        # 字体大小
        text_layout.addWidget(QLabel("字体大小:"), 1, 2)
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 200)
        self.font_size.setValue(40)
        self.font_size.valueChanged.connect(self.update_preview)
        text_layout.addWidget(self.font_size, 1, 3)

        # 粗体和斜体
        self.bold_check = QCheckBox("粗体")
        self.bold_check.stateChanged.connect(self.update_preview)
        text_layout.addWidget(self.bold_check, 2, 0)

        self.italic_check = QCheckBox("斜体")
        self.italic_check.stateChanged.connect(self.update_preview)
        text_layout.addWidget(self.italic_check, 2, 1)

        # 颜色选择
        text_layout.addWidget(QLabel("颜色:"), 3, 0)
        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet("background-color: #FFFFFF;")
        self.color_btn.clicked.connect(self.choose_color)
        text_layout.addWidget(self.color_btn, 3, 1)

        # 透明度
        text_layout.addWidget(QLabel("透明度:"), 3, 2)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.update_preview)
        text_layout.addWidget(self.opacity_slider, 3, 3)

        # 阴影效果
        self.shadow_check = QCheckBox("阴影效果")
        self.shadow_check.stateChanged.connect(self.update_preview)
        text_layout.addWidget(self.shadow_check, 4, 0)

        text_layout.addWidget(QLabel("阴影颜色:"), 4, 1)
        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setStyleSheet("background-color: #000000;")
        self.shadow_color_btn.clicked.connect(self.choose_shadow_color)
        text_layout.addWidget(self.shadow_color_btn, 4, 2)

        text_layout.addWidget(QLabel("阴影偏移:"), 4, 3)
        self.shadow_offset = QSpinBox()
        self.shadow_offset.setRange(1, 10)
        self.shadow_offset.setValue(2)
        self.shadow_offset.valueChanged.connect(self.update_preview)
        text_layout.addWidget(self.shadow_offset, 4, 4)

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
        self.image_scale.valueChanged.connect(self.update_preview)
        image_layout.addWidget(self.image_scale, 1, 1)

        # 透明度
        image_layout.addWidget(QLabel("透明度:"), 1, 2)
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 100)
        self.image_opacity_slider.setValue(80)
        self.image_opacity_slider.valueChanged.connect(self.update_preview)
        image_layout.addWidget(self.image_opacity_slider, 1, 3)

        layout.addWidget(self.image_group)

        # 旋转设置
        rotation_group = QGroupBox("旋转")
        rotation_layout = QHBoxLayout(rotation_group)

        rotation_layout.addWidget(QLabel("旋转角度:"))
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.valueChanged.connect(self.update_preview)
        rotation_layout.addWidget(self.rotation_slider)

        self.rotation_value = QLabel("0°")
        rotation_layout.addWidget(self.rotation_value)

        layout.addWidget(rotation_group)

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
        self.prefix_input.textChanged.connect(self.update_preview)
        naming_layout.addWidget(self.prefix_input, 0, 1)

        naming_layout.addWidget(QLabel("后缀:"), 1, 0)
        self.suffix_input = QLineEdit("_watermarked")
        self.suffix_input.textChanged.connect(self.update_preview)
        naming_layout.addWidget(self.suffix_input, 1, 1)

        layout.addWidget(naming_group)

        # 图片尺寸调整（可选功能）
        resize_group = QGroupBox("图片尺寸调整（可选）")
        resize_layout = QGridLayout(resize_group)

        self.resize_check = QCheckBox("调整图片尺寸")
        self.resize_check.stateChanged.connect(self.on_resize_changed)
        resize_layout.addWidget(self.resize_check, 0, 0, 1, 2)

        resize_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.resize_width = QSpinBox()
        self.resize_width.setRange(1, 10000)
        self.resize_width.setValue(0)
        self.resize_width.setSuffix(" px")
        self.resize_width.setEnabled(False)
        resize_layout.addWidget(self.resize_width, 1, 1)

        resize_layout.addWidget(QLabel("高度:"), 1, 2)
        self.resize_height = QSpinBox()
        self.resize_height.setRange(1, 10000)
        self.resize_height.setValue(0)
        self.resize_height.setSuffix(" px")
        self.resize_height.setEnabled(False)
        resize_layout.addWidget(self.resize_height, 1, 3)

        resize_layout.addWidget(QLabel("缩放百分比:"), 2, 0)
        self.resize_percent = QSpinBox()
        self.resize_percent.setRange(1, 500)
        self.resize_percent.setValue(100)
        self.resize_percent.setSuffix("%")
        self.resize_percent.setEnabled(False)
        resize_layout.addWidget(self.resize_percent, 2, 1)

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

    def on_watermark_type_changed(self, text):
        is_text = text == "文本水印"
        self.text_group.setVisible(is_text)
        self.image_group.setVisible(not is_text)
        self.update_preview()

    def on_format_changed(self, text):
        is_jpeg = text == "JPEG"
        self.quality_slider.setEnabled(is_jpeg)
        self.quality_label.setEnabled(is_jpeg)

    def on_resize_changed(self, state):
        enabled = state == Qt.Checked
        self.resize_width.setEnabled(enabled)
        self.resize_height.setEnabled(enabled)
        self.resize_percent.setEnabled(enabled)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.update_preview()

    def choose_shadow_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.shadow_color_btn.setStyleSheet(f"background-color: {color.name()};")
            self.update_preview()

    def select_watermark_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "",
                                              "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if path:
            self.image_path_label.setText(os.path.basename(path))
            self.update_preview()

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

                # 创建列表项
                item = QListWidgetItem()
                item.setText(os.path.basename(path))

                # 创建缩略图
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # 缩放缩略图
                    thumb = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item.setIcon(QIcon(thumb))

                self.image_list.addItem(item)

        # 如果有图片，选择第一个
        if self.images and self.current_image_index == -1:
            self.image_list.setCurrentRow(0)

    def clear_images(self):
        self.images.clear()
        self.image_list.clear()
        self.current_image_index = -1
        self.preview_label.setText("导入图片后预览将显示在这里")

    def on_image_selected(self, index):
        if index >= 0 and index < len(self.images):
            self.current_image_index = index
            self.update_preview()

    def update_preview(self):
        if self.current_image_index < 0 or self.current_image_index >= len(self.images):
            return

        image_path = self.images[self.current_image_index]

        try:
            # 打开原始图片
            original_image = Image.open(image_path)

            # 调整图片尺寸（如果启用）
            if self.resize_check.isChecked():
                width = self.resize_width.value()
                height = self.resize_height.value()
                percent = self.resize_percent.value()

                if width > 0 and height > 0:
                    original_image = original_image.resize((width, height), Image.Resampling.LANCZOS)
                elif width > 0:
                    w_percent = width / float(original_image.size[0])
                    h_size = int(float(original_image.size[1]) * float(w_percent))
                    original_image = original_image.resize((width, h_size), Image.Resampling.LANCZOS)
                elif height > 0:
                    h_percent = height / float(original_image.size[1])
                    w_size = int(float(original_image.size[0]) * float(h_percent))
                    original_image = original_image.resize((w_size, height), Image.Resampling.LANCZOS)
                else:
                    new_width = int(original_image.size[0] * percent / 100)
                    new_height = int(original_image.size[1] * percent / 100)
                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 添加水印
            watermarked_image = self.add_watermark_to_image(original_image)

            # 转换为QPixmap并显示
            watermarked_image = watermarked_image.convert("RGB")
            data = watermarked_image.tobytes("raw", "RGB")
            qimage = QImage(data, watermarked_image.size[0], watermarked_image.size[1], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # 缩放以适应预览区域
            preview_size = self.preview_label.size()
            scaled_pixmap = pixmap.scaled(preview_size.width() - 20, preview_size.height() - 20,
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法加载图片: {str(e)}")

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

    def add_text_watermark(self, image):
        # 创建可绘制对象
        draw = ImageDraw.Draw(image)

        # 获取文本设置
        text = self.text_input.text()
        font_family = self.font_combo.currentText()
        font_size = self.font_size.value()
        bold = self.bold_check.isChecked()
        italic = self.italic_check.isChecked()

        # 创建字体
        try:
            # 尝试加载系统字体
            font = ImageFont.truetype(font_family, font_size)
        except:
            # 如果失败，使用默认字体
            font = ImageFont.load_default()

        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 计算水印位置
        position = self.position_combo.currentText()
        img_width, img_height = image.size

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
        else:  # 自定义
            x, y = 10, 10

        # 获取颜色和透明度
        color = self.color_btn.styleSheet().split(": ")[1].split(";")[0]
        opacity = self.opacity_slider.value()

        # 创建带透明度的颜色
        from PIL import ImageColor
        rgb = ImageColor.getrgb(color)
        rgba = rgb + (int(255 * opacity / 100),)

        # 如果有阴影效果
        if self.shadow_check.isChecked():
            shadow_color = self.shadow_color_btn.styleSheet().split(": ")[1].split(";")[0]
            shadow_offset = self.shadow_offset.value()
            shadow_rgb = ImageColor.getrgb(shadow_color)
            shadow_rgba = shadow_rgb + (int(255 * opacity / 100),)

            # 绘制阴影
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_rgba)

        # 绘制文本
        draw.text((x, y), text, font=font, fill=rgba)

        return image

    def add_image_watermark(self, image):
        # 获取水印图片路径
        watermark_path = self.image_path_label.text()
        if watermark_path == "未选择":
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
            opacity = self.image_opacity_slider.value() / 100.0
            if opacity < 1.0:
                # 调整透明度
                alpha = watermark.split()[3]
                alpha = alpha.point(lambda p: p * opacity)
                watermark.putalpha(alpha)

            # 计算水印位置
            position = self.position_combo.currentText()
            img_width, img_height = image.size
            wm_width, wm_height = watermark.size

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
            else:  # 自定义
                x, y = 10, 10

            # 如果原图没有透明通道，转换为RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # 合并水印
            image.paste(watermark, (x, y), watermark)

            return image.convert("RGB")  # 转换回RGB

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法添加图片水印: {str(e)}")
            return image

    def use_exif_date(self):
        if self.current_image_index < 0:
            QMessageBox.information(self, "提示", "请先选择一张图片")
            return

        image_path = self.images[self.current_image_index]
        date = self.get_exif_date(image_path)
        if date:
            self.text_input.setText(date)

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
        progress_dialog = QProgressDialog("正在导出图片...", "取消", 0, len(self.images), self)
        progress_dialog.setWindowTitle("导出进度")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        # 导出每张图片
        for i, image_path in enumerate(self.images):
            if progress_dialog.wasCanceled():
                break

            try:
                self.export_single_image(image_path, output_path)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出图片失败: {str(e)}")

            progress_dialog.setValue(i + 1)
            QApplication.processEvents()  # 保持UI响应

        progress_dialog.close()
        QMessageBox.information(self, "完成", f"已成功导出 {len(self.images)} 张图片")

    def export_single_image(self, image_path, output_path):
        # 打开原始图片
        original_image = Image.open(image_path)

        # 调整图片尺寸（如果启用）
        if self.resize_check.isChecked():
            width = self.resize_width.value()
            height = self.resize_height.value()
            percent = self.resize_percent.value()

            if width > 0 and height > 0:
                original_image = original_image.resize((width, height), Image.Resampling.LANCZOS)
            elif width > 0:
                w_percent = width / float(original_image.size[0])
                h_size = int(float(original_image.size[1]) * float(w_percent))
                original_image = original_image.resize((width, h_size), Image.Resampling.LANCZOS)
            elif height > 0:
                h_percent = height / float(original_image.size[1])
                w_size = int(float(original_image.size[0]) * float(h_percent))
                original_image = original_image.resize((w_size, height), Image.Resampling.LANCZOS)
            else:
                new_width = int(original_image.size[0] * percent / 100)
                new_height = int(original_image.size[1] * percent / 100)
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
            watermarked_image.save(output_filepath, format, quality=quality)
        else:
            watermarked_image.save(output_filepath, format)

    def save_template(self):
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if ok and name:
            # 收集当前设置
            template = {
                "type": self.watermark_type.currentText(),
                "text": self.text_input.text(),
                "font_family": self.font_combo.currentText(),
                "font_size": self.font_size.value(),
                "bold": self.bold_check.isChecked(),
                "italic": self.italic_check.isChecked(),
                "color": self.color_btn.styleSheet().split(": ")[1].split(";")[0],
                "opacity": self.opacity_slider.value(),
                "position": self.position_combo.currentText(),
                "shadow": self.shadow_check.isChecked(),
                "shadow_color": self.shadow_color_btn.styleSheet().split(": ")[1].split(";")[0],
                "shadow_offset": self.shadow_offset.value(),
                "image_path": self.image_path_label.text(),
                "image_scale": self.image_scale.value(),
                "image_opacity": self.image_opacity_slider.value(),
                "rotation": self.rotation_slider.value(),
                "output_format": self.format_combo.currentText(),
                "quality": self.quality_slider.value(),
                "resize_enabled": self.resize_check.isChecked(),
                "resize_width": self.resize_width.value(),
                "resize_height": self.resize_height.value(),
                "resize_percent": self.resize_percent.value(),
                "naming_prefix": self.prefix_input.text(),
                "naming_suffix": self.suffix_input.text()
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
            self.watermark_type.setCurrentText(template.get("type", "文本水印"))
            self.text_input.setText(template.get("text", "水印"))
            self.font_combo.setCurrentText(template.get("font_family", "Arial"))
            self.font_size.setValue(template.get("font_size", 40))
            self.bold_check.setChecked(template.get("bold", False))
            self.italic_check.setChecked(template.get("italic", False))

            color = template.get("color", "#FFFFFF")
            self.color_btn.setStyleSheet(f"background-color: {color};")

            self.opacity_slider.setValue(template.get("opacity", 80))
            self.position_combo.setCurrentText(template.get("position", "右下角"))
            self.shadow_check.setChecked(template.get("shadow", False))

            shadow_color = template.get("shadow_color", "#000000")
            self.shadow_color_btn.setStyleSheet(f"background-color: {shadow_color};")

            self.shadow_offset.setValue(template.get("shadow_offset", 2))
            self.image_path_label.setText(template.get("image_path", "未选择"))
            self.image_scale.setValue(template.get("image_scale", 100))
            self.image_opacity_slider.setValue(template.get("image_opacity", 80))
            self.rotation_slider.setValue(template.get("rotation", 0))
            self.format_combo.setCurrentText(template.get("output_format", "JPEG"))
            self.quality_slider.setValue(template.get("quality", 90))
            self.resize_check.setChecked(template.get("resize_enabled", False))
            self.resize_width.setValue(template.get("resize_width", 0))
            self.resize_height.setValue(template.get("resize_height", 0))
            self.resize_percent.setValue(template.get("resize_percent", 100))
            self.prefix_input.setText(template.get("naming_prefix", ""))
            self.suffix_input.setText(template.get("naming_suffix", "_watermarked"))

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

    def load_settings(self):
        # 加载应用设置
        settings_path = os.path.join(os.path.expanduser("~"), ".watermark_settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # 应用设置
                if settings.get("auto_load_last", False):
                    # 加载上次使用的模板
                    last_template = settings.get("last_template")
                    if last_template:
                        self.load_template_by_name(last_template)

            except:
                pass  # 如果设置文件损坏，忽略错误

    def save_settings(self):
        # 保存应用设置
        settings = {
            "auto_load_last": self.auto_load_check.isChecked(),
            "last_template": None  # 这里可以保存最后使用的模板
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