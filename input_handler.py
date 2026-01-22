import pygame


class InputHandler:
    """输入处理器 - 处理用户输入"""
    
    def __init__(self):
        self.key_delay = {'left': 0, 'right': 0, 'down': 0}
    
    def update_delays(self):
        """更新按键延迟"""
        for key in self.key_delay:
            if self.key_delay[key] > 0:
                self.key_delay[key] -= 1
    
    def handle_movement(self, game):
        """处理移动输入"""
        if game.animating or game.current_block is None:
            return
        
        keys = pygame.key.get_pressed()
        self.update_delays()
        
        # 左右移动步幅
        move_step = 5
        
        # 左移
        if keys[pygame.K_LEFT] and self.key_delay['left'] == 0:
            move_step_actual = 0
            for step in range(1, move_step + 1):
                if not game.check_collision(game.current_block, -step, 0):
                    move_step_actual = step
                else:
                    break
            
            if move_step_actual > 0:
                game.current_block.move(-move_step_actual, 0)
                self.key_delay['left'] = 5
        
        # 右移
        if keys[pygame.K_RIGHT] and self.key_delay['right'] == 0:
            move_step_actual = 0
            for step in range(1, move_step + 1):
                if not game.check_collision(game.current_block, step, 0):
                    move_step_actual = step
                else:
                    break
            
            if move_step_actual > 0:
                game.current_block.move(move_step_actual, 0)
                self.key_delay['right'] = 5
        
        # 快速下落
        if keys[pygame.K_DOWN] and self.key_delay['down'] == 0:
            fall_distance = game.get_fall_distance(game.current_block)
            if fall_distance > 0:
                game.current_block.move(0, fall_distance)
                game.place_block()
                self.key_delay['down'] = 30
            else:
                if game.check_collision(game.current_block, 0, 1):
                    game.place_block()
                    self.key_delay['down'] = 30
    
    def handle_events(self, game):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # 支持大小写 R 键重新开始游戏
                # 检查键码或 unicode 字符
                is_r_key = (event.key == pygame.K_r or 
                           (event.unicode and event.unicode.lower() == 'r'))
                if is_r_key and game.game_over:
                    game.reset()
        
        return True
