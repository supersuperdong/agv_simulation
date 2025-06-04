"""
简化的控制面板模块
"""

import random
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QCheckBox, QTextEdit,
                             QGroupBox, QMessageBox, QScrollArea)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer


class ControlPanel(QWidget):
    """AGV仿真控制面板 - 简化版"""

    def __init__(self, simulation_widget, parent=None):
        super().__init__(parent)
        self.simulation_widget = simulation_widget
        self._setup_ui()
        self._setup_timer()
        self._update_node_lists()

    def _setup_ui(self):
        """设置用户界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 创建滚动内容部件
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)

        # 创建各个控制组
        scroll_layout.addWidget(self._create_title())
        scroll_layout.addWidget(self._create_map_group())
        scroll_layout.addWidget(self._create_agv_group())
        scroll_layout.addWidget(self._create_batch_group())
        scroll_layout.addWidget(self._create_info_group())
        scroll_layout.addWidget(self._create_log_group())

        # 添加伸缩项
        scroll_layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _create_title(self):
        """创建标题"""
        title_label = QLabel("智能控制面板")
        title_label.setFont(QFont('Arial', 14, QFont.Bold))
        return title_label

    def _create_map_group(self):
        """创建地图管理组"""
        map_group = QGroupBox("地图管理")
        map_layout = QVBoxLayout(map_group)

        # 地图控制按钮
        map_control_layout = QHBoxLayout()

        self.zoom_in_button = QPushButton("放大 (+)")
        self.zoom_in_button.clicked.connect(self._zoom_in)
        map_control_layout.addWidget(self.zoom_in_button)

        self.zoom_out_button = QPushButton("缩小 (-)")
        self.zoom_out_button.clicked.connect(self._zoom_out)
        map_control_layout.addWidget(self.zoom_out_button)

        self.reset_view_button = QPushButton("重置视图")
        self.reset_view_button.clicked.connect(self._reset_view)
        map_control_layout.addWidget(self.reset_view_button)

        map_layout.addLayout(map_control_layout)

        return map_group

    def _create_agv_group(self):
        """创建AGV管理组"""
        agv_group = QGroupBox("AGV管理")
        agv_layout = QVBoxLayout(agv_group)

        # 添加AGV
        add_agv_layout = QHBoxLayout()

        self.add_agv_button = QPushButton("添加AGV")
        self.add_agv_button.clicked.connect(self._add_agv)
        add_agv_layout.addWidget(self.add_agv_button)

        add_agv_layout.addWidget(QLabel("起始节点:"))
        self.start_node_combo = QComboBox()
        self.start_node_combo.setEditable(True)
        add_agv_layout.addWidget(self.start_node_combo)

        agv_layout.addLayout(add_agv_layout)

        # AGV任务分配
        task_layout = QVBoxLayout()

        # AGV选择
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择AGV:"))
        self.agv_selector = QComboBox()
        select_layout.addWidget(self.agv_selector)
        task_layout.addLayout(select_layout)

        # 目标节点
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标节点:"))
        self.target_node_combo = QComboBox()
        self.target_node_combo.setEditable(True)
        target_layout.addWidget(self.target_node_combo)
        task_layout.addLayout(target_layout)

        # 算法选择
        algorithm_layout = QHBoxLayout()
        algorithm_layout.addWidget(QLabel("算法:"))
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItems(["dijkstra", "a_star"])
        algorithm_layout.addWidget(self.algorithm_selector)
        task_layout.addLayout(algorithm_layout)

        # 发送任务按钮
        self.send_task_button = QPushButton("发送任务")
        self.send_task_button.clicked.connect(self._send_task)
        task_layout.addWidget(self.send_task_button)

        # 删除AGV按钮
        self.delete_agv_button = QPushButton("删除AGV")
        self.delete_agv_button.clicked.connect(self._delete_agv)
        self.delete_agv_button.setStyleSheet("QPushButton { background-color: #ff6666; color: white; }")
        task_layout.addWidget(self.delete_agv_button)

        agv_layout.addLayout(task_layout)
        return agv_group

    def _create_batch_group(self):
        """创建批量任务组"""
        batch_group = QGroupBox("批量任务")
        batch_layout = QVBoxLayout(batch_group)

        # 自动任务按钮
        self.auto_task_button = QPushButton("自动随机任务")
        self.auto_task_button.clicked.connect(self._start_auto_tasks)
        batch_layout.addWidget(self.auto_task_button)

        # 停止所有按钮
        self.stop_all_button = QPushButton("停止所有AGV")
        self.stop_all_button.clicked.connect(self._stop_all_agvs)
        batch_layout.addWidget(self.stop_all_button)

        # 碰撞检测开关
        self.collision_check = QCheckBox("启用碰撞检测")
        self.collision_check.setChecked(True)
        self.collision_check.stateChanged.connect(self._toggle_collision_detection)
        batch_layout.addWidget(self.collision_check)

        return batch_group

    def _create_info_group(self):
        """创建信息组"""
        info_group = QGroupBox("操作说明")
        info_layout = QVBoxLayout(info_group)

        info_font = QFont()
        info_font.setPointSize(8)

        instructions = [
            "• 鼠标: 滚轮缩放, 右键拖拽, 双击重置",
            "• 点击节点: 手动移动AGV",
            "• 点击AGV: 查看/编辑属性",
            "• 键盘: +/-缩放, R重置, Ctrl+E导出",
            "• 橙色方块: 管控区节点",
            "• 节点: 24×24, AGV: 20×20, 路径: 4px"  # 更新尺寸信息
        ]

        for instruction in instructions:
            label = QLabel(instruction)
            label.setFont(info_font)
            info_layout.addWidget(label)

        return info_group

    def _create_log_group(self):
        """创建状态日志组"""
        log_group = QGroupBox("状态日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        return log_group

    def _setup_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(1000)

    # =============================================================================
    # 地图管理方法
    # =============================================================================

    def _zoom_in(self):
        """放大地图"""
        old_scale = self.simulation_widget.zoom_scale
        self.simulation_widget._zoom_in()
        new_scale = self.simulation_widget.zoom_scale
        if new_scale != old_scale:
            self._log_message(f"地图放大到 {new_scale:.1f}x")

    def _zoom_out(self):
        """缩小地图"""
        old_scale = self.simulation_widget.zoom_scale
        self.simulation_widget._zoom_out()
        new_scale = self.simulation_widget.zoom_scale
        if new_scale != old_scale:
            self._log_message(f"地图缩小到 {new_scale:.1f}x")

    def _reset_view(self):
        """重置视图"""
        self.simulation_widget.reset_view()
        self._log_message("视图已重置")

    # =============================================================================
    # AGV管理方法
    # =============================================================================

    def _add_agv(self):
        """添加AGV"""
        start_node_text = self.start_node_combo.currentText()
        start_node_id = start_node_text if start_node_text in self.simulation_widget.nodes else None

        agv = self.simulation_widget.add_agv(start_node_id)
        if agv:
            self._log_message(f"AGV #{agv.id} 已添加到节点 {agv.current_node.id}")
            self._update_agv_list()
        else:
            self._log_message("无法添加AGV: 节点已被占用或所有节点均已占用")

    def _send_task(self):
        """发送任务给选中的AGV"""
        agv_text = self.agv_selector.currentText()
        if not agv_text or not agv_text.startswith("AGV #"):
            self._log_message("请先选择一个AGV")
            return

        try:
            agv_id = int(agv_text.split('#')[1])
        except (IndexError, ValueError):
            self._log_message("AGV选择格式错误")
            return

        target_node_text = self.target_node_combo.currentText()
        if not target_node_text or target_node_text not in self.simulation_widget.nodes:
            self._log_message("请选择有效的目标节点")
            return

        algorithm = self.algorithm_selector.currentText()
        success = self.simulation_widget.send_agv_to_target(agv_id, target_node_text, algorithm)

        if success:
            self._log_message(f"AGV #{agv_id} 开始前往节点 {target_node_text}")
        else:
            self._log_message(f"无法为AGV #{agv_id} 规划路径")

    def _delete_agv(self):
        """删除选中的AGV"""
        agv_text = self.agv_selector.currentText()
        if not agv_text or not agv_text.startswith("AGV #"):
            self._log_message("请先选择一个AGV")
            return

        try:
            agv_id = int(agv_text.split('#')[1])
        except (IndexError, ValueError):
            self._log_message("AGV选择格式错误")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除AGV #{agv_id} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.simulation_widget.remove_agv(agv_id):
                self._log_message(f"AGV #{agv_id} 已删除")
                self._update_agv_list()
            else:
                self._log_message(f"删除AGV #{agv_id} 失败")

    def _start_auto_tasks(self):
        """开始自动随机任务"""
        if not self.simulation_widget.agvs:
            for i in range(3):
                self.simulation_widget.add_agv()
            self._update_agv_list()
            self._log_message("已自动添加3个AGV")

        success_count = 0
        for agv in self.simulation_widget.agvs:
            if not agv.moving:
                available_nodes = list(self.simulation_widget.nodes.keys())
                if available_nodes:
                    target_id = random.choice(available_nodes)
                    algorithm = random.choice(['dijkstra', 'a_star'])

                    if self.simulation_widget.send_agv_to_target(agv.id, target_id, algorithm):
                        success_count += 1

        if success_count > 0:
            self._log_message(f"已为 {success_count} 个AGV分配随机任务")
        else:
            self._log_message("未能分配任何随机任务")

    def _stop_all_agvs(self):
        """停止所有AGV"""
        agv_count = len(self.simulation_widget.agvs)
        self.simulation_widget.stop_all_agvs()

        if agv_count > 0:
            self._log_message(f"已停止 {agv_count} 个AGV")
        else:
            self._log_message("没有AGV在运行")

    def _toggle_collision_detection(self, state):
        """切换碰撞检测开关"""
        enabled = (state == Qt.Checked)
        self.simulation_widget.set_collision_detection(enabled)
        self._log_message(f"碰撞检测已{'开启' if enabled else '关闭'}")

    # =============================================================================
    # UI更新方法
    # =============================================================================

    def _update_ui(self):
        """更新UI状态"""
        self._update_agv_list()

    def _update_node_lists(self):
        """更新节点选择列表"""
        self.start_node_combo.clear()
        self.target_node_combo.clear()

        node_ids = sorted(self.simulation_widget.nodes.keys(), key=str)

        for node_id in node_ids:
            node_id_str = str(node_id)
            self.start_node_combo.addItem(node_id_str)
            self.target_node_combo.addItem(node_id_str)

    def _update_agv_list(self):
        """更新AGV选择列表"""
        current_text = self.agv_selector.currentText()

        self.agv_selector.clear()
        for agv in self.simulation_widget.agvs:
            self.agv_selector.addItem(f"AGV #{agv.id}")

        if current_text:
            index = self.agv_selector.findText(current_text)
            if index >= 0:
                self.agv_selector.setCurrentIndex(index)

    # =============================================================================
    # 辅助方法
    # =============================================================================

    def _log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # 限制日志行数
        document = self.log_text.document()
        if document.blockCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 20)
            cursor.removeSelectedText()

    def get_simulation_widget(self):
        """获取仿真组件引用"""
        return self.simulation_widget