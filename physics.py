import random
from config import GRID_WIDTH, GRID_HEIGHT


class PhysicsEngine:
    """物理引擎 - 处理粒子的移动和分散逻辑"""
    
    def __init__(self, grid):
        self.grid = grid
    
    def calculate_new_block_trajectories(self, new_particles):
        """只计算新落下方块的粒子轨迹，已固定的粒子不动
        
        规则：
        1. 底部没有粒子时，自动落下填充
        2. 相邻两列高度差不超过1，否则高列的粒子移到低列
        3. 如果中间列比两边都高超过1，随机选择一边
        
        new_particles: 新方块的粒子列表 [(particle, grid_x, grid_y), ...]
        """
        trajectories = {}
        
        # 获取每列现有的高度（已固定粒子的高度）
        existing_heights = [0] * GRID_WIDTH
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT - 1, -1, -1):
                particle = self.grid[x][y]
                # 只统计已固定的粒子（不在new_particles中的）
                if particle is not None:
                    is_new = False
                    for np, nx, ny in new_particles:
                        if np is particle:
                            is_new = True
                            break
                    if not is_new:
                        existing_heights[x] += 1
        
        # 创建模拟高度数组（用于计算最终状态）
        sim_heights = existing_heights.copy()
        
        # 收集所有新粒子及其原始位置
        all_new_particles = []
        for particle, grid_x, grid_y in new_particles:
            start_x = particle.x if not particle.animating else particle.get_draw_x()
            start_y = particle.y if not particle.animating else particle.get_draw_y()
            all_new_particles.append((particle, grid_x, grid_y, start_x, start_y))
        
        # 按原始列和y位置排序（从下到上处理）
        all_new_particles.sort(key=lambda p: (p[1], -p[2]))
        
        # 模拟每个粒子的最终位置
        for particle, orig_col, orig_y, start_x, start_y in all_new_particles:
            # 找到该粒子应该落到哪一列
            target_col = self._find_target_column(sim_heights, orig_col)
            
            # 该粒子落到目标列的顶部
            target_y = GRID_HEIGHT - 1 - sim_heights[target_col]
            
            # 更新模拟高度
            sim_heights[target_col] += 1
            
            # 记录最终位置
            trajectories[particle] = (start_x, start_y, target_col, target_y)
        
        return trajectories
    
    def _find_target_column(self, heights, orig_col):
        """根据分散规则找到粒子应该落到的目标列
        
        规则：
        1. 如果当前列加上这个粒子后，与相邻列高度差不超过1，就落在当前列
        2. 否则，移动到较低的相邻列
        3. 如果两边都低且差距相同，随机选择
        """
        # 计算如果粒子落在原始列，新高度是多少
        new_height = heights[orig_col] + 1
        
        # 获取左右相邻列的高度
        left_height = heights[orig_col - 1] if orig_col > 0 else float('inf')
        right_height = heights[orig_col + 1] if orig_col < GRID_WIDTH - 1 else float('inf')
        
        # 计算高度差
        left_diff = new_height - left_height
        right_diff = new_height - right_height
        
        # 如果与两边高度差都不超过1，就落在当前列
        if left_diff <= 1 and right_diff <= 1:
            return orig_col
        
        # 需要移动到较低的列
        if left_diff > 1 and right_diff > 1:
            # 两边都需要移动，随机选择一边（或选择较低的）
            if left_height < right_height:
                return self._find_target_column(heights, orig_col - 1)
            elif right_height < left_height:
                return self._find_target_column(heights, orig_col + 1)
            else:
                # 高度相同，随机选择
                if random.random() < 0.5:
                    return self._find_target_column(heights, orig_col - 1)
                else:
                    return self._find_target_column(heights, orig_col + 1)
        elif left_diff > 1:
            # 只向左移动
            return self._find_target_column(heights, orig_col - 1)
        elif right_diff > 1:
            # 只向右移动
            return self._find_target_column(heights, orig_col + 1)
        
        return orig_col
    
    def calculate_remaining_particles_trajectories(self, remaining_particles):
        """计算消除后剩余粒子的最终位置轨迹
        
        规则：
        1. 先让每列的粒子垂直下落填补空隙（保持颜色顺序）
        2. 然后按照分散规则（相邻两列高度差不超过1）得到最终状态
        """
        trajectories = {}
        
        if not remaining_particles:
            return trajectories
        
        # 按列分组粒子
        particles_by_column = {}
        for particle, orig_x, orig_y, start_x, start_y in remaining_particles:
            if orig_x not in particles_by_column:
                particles_by_column[orig_x] = []
            particles_by_column[orig_x].append((particle, orig_x, orig_y, start_x, start_y))
        
        # 对每列的粒子按y排序（从下到上，保持顺序）
        for col in particles_by_column:
            particles_by_column[col].sort(key=lambda p: -p[2])  # y值大的在前（靠近底部）
        
        # 第一步：计算每列垂直下落后的中间状态
        # 记录每列的粒子列表（从底到顶的顺序）
        column_stacks = {}  # col -> [(particle, start_x, start_y), ...]
        for col in range(GRID_WIDTH):
            column_stacks[col] = []
        
        for col, particles_list in particles_by_column.items():
            for particle, orig_x, orig_y, start_x, start_y in particles_list:
                column_stacks[col].append((particle, start_x, start_y))
        
        # 第二步：按照分散规则重新分配粒子位置
        # 计算当前每列高度
        sim_heights = [len(column_stacks[col]) for col in range(GRID_WIDTH)]
        
        # 模拟分散过程，得到最终每列高度
        final_heights = self._calculate_dispersed_heights(sim_heights)
        
        # 为每列分配粒子，保持每列内部顺序
        # 先确定每列需要多少粒子
        target_heights = final_heights.copy()
        
        # 重新分配粒子到各列
        final_column_stacks = {col: [] for col in range(GRID_WIDTH)}
        
        # 从每列取粒子，分配到最终位置
        # 策略：尽量让粒子留在原列附近，同时满足高度要求
        for col in range(GRID_WIDTH):
            needed = target_heights[col]
            available = column_stacks[col].copy()
            
            # 先用本列的粒子
            while len(final_column_stacks[col]) < needed and available:
                final_column_stacks[col].append(available.pop(0))
            
            # 把多余的粒子放回待分配
            column_stacks[col] = available
        
        # 处理剩余粒子（需要移动到其他列的）
        remaining = []
        for col in range(GRID_WIDTH):
            remaining.extend([(p, s_x, s_y, col) for p, s_x, s_y in column_stacks[col]])
        
        # 把剩余粒子分配到还需要粒子的列
        for col in range(GRID_WIDTH):
            needed = target_heights[col] - len(final_column_stacks[col])
            while needed > 0 and remaining:
                # 找最近的剩余粒子
                best_idx = 0
                best_dist = abs(remaining[0][3] - col)
                for i, (p, s_x, s_y, orig_col) in enumerate(remaining):
                    dist = abs(orig_col - col)
                    if dist < best_dist:
                        best_dist = dist
                        best_idx = i
                
                particle, start_x, start_y, orig_col = remaining.pop(best_idx)
                final_column_stacks[col].append((particle, start_x, start_y))
                needed -= 1
        
        # 生成最终轨迹
        for col in range(GRID_WIDTH):
            for i, (particle, start_x, start_y) in enumerate(final_column_stacks[col]):
                target_y = GRID_HEIGHT - 1 - i
                trajectories[particle] = (start_x, start_y, col, target_y)
        
        return trajectories
    
    def _calculate_dispersed_heights(self, heights):
        """计算分散后每列的最终高度（相邻两列高度差不超过1）"""
        total = sum(heights)
        result = heights.copy()
        
        # 迭代调整直到满足条件
        max_iterations = 1000
        for _ in range(max_iterations):
            changed = False
            for col in range(GRID_WIDTH):
                if result[col] == 0:
                    continue
                
                left_h = result[col - 1] if col > 0 else result[col]
                right_h = result[col + 1] if col < GRID_WIDTH - 1 else result[col]
                
                # 检查是否需要向左移动
                if col > 0 and result[col] - left_h > 1:
                    result[col] -= 1
                    result[col - 1] += 1
                    changed = True
                # 检查是否需要向右移动
                elif col < GRID_WIDTH - 1 and result[col] - right_h > 1:
                    result[col] -= 1
                    result[col + 1] += 1
                    changed = True
            
            if not changed:
                break
        
        return result
    
    def find_connected_region(self, start_x, start_y, color):
        """使用BFS找到与起始点连通的所有相同颜色粒子"""
        visited = set()
        region = []
        queue = [(start_x, start_y)]
        
        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
                continue
            if self.grid[x][y] is None:
                continue
            if self.grid[x][y].color != color:
                continue
            
            visited.add((x, y))
            region.append((x, y))
            
            # 检查四个方向的相邻粒子
            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))
        
        return region, visited
    
    def check_region_spans_width(self, region):
        """检查一个连通区域是否横跨整个地图宽度"""
        if not region:
            return False
        
        # 获取区域中所有x坐标
        x_coords = set(x for x, y in region)
        
        # 检查是否从最左边到最右边都有
        return 0 in x_coords and (GRID_WIDTH - 1) in x_coords
    
    def get_column_height(self, col):
        """获取某一列的高度"""
        height = 0
        for y in range(GRID_HEIGHT):
            if self.grid[col][y] is not None:
                height += 1
        return height
