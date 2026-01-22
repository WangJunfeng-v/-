import pygame
from config import GRID_X_OFFSET, GRID_Y_OFFSET, CELL_SIZE


class Particle:
    """粒子类 - 游戏中的最小单位"""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.target_x = x  # 目标x位置
        self.target_y = y  # 目标y位置
        self.color = color
        self.falling = False
        self.animating = False  # 是否正在动画
        self.animation_progress = 0.0  # 动画进度 0.0-1.0
    
    def set_target(self, target_x, target_y):
        """设置目标位置，开始动画"""
        if self.x != target_x or self.y != target_y:
            # 如果粒子正在动画，需要从当前动画位置继续
            if self.animating:
                # 更新当前位置到当前动画位置，确保轨迹连续
                current_x = self.get_draw_x()
                current_y = self.get_draw_y()
                self.x = current_x
                self.y = current_y
            self.target_x = target_x
            self.target_y = target_y
            self.animating = True
            self.animation_progress = 0.0
    
    def update_animation(self, speed=0.2):
        """更新动画进度"""
        if self.animating:
            self.animation_progress += speed
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
                return True  # 动画完成
        return False  # 动画未完成
    
    def get_draw_x(self):
        """获取绘制时的x位置（考虑动画）"""
        if self.animating:
            return self.x + (self.target_x - self.x) * self.animation_progress
        return self.x
    
    def get_draw_y(self):
        """获取绘制时的y位置（考虑动画）"""
        if self.animating:
            return self.y + (self.target_y - self.y) * self.animation_progress
        return self.y
    
    def draw(self, screen):
        """绘制粒子"""
        draw_x = self.get_draw_x()
        draw_y = self.get_draw_y()
        # 粒子几乎填满整个格子
        rect = pygame.Rect(
            GRID_X_OFFSET + draw_x * CELL_SIZE,
            GRID_Y_OFFSET + draw_y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, self.color, rect)
