# 游戏配置常量

# 游戏常量
BLOCK_SIZE = 5  # 每个方块包含5x5=25个粒子
CELL_SIZE = 6  # 每个粒子的大小（增大像素值）
GRID_WIDTH = 60  # 网格列数（粒子级别）
GRID_HEIGHT = 100  # 网格行数（粒子级别）
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE  # 屏幕宽度 = 360像素
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE  # 屏幕高度 = 600像素
GRID_X_OFFSET = 0  # 去掉空白，从屏幕边缘开始
GRID_Y_OFFSET = 0  # 去掉空白，从屏幕顶部开始
WARNING_LINE_Y = 20  # 警戒线的y坐标（粒子单位），超过此线游戏结束

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
PINK_WHITE = (255, 240, 245)  # 粉白色背景
RED = (255, 0, 0)  # 红色警戒线

# 5种固定颜色（每次随机选择）
PARTICLE_COLORS = [
    (255, 100, 100),  # 红色
    (100, 255, 100),  # 绿色
    (100, 100, 255),  # 蓝色
    (255, 255, 100),  # 黄色
    (255, 100, 255),  # 紫色
]

# 游戏速度
FALL_SPEED = 300  # 毫秒
ANIMATION_SPEED = 0.05  # 动画速度
