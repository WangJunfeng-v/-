import pygame
import random
from config import (
    BLOCK_SIZE, CELL_SIZE, GRID_WIDTH, GRID_HEIGHT,
    GRID_X_OFFSET, GRID_Y_OFFSET, WHITE, PARTICLE_COLORS
)


# 方块形状模板
SHAPE_TEMPLATES = [
    # 直线（横向）
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    # 直线（纵向）
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    # L形
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    # 反L形
    [(1, 0), (1, 1), (1, 2), (0, 2)],
    # T形
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    # 倒T形
    [(0, 1), (1, 1), (2, 1), (1, 0)],
    # 方形
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    # Z形
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    # 反Z形
    [(0, 1), (1, 1), (1, 0), (2, 0)],
    # 小方块（2个）
    [(0, 0), (1, 0)],
    # 小方块（3个横向）
    [(0, 0), (1, 0), (2, 0)],
    # 小方块（3个纵向）
    [(0, 0), (0, 1), (0, 2)],
    # 随机散点（5个）
    [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1)],
    # 大L形
    [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    # 十字形
    [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
]


class Block:
    """方块类 - 由多个大方块组成，每个大方块包含多个粒子"""
    
    def __init__(self):
        # 从5种固定颜色中随机选择
        self.color = random.choice(PARTICLE_COLORS)
        
        # 生成随机形状（由多个大方块组成）
        self.particles = self.generate_random_shape()
        
        # 方块在网格中的位置（以粒子为单位）
        # 起始位置居中，y=0表示顶部
        # 计算形状的宽度来居中
        if self.particles:
            min_x = min(px for px, py in self.particles)
            max_x = max(px for px, py in self.particles)
            shape_width = max_x - min_x + 1
            # 居中放置，考虑最小x偏移
            self.x = (GRID_WIDTH - shape_width) // 2 - min_x
        else:
            self.x = GRID_WIDTH // 2
        self.y = 0
    
    def generate_random_shape(self):
        """生成随机形状，由多个大方块组成"""
        # 随机选择一个形状
        self.shape_template = random.choice(SHAPE_TEMPLATES)
        
        # 为每个大方块单元生成粒子
        particles = []
        for unit_x, unit_y in self.shape_template:
            # 每个单元是BLOCK_SIZE x BLOCK_SIZE的大方块
            for px in range(BLOCK_SIZE):
                for py in range(BLOCK_SIZE):
                    # 计算粒子在整体形状中的相对位置
                    particle_x = unit_x * BLOCK_SIZE + px
                    particle_y = unit_y * BLOCK_SIZE + py
                    particles.append((particle_x, particle_y))
        
        return particles
    
    def get_particle_positions(self):
        """获取方块中所有粒子在网格中的实际位置"""
        positions = []
        for px, py in self.particles:
            grid_x = self.x + px
            grid_y = self.y + py
            positions.append((grid_x, grid_y))
        return positions
    
    def move(self, dx, dy):
        """移动方块（以粒子为单位）"""
        self.x += dx
        self.y += dy
    
    def draw(self, screen):
        """绘制方块（只显示大方块单元，不显示内部粒子）"""
        # 只绘制大方块单元
        for unit_x, unit_y in self.shape_template:
            # 计算大方块在网格中的位置
            grid_x = self.x + unit_x * BLOCK_SIZE
            grid_y = self.y + unit_y * BLOCK_SIZE
            
            # 只绘制在网格范围内的大方块
            if (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT and
                grid_x + BLOCK_SIZE <= GRID_WIDTH and grid_y + BLOCK_SIZE <= GRID_HEIGHT):
                rect = pygame.Rect(
                    GRID_X_OFFSET + grid_x * CELL_SIZE,
                    GRID_Y_OFFSET + grid_y * CELL_SIZE,
                    BLOCK_SIZE * CELL_SIZE - 1,
                    BLOCK_SIZE * CELL_SIZE - 1
                )
                pygame.draw.rect(screen, self.color, rect)
                # 绘制边框以便区分
                pygame.draw.rect(screen, WHITE, rect, 1)
