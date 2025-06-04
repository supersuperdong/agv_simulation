"""
AGV模型类 - 优化版本
"""

import math
import random
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QRectF


class AGV:
    """AGV自动导引车 - 优化版本"""

    def __init__(self, agv_id, start_node):
        # 基本属性
        self.id = agv_id
        self.name = f"AGV-{agv_id}"

        # 位置属性
        self.current_node = start_node
        self.target_node = None
        self.x = start_node.x
        self.y = start_node.y

        # 外观属性
        self.width = 24
        self.height = 24
        self.color = QColor(255, 140, 0)

        # 运动属性
        self.angle = 0
        self.target_angle = 0
        self.speed = 2
        self.moving = False

        # 路径属性
        self.path = []
        self.path_index = 0
        self.task_target = None

        # 状态属性
        self.status = "待机"
        self.waiting = False
        self.collision_buffer = 25
        self.wait_counter = 0
        self.priority = 5

        # 占用起始节点
        start_node.occupied_by = self.id

    def set_path(self, path):
        """设置路径"""
        if len(path) > 1:
            self.path = path
            self.path_index = 0
            self.task_target = path[-1]
            self.status = f"前往节点 {self.task_target}"
            self.waiting = False
            self.wait_counter = 0

    def set_target(self, node):
        """设置移动目标"""
        if node.id not in self.current_node.connections:
            return False

        if node.occupied_by is not None and node.occupied_by != self.id:
            self.status = f"等待节点 {node.id}"
            self.waiting = True
            return False

        self.target_node = node
        node.reserved_by = self.id
        node.reservation_time = 50

        # 计算朝向
        dx = node.x - self.x
        dy = node.y - self.y
        self.target_angle = self._normalize_angle(math.degrees(math.atan2(dy, dx)))

        self.moving = True
        self.waiting = False
        self.status = f"移动至节点 {node.id}"
        return True

    def move(self, nodes, other_agvs):
        """移动逻辑"""
        if not self.moving or not self.target_node:
            self._try_next_path_step(nodes)
            return

        # 检查目标节点占用
        if (self.target_node.occupied_by is not None and
            self.target_node.occupied_by != self.id):
            self.waiting = True
            self.wait_counter += 1
            self.status = f"等待节点 {self.target_node.id}"
            return

        # 旋转到目标角度
        if self._rotate_to_target():
            # 移动到目标
            self._move_to_target(other_agvs)

    def _try_next_path_step(self, nodes):
        """尝试执行路径中的下一步"""
        if not self.path or self.path_index + 1 >= len(self.path):
            return

        next_node_id = self.path[self.path_index + 1]
        if next_node_id in nodes:
            next_node = nodes[next_node_id]
            if next_node.occupied_by is None or next_node.occupied_by == self.id:
                if self.set_target(next_node):
                    self.wait_counter = 0
            else:
                self.waiting = True
                self.wait_counter += 1

    def _rotate_to_target(self):
        """旋转到目标角度"""
        self.angle = self._normalize_angle(self.angle)
        self.target_angle = self._normalize_angle(self.target_angle)

        diff = self.target_angle - self.angle
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        if abs(diff) <= 3:
            self.angle = self.target_angle
            return True

        rotation_step = 3
        self.angle += rotation_step if diff > 0 else -rotation_step
        self.angle = self._normalize_angle(self.angle)
        return False

    def _move_to_target(self, other_agvs):
        """移动到目标节点"""
        dx = self.target_node.x - self.x
        dy = self.target_node.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.speed:
            self._arrive_at_target()
        else:
            # 检查碰撞
            future_x = self.x + self.speed * dx / distance
            future_y = self.y + self.speed * dy / distance

            if not self._check_collision_at(future_x, future_y, other_agvs):
                self.x = future_x
                self.y = future_y
                self.waiting = False
                self.wait_counter = 0
            else:
                self.waiting = True
                self.wait_counter += 1
                self.status = "避让其他AGV"

    def _arrive_at_target(self):
        """到达目标节点"""
        # 释放当前节点
        if self.current_node and self.current_node.occupied_by == self.id:
            self.current_node.occupied_by = None

        # 更新位置
        self.x = self.target_node.x
        self.y = self.target_node.y
        self.current_node = self.target_node
        self.target_node = None
        self.moving = False

        # 占用新节点
        self.current_node.occupied_by = self.id
        if self.current_node.reserved_by == self.id:
            self.current_node.reserved_by = None

        # 更新路径状态
        if self.path:
            self.path_index += 1
            if self.path_index >= len(self.path) - 1:
                self.status = f"已到达 {self.current_node.id}"
                self.path = []
                self.path_index = 0
                self.task_target = None
            else:
                self.status = f"路径中 {self.current_node.id}"

    def _check_collision_at(self, x, y, other_agvs):
        """检查指定位置是否碰撞"""
        for agv in other_agvs:
            if agv.id == self.id:
                continue
            distance = math.sqrt((x - agv.x)**2 + (y - agv.y)**2)
            if distance < self.collision_buffer:
                return True
        return False

    def _normalize_angle(self, angle):
        """角度归一化"""
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle

    def stop(self, nodes):
        """停止AGV"""
        if self.moving:
            # 找最近节点
            closest_node = min(nodes.values(),
                             key=lambda n: (n.x - self.x)**2 + (n.y - self.y)**2)

            if closest_node and (closest_node.occupied_by is None or
                               closest_node.occupied_by == self.id):
                # 释放当前节点
                if self.current_node and self.current_node.occupied_by == self.id:
                    self.current_node.occupied_by = None

                # 移动到最近节点
                self.current_node = closest_node
                self.x = closest_node.x
                self.y = closest_node.y
                closest_node.occupied_by = self.id

        # 重置状态
        self.moving = False
        self.target_node = None
        self.path = []
        self.path_index = 0
        self.task_target = None
        self.status = "已停止"
        self.waiting = False
        self.wait_counter = 0

    def draw(self, painter):
        """绘制AGV"""
        painter.save()
        painter.translate(int(self.x), int(self.y))
        painter.rotate(self.angle)

        # 绘制主体
        color = self.color.lighter(140) if self.waiting else self.color
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(-self.width//2, -self.height//2, self.width, self.height)

        # 绘制方向指示（调整大小适应20×20的AGV）
        front_size = 6  # 放大方向指示
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawRect(self.width//2 - front_size, -front_size//2, front_size, front_size)

        painter.restore()

        # 绘制ID（调整字体大小适应20×20的AGV）
        painter.setFont(QFont('Arial', 8, QFont.Bold))  # 字体放大适配20×20 AGV
        painter.setPen(QPen(Qt.white))
        text_rect = QRectF(self.x - self.width//2, self.y - self.height//2,
                          self.width, self.height)
        painter.drawText(text_rect, Qt.AlignCenter, f"#{self.id}")

        # 等待状态指示
        if self.waiting:
            painter.setBrush(QBrush(Qt.red))
            painter.setPen(QPen(Qt.red))
            painter.drawEllipse(int(self.x + self.width//2 - 4),
                              int(self.y - self.height//2 + 4), 8, 8)  # 指示点也放大

    def destroy(self):
        """清理资源"""
        if self.current_node and self.current_node.occupied_by == self.id:
            self.current_node.occupied_by = None
        if self.target_node and self.target_node.reserved_by == self.id:
            self.target_node.reserved_by = None
        self.path = []
        self.status = "已销毁"