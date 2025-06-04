"""
简化的主窗口模块
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                             QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                             QApplication)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QTimer

from ui.simulation_widget import SimulationWidget
from ui.control_panel import ControlPanel


class MainWindow(QMainWindow):
    """AGV仿真系统主窗口 - 简化版"""

    DEFAULT_WIDTH = 1750
    DEFAULT_HEIGHT = 1050
    MIN_WIDTH = 1200
    MIN_HEIGHT = 800

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._create_widgets()
        self._create_menu_bar()
        self._create_status_bar()
        self._setup_layout()
        self._setup_timer()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("RCS-Lite AGV智能仿真系统 v6.2 ")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

    def _create_widgets(self):
        """创建主要组件"""
        self.simulation_widget = SimulationWidget()
        self.control_panel = ControlPanel(self.simulation_widget)

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = self._create_file_menu(menubar)
        # 视图菜单
        view_menu = self._create_view_menu(menubar)
        # AGV菜单
        agv_menu = self._create_agv_menu(menubar)
        # 帮助菜单
        help_menu = self._create_help_menu(menubar)

    def _create_file_menu(self, menubar):
        """创建文件菜单"""
        file_menu = menubar.addMenu('文件(&F)')

        # 退出
        exit_action = QAction('退出(&Q)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        return file_menu

    def _create_view_menu(self, menubar):
        """创建视图菜单"""
        view_menu = menubar.addMenu('视图(&V)')

        # 缩放控制
        zoom_in_action = QAction('放大(&I)', self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.control_panel._zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction('缩小(&O)', self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.control_panel._zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_view_action = QAction('重置视图(&R)', self)
        reset_view_action.setShortcut(QKeySequence('R'))
        reset_view_action.triggered.connect(self.control_panel._reset_view)
        view_menu.addAction(reset_view_action)

        view_menu.addSeparator()

        # 全屏
        fullscreen_action = QAction('全屏(&F)', self)
        fullscreen_action.setShortcut(QKeySequence.FullScreen)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        return view_menu

    def _create_agv_menu(self, menubar):
        """创建AGV菜单"""
        agv_menu = menubar.addMenu('AGV(&A)')

        # 添加AGV
        add_agv_action = QAction('添加AGV(&A)', self)
        add_agv_action.setShortcut(QKeySequence('Ctrl+A'))
        add_agv_action.triggered.connect(self.control_panel._add_agv)
        agv_menu.addAction(add_agv_action)

        agv_menu.addSeparator()

        # 任务控制
        auto_task_action = QAction('自动随机任务(&T)', self)
        auto_task_action.setShortcut(QKeySequence('Ctrl+T'))
        auto_task_action.triggered.connect(self.control_panel._start_auto_tasks)
        agv_menu.addAction(auto_task_action)

        stop_all_action = QAction('停止所有AGV(&S)', self)
        stop_all_action.setShortcut(QKeySequence('Ctrl+S'))
        stop_all_action.triggered.connect(self.control_panel._stop_all_agvs)
        agv_menu.addAction(stop_all_action)

        agv_menu.addSeparator()

        # 碰撞检测
        collision_action = QAction('碰撞检测(&D)', self)
        collision_action.setCheckable(True)
        collision_action.setChecked(True)
        collision_action.triggered.connect(self._toggle_collision_from_menu)
        agv_menu.addAction(collision_action)

        self.collision_action = collision_action

        return agv_menu

    def _create_help_menu(self, menubar):
        """创建帮助菜单"""
        help_menu = menubar.addMenu('帮助(&H)')

        # 使用说明
        usage_action = QAction('使用说明(&U)', self)
        usage_action.setShortcut(QKeySequence.HelpContents)
        usage_action.triggered.connect(self._show_usage)
        help_menu.addAction(usage_action)

        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        return help_menu

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('就绪')

    def _setup_layout(self):
        """设置布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.simulation_widget)
        splitter.addWidget(self.control_panel)
        splitter.setSizes([int(self.DEFAULT_WIDTH * 0.8), int(self.DEFAULT_WIDTH * 0.2)])

        layout = QHBoxLayout(central_widget)
        layout.addWidget(splitter)
        layout.setContentsMargins(0, 0, 0, 0)

    def _setup_timer(self):
        """设置定时器"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)

    # =============================================================================
    # 菜单动作方法
    # =============================================================================

    def _toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
            self.status_bar.showMessage('退出全屏模式', 2000)
        else:
            self.showFullScreen()
            self.status_bar.showMessage('进入全屏模式，按F11退出', 2000)

    def _toggle_collision_from_menu(self, checked):
        """从菜单切换碰撞检测"""
        self.control_panel.collision_check.setChecked(checked)
        self.simulation_widget.set_collision_detection(checked)

    def _show_usage(self):
        """显示使用说明"""
        usage_text = """AGV智能仿真系统使用说明:

地图操作:
• 滚轮: 缩放地图
• 右键拖拽: 平移地图
• 双击: 重置视图
• 左键点击节点: 手动控制AGV移动

键盘快捷键:
• +/-: 放大/缩小
• R: 重置视图
• F11: 全屏切换

AGV控制:
• 添加AGV: 在指定节点创建新AGV
• 点击AGV: 查看和编辑AGV属性
• 发送任务: 为AGV规划路径到目标节点
• 自动任务: 为所有AGV分配随机目标
• 停止所有: 立即停止所有AGV移动

节点显示:
• 灰白色方块: 普通节点
• 绿色方块: 上货点(PP)
• 红色方块: 下货点(AP)
• 金色方块: 充电点(CP)
• 橙色方块: 管控区节点

大小规格:
• 节点: 24×24 像素 (显示完整5字符节点名)
• AGV: 20×20 像素
• 路径: 4px 宽度
• 箭头: 10×4 像素"""

        QMessageBox.information(self, "使用说明", usage_text)

    def _show_about(self):
        """显示关于信息"""
        about_text = """RCS-Lite AGV智能仿真系统

版本: v6.2 

功能特性:
• 数据库地图自动加载
• 智能路径规划(Dijkstra & A*)
• AGV间碰撞检测与避让
• 管控区橙色显示
• 完整5字符节点名显示

技术规格:
• 节点大小: 24×24 像素
• AGV大小: 20×20 像素
• 路径宽度: 4px
• 箭头尺寸: 10×4 像素
• 刷新频率: ~60 FPS
• 界面框架: PyQt5

"""

        QMessageBox.about(self, "关于", about_text)

    # =============================================================================
    # 状态更新方法
    # =============================================================================

    def _update_status(self):
        """更新状态栏"""
        try:
            map_info = self.simulation_widget.get_map_info()
            agv_count = map_info['agv_count']
            node_count = map_info['node_count']

            status_text = f"节点: {node_count} | AGV: {agv_count} | {map_info['source']}"
            self.status_bar.showMessage(status_text)

        except Exception:
            self.status_bar.showMessage("状态更新失败")

    # =============================================================================
    # 窗口事件方法
    # =============================================================================

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出AGV仿真系统吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            if hasattr(self.simulation_widget, 'timer'):
                self.simulation_widget.timer.stop()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """全局键盘事件处理"""
        if event.key() == Qt.Key_F11:
            self._toggle_fullscreen()
        else:
            self.simulation_widget.keyPressEvent(event)

    # =============================================================================
    # 公共接口方法
    # =============================================================================

    def get_simulation_widget(self):
        """获取仿真组件"""
        return self.simulation_widget

    def get_control_panel(self):
        """获取控制面板"""
        return self.control_panel