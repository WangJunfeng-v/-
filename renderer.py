import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT,
    CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, WARNING_LINE_Y,
    PINK_WHITE, GRAY, RED, WHITE, BLACK
)


class Renderer:
    """渲染器 - 处理所有绘制逻辑"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # 初始化字体
        self.font = None
        self.small_font = None
        self._init_fonts()
    
    def _init_fonts(self):
        """初始化字体"""
        try:
            # 尝试使用Windows中文字体
            self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 36)
            self.small_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)
        except:
            try:
                # 尝试使用SimSun
                self.font = pygame.font.Font("C:/Windows/Fonts/simsun.ttc", 36)
                self.small_font = pygame.font.Font("C:/Windows/Fonts/simsun.ttc", 24)
            except:
                # 如果都失败，使用系统默认字体
                self.font = pygame.font.SysFont("simsun", 36)
                self.small_font = pygame.font.SysFont("simsun", 24)
    
    def clear_screen(self):
        """清屏"""
        self.screen.fill(PINK_WHITE)
    
    def draw_grid(self):
        """绘制网格背景"""
        for x in range(GRID_WIDTH + 1):
            start_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET)
            end_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE)
            pygame.draw.line(self.screen, GRAY, start_pos, end_pos)
        
        for y in range(GRID_HEIGHT + 1):
            start_pos = (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE)
            end_pos = (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE)
            pygame.draw.line(self.screen, GRAY, start_pos, end_pos)
    
    def draw_warning_line(self):
        """绘制红色警戒线"""
        line_y = GRID_Y_OFFSET + WARNING_LINE_Y * CELL_SIZE
        start_pos = (GRID_X_OFFSET, line_y)
        end_pos = (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, line_y)
        pygame.draw.line(self.screen, RED, start_pos, end_pos, 2)
    
    def draw_particles(self, grid):
        """绘制所有已落下的粒子"""
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if grid[x][y] is not None:
                    grid[x][y].draw(self.screen)
    
    def draw_block(self, block):
        """绘制当前方块"""
        if block:
            block.draw(self.screen)
    
    def draw_score(self, score):
        """绘制得分"""
        score_text = self.small_font.render(f"得分: {score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
    
    def draw_game_over(self):
        """绘制游戏结束信息"""
        text = self.font.render("游戏结束！按R重新开始", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
    
    def render(self, grid, current_block, score, game_over):
        """渲染整个游戏画面"""
        self.clear_screen()
        
        # 绘制红色警戒线
        self.draw_warning_line()
        
        # 绘制已落下的粒子
        self.draw_particles(grid)
        
        # 绘制当前方块
        self.draw_block(current_block)
        
        # 绘制得分（左上角）
        self.draw_score(score)
        
        # 绘制游戏结束信息
        if game_over:
            self.draw_game_over()
        
        pygame.display.flip()
