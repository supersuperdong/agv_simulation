"""
导出设置对话框模块
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QSpinBox, QCheckBox, QGroupBox,
                             QDialogButtonBox, QGridLayout)
from PyQt5.QtCore import Qt


class ExportDialog(QDialog):
    """地图导出设置对话框"""

    # 预设分辨率配置
    RESOLUTION_PRESETS = {
        "1920x1080 (1080p)": (1920, 1080),
        "2560x1440 (1440p)": (2560, 1440),
        "3840x2160 (4K)": (3840, 2160),
        "5120x2880 (5K)": (5120, 2880),
        "7680x4320 (8K)": (7680, 4320),
        "自定义": None
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("导出地图设置")
        self.setModal(True)
        self.resize(400, 350)

        layout = QVBoxLayout(self)

        # 分辨率设置组
        layout.addWidget(self._create_resolution_group())

        # 导出内容设置组
        layout.addWidget(self._create_content_group())

        # 质量设置组
        layout.addWidget(self._create_quality_group())

        # 按钮组
        layout.addWidget(self._create_button_group())

    def _create_resolution_group(self):
        """创建分辨率设置组"""
        resolution_group = QGroupBox("分辨率设置")
        resolution_layout = QGridLayout(resolution_group)

        # 预设分辨率下拉框
        resolution_layout.addWidget(QLabel("预设分辨率:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(list(self.RESOLUTION_PRESETS.keys()))
        self.resolution_combo.setCurrentIndex(2)  # 默认4K
        resolution_layout.addWidget(self.resolution_combo, 0, 1)

        # 宽度设置
        resolution_layout.addWidget(QLabel("宽度:"), 1, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(800, 20000)
        self.width_spinbox.setValue(3840)
        self.width_spinbox.setSuffix(" px")
        resolution_layout.addWidget(self.width_spinbox, 1, 1)

        # 高度设置
        resolution_layout.addWidget(QLabel("高度:"), 2, 0)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(600, 20000)
        self.height_spinbox.setValue(2160)
        self.height_spinbox.setSuffix(" px")
        resolution_layout.addWidget(self.height_spinbox, 2, 1)

        return resolution_group

    def _create_content_group(self):
        """创建导出内容设置组"""
        content_group = QGroupBox("导出内容")
        content_layout = QVBoxLayout(content_group)

        # AGV选项
        self.include_agvs = QCheckBox("包含AGV")
        self.include_agvs.setChecked(True)
        self.include_agvs.setToolTip("导出图像中是否包含AGV小车")
        content_layout.addWidget(self.include_agvs)

        # 规划路径选项
        self.include_planned_paths = QCheckBox("包含规划路径")
        self.include_planned_paths.setChecked(True)
        self.include_planned_paths.setToolTip("导出图像中是否包含红色虚线规划路径")
        content_layout.addWidget(self.include_planned_paths)

        # 活动路径选项
        self.include_active_paths = QCheckBox("包含活动路径")
        self.include_active_paths.setChecked(True)
        self.include_active_paths.setToolTip("导出图像中是否包含蓝色实线活动路径")
        content_layout.addWidget(self.include_active_paths)

        # 信息面板选项
        self.include_info = QCheckBox("包含信息面板")
        self.include_info.setChecked(False)
        self.include_info.setToolTip("导出图像中是否包含左上角的信息面板")
        content_layout.addWidget(self.include_info)

        return content_group

    def _create_quality_group(self):
        """创建质量设置组"""
        quality_group = QGroupBox("图像质量")
        quality_layout = QVBoxLayout(quality_group)

        # 抗锯齿选项
        self.anti_aliasing = QCheckBox("抗锯齿")
        self.anti_aliasing.setChecked(True)
        self.anti_aliasing.setToolTip("启用抗锯齿可以让图像边缘更平滑")
        quality_layout.addWidget(self.anti_aliasing)

        # 高质量渲染选项
        self.high_quality = QCheckBox("高质量渲染")
        self.high_quality.setChecked(True)
        self.high_quality.setToolTip("启用高质量渲染会增加导出时间但提升图像质量")
        quality_layout.addWidget(self.high_quality)

        return quality_group

    def _create_button_group(self):
        """创建按钮组"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box

    def _connect_signals(self):
        """连接信号和槽"""
        self.resolution_combo.currentTextChanged.connect(self._on_resolution_changed)

    def _on_resolution_changed(self, text):
        """分辨率选择改变时更新数值"""
        if text in self.RESOLUTION_PRESETS:
            preset = self.RESOLUTION_PRESETS[text]
            if preset:  # 不是自定义选项
                width, height = preset
                self.width_spinbox.setValue(width)
                self.height_spinbox.setValue(height)

                # 禁用/启用自定义输入
                is_custom = (text == "自定义")
                self.width_spinbox.setEnabled(is_custom)
                self.height_spinbox.setEnabled(is_custom)
            else:
                # 自定义选项，启用输入框
                self.width_spinbox.setEnabled(True)
                self.height_spinbox.setEnabled(True)

    def get_settings(self):
        """
        获取导出设置

        Returns:
            dict: 导出设置字典
        """
        return {
            'width': self.width_spinbox.value(),
            'height': self.height_spinbox.value(),
            'include_agvs': self.include_agvs.isChecked(),
            'include_planned_paths': self.include_planned_paths.isChecked(),
            'include_active_paths': self.include_active_paths.isChecked(),
            'include_info': self.include_info.isChecked(),
            'anti_aliasing': self.anti_aliasing.isChecked(),
            'high_quality': self.high_quality.isChecked()
        }

    def set_settings(self, settings):
        """
        设置导出参数

        Args:
            settings (dict): 导出设置字典
        """
        if 'width' in settings:
            self.width_spinbox.setValue(settings['width'])
        if 'height' in settings:
            self.height_spinbox.setValue(settings['height'])
        if 'include_agvs' in settings:
            self.include_agvs.setChecked(settings['include_agvs'])
        if 'include_planned_paths' in settings:
            self.include_planned_paths.setChecked(settings['include_planned_paths'])
        if 'include_active_paths' in settings:
            self.include_active_paths.setChecked(settings['include_active_paths'])
        if 'include_info' in settings:
            self.include_info.setChecked(settings['include_info'])
        if 'anti_aliasing' in settings:
            self.anti_aliasing.setChecked(settings['anti_aliasing'])
        if 'high_quality' in settings:
            self.high_quality.setChecked(settings['high_quality'])

    def get_estimated_file_size(self):
        """
        估算导出文件大小

        Returns:
            str: 估算的文件大小描述
        """
        width = self.width_spinbox.value()
        height = self.height_spinbox.value()

        # 简单的文件大小估算（基于像素数量）
        pixel_count = width * height

        if pixel_count < 2_000_000:  # < 2MP
            return "约 1-3 MB"
        elif pixel_count < 8_000_000:  # < 8MP
            return "约 3-8 MB"
        elif pixel_count < 33_000_000:  # < 33MP (8K)
            return "约 8-20 MB"
        else:
            return "约 20+ MB"

    def validate_settings(self):
        """
        验证设置的有效性

        Returns:
            tuple: (是否有效, 错误消息列表)
        """
        errors = []

        width = self.width_spinbox.value()
        height = self.height_spinbox.value()

        if width < 800:
            errors.append("宽度不能小于800像素")
        if height < 600:
            errors.append("高度不能小于600像素")
        if width > 20000:
            errors.append("宽度不能大于20000像素")
        if height > 20000:
            errors.append("高度不能大于20000像素")

        # 检查宽高比是否合理
        aspect_ratio = width / height
        if aspect_ratio < 0.5 or aspect_ratio > 3.0:
            errors.append("宽高比建议在0.5到3.0之间")

        return len(errors) == 0, errors

    @classmethod
    def get_default_settings(cls):
        """
        获取默认导出设置

        Returns:
            dict: 默认设置字典
        """
        return {
            'width': 3840,
            'height': 2160,
            'include_agvs': True,
            'include_planned_paths': True,
            'include_active_paths': True,
            'include_info': False,
            'anti_aliasing': True,
            'high_quality': True
        }

    @classmethod
    def quick_export_dialog(cls, parent=None, preset="4K"):
        """
        快速导出对话框（预设参数）

        Args:
            parent: 父窗口
            preset: 预设名称

        Returns:
            dict or None: 导出设置或None（如果取消）
        """
        dialog = cls(parent)

        # 设置预设
        if preset in cls.RESOLUTION_PRESETS:
            index = list(cls.RESOLUTION_PRESETS.keys()).index(preset)
            dialog.resolution_combo.setCurrentIndex(index)

        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_settings()
        return None