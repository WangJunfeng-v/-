"""
粒子俄罗斯方块 - 主入口文件

模块结构:
- config.py: 游戏配置常量
- particle.py: 粒子类
- block.py: 方块类
- physics.py: 物理引擎（粒子移动和分散逻辑）
- renderer.py: 渲染器
- input_handler.py: 输入处理器
- game.py: 游戏主类
"""

from game import Game


if __name__ == "__main__":
    game = Game()
    game.run()
