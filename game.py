import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT,
    WARNING_LINE_Y, FALL_SPEED, ANIMATION_SPEED
)
from particle import Particle
from block import Block
from physics import PhysicsEngine
from renderer import Renderer
from input_handler import InputHandler


class Game:
    """游戏主类"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("粒子俄罗斯方块")
        self.clock = pygame.time.Clock()
        
        # 初始化组件
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        
        # 初始化游戏状态
        self.reset()
    
    def reset(self):
        """重置游戏"""
        # 游戏网格：存储已落下的粒子
        self.grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        
        # 物理引擎
        self.physics = PhysicsEngine(self.grid)
        
        # 当前方块
        self.current_block = None
        self.spawn_new_block()
        
        # 游戏状态
        self.fall_time = 0
        self.fall_speed = FALL_SPEED
        self.game_over = False
        self.score = 0
        
        # 动画状态
        self.animating = False
        self.animation_step = 0
        self.particles_animating = False
        self.disperse_stage = 0
        self.pending_trajectories = []
        self.clear_line_trajectories = {}
    
    def spawn_new_block(self):
        """生成新方块"""
        self.current_block = Block()
        # 检查游戏是否结束
        if self.check_collision(self.current_block, 0, 0):
            self.game_over = True
    
    def check_collision(self, block, dx, dy):
        """检查碰撞"""
        for px, py in block.particles:
            grid_x = block.x + px + dx
            grid_y = block.y + py + dy
            
            # 检查边界
            if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
                return True
            
            # 检查与已落下粒子的碰撞
            if self.grid[grid_x][grid_y] is not None:
                return True
        
        return False
    
    def get_fall_distance(self, block):
        """计算方块能下落的最大距离"""
        fall_distance = 0
        while not self.check_collision(block, 0, fall_distance + 1):
            fall_distance += 1
        return fall_distance
    
    def check_warning_line(self):
        """检查是否有粒子超过警戒线"""
        for x in range(GRID_WIDTH):
            for y in range(WARNING_LINE_Y):
                if self.grid[x][y] is not None:
                    return True
        return False
    
    def place_block(self):
        """将方块放置到网格中"""
        # 收集新方块的所有粒子
        new_particles = []
        
        # 将方块中的所有粒子放置到网格中
        for px, py in self.current_block.particles:
            grid_x = self.current_block.x + px
            grid_y = self.current_block.y + py
            
            # 只放置网格范围内的粒子
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                if self.grid[grid_x][grid_y] is None:
                    particle = Particle(grid_x, grid_y, self.current_block.color)
                    self.grid[grid_x][grid_y] = particle
                    new_particles.append((particle, grid_x, grid_y))
        
        # 隐藏大方块显示
        self.current_block = None
        
        # 只计算新方块粒子的轨迹（已固定粒子不动）
        trajectories = self.physics.calculate_new_block_trajectories(new_particles)
        
        # 初始化动画
        self.animating = True
        self.animation_step = 0
        self.disperse_stage = 0
        self.pending_trajectories = [trajectories] if trajectories else []
        
        # 应用轨迹，只有新粒子移动
        if trajectories:
            self.apply_trajectories(trajectories)
    
    def apply_trajectories(self, trajectories):
        """应用轨迹到粒子"""
        particles_to_move = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] is not None:
                    particle = self.grid[x][y]
                    if particle in trajectories:
                        start_x, start_y, target_x, target_y = trajectories[particle]
                        particles_to_move.append((particle, x, y, start_x, start_y, target_x, target_y))
        
        # 清空网格，准备重新放置
        for particle, old_x, old_y, start_x, start_y, target_x, target_y in particles_to_move:
            self.grid[old_x][old_y] = None
        
        # 根据轨迹设置所有粒子
        for particle, old_x, old_y, start_x, start_y, target_x, target_y in particles_to_move:
            if particle.animating:
                start_x = particle.get_draw_x()
                start_y = particle.get_draw_y()
            
            particle.x = start_x
            particle.y = start_y
            particle.set_target(target_x, target_y)
            self.grid[target_x][target_y] = particle
            self.particles_animating = True
    
    def apply_clear_line_trajectories(self):
        """应用消除后的粒子移动轨迹"""
        if not self.clear_line_trajectories:
            return
        
        trajectories = self.clear_line_trajectories
        
        particles_to_move = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] is not None:
                    particle = self.grid[x][y]
                    if particle in trajectories:
                        start_x, start_y, target_x, target_y = trajectories[particle]
                        particles_to_move.append((particle, x, y, start_x, start_y, target_x, target_y))
        
        # 清空所有旧位置
        for particle, old_x, old_y, start_x, start_y, target_x, target_y in particles_to_move:
            self.grid[old_x][old_y] = None
        
        # 设置新位置和动画
        for particle, old_x, old_y, start_x, start_y, target_x, target_y in particles_to_move:
            particle.x = start_x
            particle.y = start_y
            particle.set_target(int(target_x), int(target_y))
            self.grid[int(target_x)][int(target_y)] = particle
            self.particles_animating = True
        
        self.clear_line_trajectories = {}
    
    def check_and_clear_lines(self):
        """检查并消除横跨整个地图的相同颜色连通区域"""
        visited = set()
        regions_to_clear = []
        
        # 遍历所有粒子，找到所有连通区域
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in visited and self.grid[x][y] is not None:
                    color = self.grid[x][y].color
                    region, region_visited = self.physics.find_connected_region(x, y, color)
                    visited.update(region_visited)
                    
                    # 检查这个区域是否横跨整个地图
                    if self.physics.check_region_spans_width(region):
                        regions_to_clear.append(region)
        
        if not regions_to_clear:
            return False
        
        # 计算得分
        for region in regions_to_clear:
            particle_count = len(region)
            min_y = min(y for x, y in region)
            max_height = GRID_HEIGHT - min_y
            region_score = particle_count * max_height
            self.score += region_score
        
        # 收集所有要消除的位置
        positions_to_clear = set()
        for region in regions_to_clear:
            for pos in region:
                positions_to_clear.add(pos)
        
        # 消除这些位置的粒子
        for x, y in positions_to_clear:
            self.grid[x][y] = None
        
        # 收集剩余的粒子
        remaining_particles = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] is not None:
                    particle = self.grid[x][y]
                    start_x = particle.x if not particle.animating else particle.get_draw_x()
                    start_y = particle.y if not particle.animating else particle.get_draw_y()
                    remaining_particles.append((particle, x, y, start_x, start_y))
        
        # 计算剩余粒子的最终位置
        trajectories = self.physics.calculate_remaining_particles_trajectories(remaining_particles)
        
        self.clear_line_trajectories = trajectories
        
        return True
    
    def update(self, dt):
        """更新游戏状态"""
        if self.game_over:
            return
        
        # 更新所有粒子的动画
        self.particles_animating = False
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] is not None:
                    self.grid[x][y].update_animation(speed=ANIMATION_SPEED)
                    if self.grid[x][y].animating:
                        self.particles_animating = True
        
        # 如果正在执行动画
        if self.animating:
            if not self.particles_animating:
                self.disperse_stage += 1
                
                if self.disperse_stage < len(self.pending_trajectories):
                    self.apply_trajectories(self.pending_trajectories[self.disperse_stage])
                else:
                    self.animating = False
                    self.animation_step = 0
                    self.disperse_stage = 0
                    self.pending_trajectories = []
                    
                    # 检查警戒线
                    if self.check_warning_line():
                        self.game_over = True
                        return
                    
                    # 检查消除
                    if self.check_and_clear_lines():
                        if self.clear_line_trajectories:
                            self.animating = True
                            self.disperse_stage = 0
                            self.pending_trajectories = [self.clear_line_trajectories]
                            self.apply_clear_line_trajectories()
                        else:
                            self.spawn_new_block()
                    else:
                        self.spawn_new_block()
            return
        
        self.fall_time += dt
        
        # 自动下落
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.check_collision(self.current_block, 0, 1):
                self.current_block.move(0, 1)
            else:
                self.place_block()
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            dt = self.clock.tick(60)
            
            # 处理事件
            running = self.input_handler.handle_events(self)
            
            if not self.game_over:
                self.input_handler.handle_movement(self)
                self.update(dt)
            
            # 渲染
            self.renderer.render(self.grid, self.current_block, self.score, self.game_over)
        
        pygame.quit()
