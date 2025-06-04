# RCS-Lite AGV智能仿真系统 v6.0

## 项目概述

这是一个基于PyQt5的AGV智能仿真系统，支持直接从SQLite数据库读取地图数据，提供实时路径规划、碰撞检测和高清地图导出功能。

## 项目结构

```
agv_simulation_system/
├── main.py                          # 主入口文件
├── Map.db                          # SQLite数据库文件（地图数据）
├── README.md                       # 项目说明文件
├── requirements.txt               # 依赖包列表
├── models/                        # 数据模型层
│   ├── __init__.py
│   ├── node.py                    # 节点模型（缩小尺寸版本）
│   ├── path.py                    # 路径模型
│   └── agv.py                     # AGV模型
├── algorithms/                    # 算法层
│   ├── __init__.py
│   └── path_planner.py           # 路径规划算法（Dijkstra & A*）
├── data/                          # 数据层
│   ├── __init__.py
│   └── map_loader.py             # 地图加载器（数据库 & Excel）
├── ui/                           # 用户界面层
│   ├── __init__.py
│   ├── main_window.py            # 主窗口（带菜单栏和状态栏）
│   ├── simulation_widget.py     # 仿真显示组件
│   ├── control_panel.py         # 控制面板（优化布局，支持滚动）
│   ├── export_dialog.py         # 导出设置对话框
│   └── agv_property_dialog.py   # AGV属性编辑对话框
└── utils/                        # 工具层
    └── __init__.py
```

## 关键改进

### 1. 节点尺寸优化
- 节点宽度和高度从25px缩小到15px
- 路径宽度从8px调整到6px
- 更好地凸显路径，提升视觉效果

### 2. 刷新机制详解
```python
# 定时器设置：16ms = 62.5 FPS
self.timer = QTimer(self)
self.timer.timeout.connect(self._update_simulation)
self.timer.start(16)  # 约60FPS
```

**刷新流程：**
1. **QTimer** 每16ms触发一次
2. **update_simulation()** 更新AGV位置和状态
3. **self.update()** 触发Qt重绘事件
4. **paintEvent()** 完全重绘所有元素

### 3. 模块化架构
- **分层设计**：模型层、算法层、数据层、UI层分离
- **低耦合**：各模块间依赖关系清晰
- **易维护**：每个模块职责单一，便于独立修改和测试

## 主要功能

### 地图管理
- 直接连接SQLite数据库读取地图数据
- 支持Excel文件导入
- 自动识别节点类型（PP/CP/AP）
- 智能地图缩放和坐标转换

### AGV仿真
- 多AGV协同仿真
- 实时碰撞检测和避让
- 支持手动和自动路径规划
- 动态状态显示和监控
- **点击AGV查看和编辑属性**
- **支持AGV删除功能**
- **AGV属性实时编辑（位置、速度、颜色等）**

### 路径规划
- Dijkstra最短路径算法
- A*启发式搜索算法
- 考虑节点占用状态的成本计算
- 支持有向图和双向路径

### 可视化
- 实时动画显示
- 多种节点类型标识
- 路径方向指示
- AGV状态可视化

### 导出功能
- 支持1080p到8K分辨率
- 可选择导出内容
- 高质量抗锯齿渲染
- 多种图像格式支持

## 数据库结构

### T_GraphPoint表
```sql
CREATE TABLE T_GraphPoint (
    id INTEGER,
    canRotate INTEGER,
    pointId TEXT PRIMARY KEY,
    x REAL,
    y REAL
);
```

### T_GraphEdge表
```sql
CREATE TABLE T_GraphEdge (
    id INTEGER,
    beginAngle REAL,
    beginPointId TEXT,
    endAngle REAL,
    endPointId TEXT,
    passAngles TEXT,
    weight REAL
);
```

## 安装和运行

### 环境要求
- Python 3.7+
- PyQt5
- pandas
- sqlite3（Python内置）

### 安装依赖
```bash
pip install PyQt5 pandas
```

### 运行程序
```bash
python main.py
```

## 使用指南

### 基本操作
- **滚轮**：缩放地图
- **右键拖拽**：平移地图
- **双击**：重置视图
- **左键点击节点**：手动控制AGV移动
- **左键点击AGV**：查看和编辑AGV属性

### 键盘快捷键
- **+/-**：放大/缩小地图
- **R**：重置视图
- **空格**：居中视图
- **Ctrl+E**：快速导出4K地图
- **F11**：全屏切换
- **Delete**：删除选中的AGV

### AGV管理
1. 点击"添加AGV"创建新的AGV
2. 选择AGV和目标节点
3. 选择路径规划算法
4. 点击"发送任务"开始移动
5. **点击AGV可查看详细属性和进行编辑**
6. **在控制面板中可删除选中的AGV**

### 批量操作
- **自动随机任务**：为所有AGV分配随机目标
- **停止所有AGV**：立即停止所有移动
- **碰撞检测开关**：控制AGV间避让行为

## 扩展开发

### 添加新的算法
在`algorithms/`目录下创建新的算法模块，实现相应的接口。

### 自定义节点类型
在`models/node.py`中扩展节点类型和相应的视觉表示。

### 新增数据源
在`data/map_loader.py`中添加新的数据加载方法。

### UI组件定制
在`ui/`目录下创建新的界面组件，遵循现有的设计模式。

## 性能优化

- **绘制优化**：使用QPainter的抗锯齿和高质量渲染
- **更新优化**：仅在必要时触发重绘
- **内存管理**：限制日志行数，避免内存泄漏
- **计算优化**：使用高效的数据结构和算法

## 版本历史

- **v6.1**：优化版本
  - 控制面板布局优化，支持滚动显示
  - 新增AGV属性编辑对话框，支持实时编辑AGV属性
  - 新增AGV删除功能
  - 支持点击AGV查看详细属性
  - 完善键盘快捷键支持
- **v6.0**：数据库直连版本，节点尺寸优化，完整模块化重构
- **v5.0**：Excel地图+缩放+高清导出版本
- 更早版本：基础功能实现

## 贡献指南

1. Fork本项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues
- 邮箱：[开发团队邮箱]

---

**注意**：本系统设计用于教学和研究目的，在生产环境中使用需要进一步的测试和验证。