from typing import List, Tuple
from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用

class MyAI(Alg3D):
    def get_move(
        self,
        board: Board, # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # 可視化: 現在の盤面と置けるマスを表示
        self.visualize_board(board)
        self.print_legal_moves(board)
        
        # 可視化: 各マスのアクセス可能ライン数を表示
        self.print_line_accessibility(board, player)
        
        # 可視化: 各マスの重み（点数）を表示
        self.print_position_scores(board, player)
        
        # 可視化: 各マスで妨害できる相手の石数を表示
        self.print_opponent_interference(board, player)
        
        # 基本的なAIアルゴリズムを実装
        move = self.find_best_move(board, player)
        
        # 可視化: AIの選択理由を表示
        self.print_move_reason(board, player, move)
        
        return move

    def get_legal_moves(self, board: Board) -> List[Tuple[int, int, int]]:
        """現在置けるすべての手を (x, y, z) で返す。満杯列は除外。"""
        moves: List[Tuple[int, int, int]] = []
        for y in range(4):
            for x in range(4):
                z = self.get_height(board, x, y)
                if z < 4:
                    moves.append((x, y, z))
        return moves

    def print_legal_moves(self, board: Board) -> None:
        """置けるマスを4x4の表で表示。各セルには石が落ちる z を表示（満杯は .）。"""
        grid = [['.' for _ in range(4)] for _ in range(4)]
        moves = self.get_legal_moves(board)
        for x, y, z in moves:
            grid[y][x] = str(z)

        # y=3 を上にして見やすく表示
        print("  x→   0 1 2 3    （値＝落ちる z / .＝満杯）")
        for y in range(3, -1, -1):
            print(f"y={y} |", ' '.join(grid[y]))
        print("合法手一覧:", sorted(moves))
    
    def count_accessible_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時にアクセスできる勝利ライン数をカウント"""
        # 仮想的に石を置く
        temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        temp_board[z][y][x] = player
        
        accessible_lines = 0
        
        # 13方向の直線をチェック
        directions = [
            (1, 0, 0),   # x軸方向
            (0, 1, 0),   # y軸方向
            (0, 0, 1),   # z軸方向
            (1, 1, 0),   # xy対角線
            (1, 0, 1),   # xz対角線
            (0, 1, 1),   # yz対角線
            (1, 1, 1),   # xyz対角線
            (1, -1, 0),  # xy逆対角線
            (1, 0, -1),  # xz逆対角線
            (0, 1, -1),  # yz逆対角線
            (1, -1, -1), # xyz逆対角線
            (1, 1, -1),  # xy正、z負対角線
            (1, -1, 1),  # xy負、z正対角線
        ]
        
        for dx, dy, dz in directions:
            count = 1  # 現在の石を含む
            
            # 正方向にカウント
            nx, ny, nz = x + dx, y + dy, z + dz
            while 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4 and temp_board[nz][ny][nx] == player:
                count += 1
                nx, ny, nz = nx + dx, ny + dy, nz + dz
            
            # 負方向にカウント
            nx, ny, nz = x - dx, y - dy, z - dz
            while 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4 and temp_board[nz][ny][nx] == player:
                count += 1
                nx, ny, nz = nx - dx, ny - dy, nz - dz
            
            # 4つ以上並ぶ可能性があるラインをカウント
            if count >= 2:  # 2つ以上並んでいるライン
                accessible_lines += 1
        
        return accessible_lines
    
    def classify_directions(self, board: Board, x: int, y: int, z: int, player: int) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int]], List[Tuple[int, int, int]]]:
        """指定位置に石を置いた時に、方向を3つに分類して返す"""
        my_accessible_directions = []  # 自分のアクセスライン（自分の石しかないか空）
        opponent_accessible_directions = []  # 相手のアクセスライン（相手の石しかない）
        mixed_directions = []  # 混在ライン（自分の石と相手の石が混在）
        
        opponent = 3 - player
        
        # 13方向の直線をチェック
        directions = [
            (1, 0, 0),   # x軸方向
            (0, 1, 0),   # y軸方向
            (0, 0, 1),   # z軸方向
            (1, 1, 0),   # xy対角線
            (1, 0, 1),   # xz対角線
            (0, 1, 1),   # yz対角線
            (1, 1, 1),   # xyz対角線
            (1, -1, 0),  # xy逆対角線
            (1, 0, -1),  # xz逆対角線
            (0, 1, -1),  # yz逆対角線
            (1, -1, -1), # xyz逆対角線
            (1, 1, -1),  # xy正、z負対角線
            (1, -1, 1),  # xy負、z正対角線
        ]
        
        for dx, dy, dz in directions:
            # 正方向の最大距離と障害物チェック
            max_pos = 0
            has_opponent_stone = False
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if board[nz][ny][nx] == opponent:
                        has_opponent_stone = True
                        break
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離と障害物チェック
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if board[nz][ny][nx] == opponent:
                        has_opponent_stone = True
                        break
                    max_neg = i
                else:
                    break
            
            # 合計で4つ以上並べるかチェック
            if max_pos + max_neg + 1 >= 4:
                # ライン上の石の種類をチェック
                my_stones = 0
                opponent_stones = 0
                
                for i in range(-max_neg, max_pos + 1):
                    if i == 0:
                        continue  # 自分の位置はスキップ
                    nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                    if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                        if board[nz][ny][nx] == player:
                            my_stones += 1
                        elif board[nz][ny][nx] == opponent:
                            opponent_stones += 1
                
                # 分類
                if my_stones > 0 and opponent_stones > 0:
                    mixed_directions.append((dx, dy, dz))
                elif my_stones > 0:
                    my_accessible_directions.append((dx, dy, dz))
                elif opponent_stones > 0:
                    opponent_accessible_directions.append((dx, dy, dz))
                else:
                    my_accessible_directions.append((dx, dy, dz))  # 空のラインは自分のアクセスライン
        
        return my_accessible_directions, opponent_accessible_directions, mixed_directions
    
    def get_accessible_directions(self, board: Board, x: int, y: int, z: int, player: int) -> List[Tuple[int, int, int]]:
        """指定位置に石を置いた時に、アクセス可能な方向の配列を返す（後方互換性のため）"""
        my_accessible, _, _ = self.classify_directions(board, x, y, z, player)
        return my_accessible
    
    def count_stones_in_directions(self, board: Board, x: int, y: int, z: int, directions: List[Tuple[int, int, int]], target_player: int) -> int:
        """指定された方向リスト内で、対象プレイヤーの石の数をカウント"""
        stone_count = 0
        
        for dx, dy, dz in directions:
            # 正方向の最大距離を計算
            max_pos = 0
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離を計算
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    max_neg = i
                else:
                    break
            
            # この方向の対象プレイヤーの石をカウント
            for i in range(-max_neg, max_pos + 1):
                if i == 0:
                    continue  # 自分の位置はスキップ
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if board[nz][ny][nx] == target_player:
                        stone_count += 1
        
        return stone_count
    
    def count_potential_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時に、4つ並ぶ可能性があるライン数をカウント"""
        return len(self.get_accessible_directions(board, x, y, z, player))
    
    def print_line_accessibility(self, board: Board, player: int) -> None:
        """各マスに置いた時のアクセス可能ライン数を表示"""
        print(f"\n📊 プレイヤー{player}の各マスアクセス可能ライン数:")
        print("  x→   0 1 2 3    （値＝4つ並ぶ可能性があるライン数）")
        
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    # 常に潜在的なライン数を表示
                    lines = self.count_potential_lines(board, x, y, z, player)
                    print(f"{lines:2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
    
    def visualize_board(self, board: Board) -> None:
        """3D盤面を可視化"""
        print("\n" + "=" * 50)
        print("立体四目並べ盤面 (Z軸: 下から上へ 0→3)")
        print("=" * 50)
        
        for z in range(3, -1, -1):  # 上から下へ表示
            print(f"\nZ = {z} (高さ {z}):")
            print("  0 1 2 3")
            for y in range(4):
                print(f"{y} ", end="")
                for x in range(4):
                    if board[z][y][x] == 0:
                        print("・", end=" ")
                    elif board[z][y][x] == 1:
                        print("●", end=" ")  # 先手（黒）
                    elif board[z][y][x] == 2:
                        print("○", end=" ")  # 後手（白）
                print()
    
    def print_move_reason(self, board: Board, player: int, move: Tuple[int, int]) -> None:
        """AIの選択理由を表示"""
        print(f"\n🎮 AI選択: {move}")
        print(f"プレイヤー: {player} ({'先手(黒)' if player == 1 else '後手(白)'})")
        
        # 選択理由を分析
        win_move = self.find_winning_move(board, player)
        if win_move and win_move == move:
            print("🏆 理由: 勝利手")
            return
        
        opponent = 3 - player
        block_move = self.find_winning_move(board, opponent)
        if block_move and block_move == move:
            print("🛡️ 理由: 防御手")
            return
        
        best_line_move = self.find_highest_line_access_move(board, player)
        if best_line_move and best_line_move == move:
            score = self.evaluate_position(board, move[0], move[1], self.get_height(board, move[0], move[1]), player, 0)
            print(f"🎯 理由: 最高重み点数 ({score}点)")
            return
        
        print("📍 理由: フォールバック")
    
    def print_position_scores(self, board: Board, player: int) -> None:
        """各マスの重み（点数）を詳細表示"""
        print(f"\n🎯 プレイヤー{player}の各マス重み詳細:")
        
        # 各重みの詳細を表示
        print("\n📊 重み詳細:")
        print("  x→   0 1 2 3    （値＝各重みの点数）")
        
        # 1. アクセス可能ライン数
        print("\n1️⃣ アクセス可能ライン数 (1ライン=2点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    lines = self.count_potential_lines(board, x, y, z, player)
                    print(f"{lines*2:2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 2. アクセスライン上の自分の石の数
        print("\n2️⃣ アクセスライン上の自分の石の数 (1石=2点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    own_stones = self.count_own_stones_in_lines(board, x, y, z, player)
                    print(f"{own_stones*2:2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 2-1. 混在時の相手石による減点
        print("\n2️⃣-1 混在時の相手石による減点 (1石=2点減点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    own_stones = self.count_own_stones_in_lines(board, x, y, z, player)
                    opponent_stones = self.count_opponent_stones_in_lines(board, x, y, z, player)
                    if own_stones > 0 and opponent_stones > 0:
                        penalty = opponent_stones * 2
                        print(f"-{penalty:2d}", end=" ")
                    else:
                        print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 2-2. 相手の石のみの場合の段階的加点
        print("\n2️⃣-2 相手の石のみの場合の段階的加点 (1石目=2点, 2石目=4点, 3石目=6点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    own_stones = self.count_own_stones_in_lines(board, x, y, z, player)
                    opponent_stones = self.count_opponent_stones_in_lines(board, x, y, z, player)
                    if own_stones == 0 and opponent_stones > 0:
                        # 段階的加点の計算
                        bonus = 0
                        for i in range(opponent_stones):
                            bonus += (i + 1) * 2
                        print(f"+{bonus:2d}", end=" ")
                    else:
                        print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 3. 角と中央の4マスの位置ボーナス
        print("\n3️⃣ 角と中央の4マスの位置ボーナス (2点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    if (x == 0 or x == 3) and (y == 0 or y == 3):  # 角の4マス
                        print("  2", end=" ")
                    elif (x == 1 or x == 2) and (y == 1 or y == 2):  # 中央の4マス
                        print("  2", end=" ")
                    else:
                        print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 4. ダブルリーチ報酬
        print("\n4️⃣ ダブルリーチ報酬 (2個目以降=100点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    double_reach_lines = self.count_double_reach_lines(board, x, y, z, player)
                    if double_reach_lines >= 2:
                        bonus = (double_reach_lines - 1) * 100  # 2個目以降=100点
                        print(f"+{bonus:2d}", end=" ")
                    else:
                        print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 5. ダブルリーチ妨害
        print("\n5️⃣ ダブルリーチ妨害 (2個目以降=100点):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    opponent_double_reach_lines = self.count_opponent_double_reach_lines(board, x, y, z, player)
                    if opponent_double_reach_lines >= 2:
                        bonus = (opponent_double_reach_lines - 1) * 100  # 2個目以降=100点
                        print(f"+{bonus:2d}", end=" ")
                    else:
                        print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 6. 罠回避（統合版・depth別重み）
        print("\n6️⃣ 罠回避 (自分の手:勝利手100点減点,最大点数*0.5 / 相手の手:勝利手80点減点,最大点数*0.4):")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    opponent_winning_moves = self.check_opponent_winning_moves_after_my_move(board, x, y, z, player)
                    opponent_max_score = self.get_opponent_max_score_after_my_move(board, x, y, z, player)
                    
                    if opponent_winning_moves > 0:
                        penalty = opponent_winning_moves * 100  # 自分の手の重みで表示
                        print(f"-{penalty:2d}", end=" ")
                    else:
                        penalty = int(opponent_max_score * 0.5)  # 自分の手の重みで表示
                        if penalty > 0:
                            print(f"-{penalty:2d}", end=" ")
                        else:
                            print("  0", end=" ")
                else:
                    print(" .", end=" ")
            print()
        
        # 7. 合計
        print("\n🎯 合計点数:")
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    score = self.evaluate_position(board, x, y, z, player, 0)
                    print(f"{int(score):2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
    
    def find_best_move(self, board: Board, player: int):
        """最適な手を見つける"""
        # 1. 勝利できる手があるかチェック
        win_move = self.find_winning_move(board, player)
        if win_move:
            return win_move
        
        # 2. 相手の勝利を阻止する手があるかチェック
        opponent = 3 - player  # 相手のプレイヤー番号
        block_move = self.find_winning_move(board, opponent)
        if block_move:
            return block_move
        
        # 3. 最もアクセス可能なライン数が多い位置を探す
        best_move = self.find_highest_line_access_move(board, player)
        if best_move:
            return best_move
        
        # 4. 空いている最初の位置に置く
        return self.find_first_available_move(board)
    
    def count_opponent_stones_in_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時に、アクセスできるライン上の相手の石の数をカウント"""
        opponent = 3 - player
        opponent_stones = 0
        accessible_directions = self.get_accessible_directions(board, x, y, z, player)
        
        for dx, dy, dz in accessible_directions:
            # 正方向の最大距離と障害物チェック
            max_pos = 0
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離と障害物チェック
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_neg = i
                else:
                    break
            
                # このライン上で相手の石をカウント
                for i in range(-max_neg, max_pos + 1):
                    if i == 0:
                        continue  # 自分の位置はスキップ
                    nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                    if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                        if board[nz][ny][nx] == opponent:
                            opponent_stones += 1
        
        return opponent_stones
    
    def count_own_stones_in_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時に、アクセスできるライン上の自分の石の数をカウント"""
        own_stones = 0
        accessible_directions = self.get_accessible_directions(board, x, y, z, player)
        
        for dx, dy, dz in accessible_directions:
            # 正方向の最大距離と障害物チェック
            max_pos = 0
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離と障害物チェック
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_neg = i
                else:
                    break
            
            # このライン上で自分の石をカウント
            for i in range(-max_neg, max_pos + 1):
                if i == 0:
                    continue  # 自分の位置はスキップ
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if board[nz][ny][nx] == player:
                        own_stones += 1
        
        return own_stones
    
    def count_double_reach_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時に、自分の石が2個以上あるアクセスライン数をカウント"""
        double_reach_lines = 0
        accessible_directions = self.get_accessible_directions(board, x, y, z, player)
        
        for dx, dy, dz in accessible_directions:
            # 正方向の最大距離と障害物チェック
            max_pos = 0
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離と障害物チェック
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 他のプレイヤーの石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != player:
                        break
                    max_neg = i
                else:
                    break
            
            # このライン上で自分の石をカウント（自分を置く位置も含む）
            own_count = 1  # 自分を置く位置
            for i in range(-max_neg, max_pos + 1):
                if i == 0:
                    continue  # 自分の位置は既にカウント済み
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    if board[nz][ny][nx] == player:
                        own_count += 1
            
            # 自分の石が2個以上あるラインをカウント
            if own_count >= 2:
                double_reach_lines += 1
        
        return double_reach_lines
    
    def count_opponent_double_reach_lines(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に石を置いた時に、相手の石が2個以上あるアクセスライン数をカウント"""
        opponent = 3 - player
        opponent_double_reach_lines = 0
        
        # 相手の視点でアクセス可能な方向を取得
        accessible_directions = self.get_accessible_directions(board, x, y, z, opponent)
        
        for dx, dy, dz in accessible_directions:
            # 正方向の最大距離と障害物チェック
            max_pos = 0
            for i in range(1, 4):
                nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 自分の石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != opponent:
                        break
                    max_pos = i
                else:
                    break
            
            # 負方向の最大距離と障害物チェック
            max_neg = 0
            for i in range(1, 4):
                nx, ny, nz = x - i*dx, y - i*dy, z - i*dz
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                    # 自分の石がある場合はラインを断ち切る
                    if board[nz][ny][nx] != 0 and board[nz][ny][nx] != opponent:
                        break
                    max_neg = i
                else:
                    break
            
            # 合計で4つ以上並べるかチェック
            if max_pos + max_neg + 1 >= 4:
                # このライン上で相手の石をカウント
                opponent_count = 0
                for i in range(-max_neg, max_pos + 1):
                    nx, ny, nz = x + i*dx, y + i*dy, z + i*dz
                    if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4:
                        if board[nz][ny][nx] == opponent:
                            opponent_count += 1
                
                # 相手の石が2個以上あるラインをカウント
                if opponent_count >= 2:
                    opponent_double_reach_lines += 1
        
        return opponent_double_reach_lines
    
    def check_opponent_winning_moves_after_my_move(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置に自分の石を置いた後、相手が勝利できる手の数をカウント"""
        opponent = 3 - player
        
        # 仮想的に自分の石を置く
        temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        temp_board[z][y][x] = player
        
        # 相手が勝利できる手の数をカウント
        winning_moves_count = 0
        
        for opp_x in range(4):
            for opp_y in range(4):
                if self.can_place_stone(temp_board, opp_x, opp_y):
                    opp_z = self.get_height(temp_board, opp_x, opp_y)
                    
                    # 仮想的に相手の石を置いてみる
                    temp_board2 = [[[temp_board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
                    temp_board2[opp_z][opp_y][opp_x] = opponent
                    
                    if self.check_win(temp_board2, opp_x, opp_y, opp_z, opponent):
                        winning_moves_count += 1
        
        return winning_moves_count
    
    def get_opponent_max_score_after_my_move(self, board: Board, x: int, y: int, z: int, player: int, depth: int = 0) -> int:
        """指定位置に自分の石を置いた後、相手が得られる最大点数を取得"""
        opponent = 3 - player
        
        # 仮想的に自分の石を置く
        temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        temp_board[z][y][x] = player
        
        # 相手が得られる最大点数を計算
        max_score = -1
        
        for opp_x in range(4):
            for opp_y in range(4):
                if self.can_place_stone(temp_board, opp_x, opp_y):
                    opp_z = self.get_height(temp_board, opp_x, opp_y)
                    score = self.evaluate_position(temp_board, opp_x, opp_y, opp_z, opponent, depth)
                    max_score = max(max_score, score)
        
        return max_score if max_score > -1 else 0
    
    def calculate_reward(self, board: Board, x: int, y: int, z: int, player: int) -> int:
        """指定位置の報酬を計算"""
        reward = 0
        
        # 1. アクセス可能なライン数による基本点
        lines = self.count_potential_lines(board, x, y, z, player)
        reward += lines * 2  # 1ライン = 2点
        
        # 2. 方向別の石の数計算
        my_accessible, opponent_accessible, mixed = self.classify_directions(board, x, y, z, player)
        
        # 2-1. 自分のアクセスライン上の自分の石の数加点
        my_stones = self.count_stones_in_directions(board, x, y, z, my_accessible, player)
        reward += my_stones * 2  # 自分の石1個 = 2点
        
        # 2-2. 相手のアクセスライン上の相手の石の数による段階的加点
        opponent_stones = self.count_stones_in_directions(board, x, y, z, opponent_accessible, 3 - player)
        if opponent_stones > 0:  # 相手の石のみ
            # 1つ目は2点、2つ目は4点（合計6点）、3つ目は6点（合計12点）
            for i in range(opponent_stones):
                reward += (i + 1) * 2  # 段階的加点
        
        # 2-3. 混在ライン上の石による加点・減点
        mixed_my_stones = self.count_stones_in_directions(board, x, y, z, mixed, player)
        mixed_opponent_stones = self.count_stones_in_directions(board, x, y, z, mixed, 3 - player)
        
        reward += mixed_my_stones * 2  # 自分の石による加点
        reward -= mixed_opponent_stones * 2  # 相手の石による減点
        
        # 3. 角と中央の4マスの位置ボーナス
        if (x == 0 or x == 3) and (y == 0 or y == 3):  # 角の4マス
            reward += 2
        elif (x == 1 or x == 2) and (y == 1 or y == 2):  # 中央の4マス
            reward += 2
        
        # 4. ダブルリーチ報酬（自分の石が2個以上あるラインが複数ある場合）
        double_reach_lines = self.count_double_reach_lines(board, x, y, z, player)
        if double_reach_lines >= 2:  # 2個目以降は100点加点
            reward += (double_reach_lines - 1) * 100  # 2個目以降=100点
        
        # 5. ダブルリーチ妨害（相手の石が2個以上あるラインが複数ある場合）
        opponent_double_reach_lines = self.count_opponent_double_reach_lines(board, x, y, z, player)
        if opponent_double_reach_lines >= 2:  # 2個目以降は100点加点
            reward += (opponent_double_reach_lines - 1) * 100  # 2個目以降=100点
        
        # 6. 罠回避（相手の勝利手を避ける）
        opponent_winning_moves = self.check_opponent_winning_moves_after_my_move(board, x, y, z, player)
        if opponent_winning_moves > 0:
            reward -= opponent_winning_moves * 100  # 勝利手1個=100点減点
        
        return reward
    
    def get_max_opponent_reward(self, board: Board, x: int, y: int, z: int, opponent: int, depth: int = 0) -> int:
        """相手が得られる最大報酬を計算"""
        # 仮想的に自分の石を置く
        temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        temp_board[z][y][x] = 3 - opponent  # 自分の石を置く
        
        max_reward = 0
        
        # 相手の全手を試して最大報酬を取得
        for opp_x in range(4):
            for opp_y in range(4):
                if self.can_place_stone(temp_board, opp_x, opp_y):
                    opp_z = self.get_height(temp_board, opp_x, opp_y)
                    # 修正: evaluate_position を再帰呼び出し
                    opponent_reward = self.evaluate_position(temp_board, opp_x, opp_y, opp_z, opponent, depth + 1)
                    max_reward = max(max_reward, opponent_reward)
        
        return max_reward
    
    def evaluate_position(self, board: Board, x: int, y: int, z: int, player: int, depth: int = 0) -> int:
        """指定位置の重み（点数）を計算"""
        # 再帰の深さ制限（4手先まで）
        if depth >= 3:
            return 0
        
        # 減衰率の計算
        decay_rate = 0.9 ** depth  # depth=0: 1.0, depth=1: 0.9, depth=2: 0.81, depth=3: 0.729
        
        # 自分の報酬を計算
        my_reward = self.calculate_reward(board, x, y, z, player)
        
        # 相手の最大報酬を計算（常に再帰）
        opponent = 3 - player
        max_opponent_reward = self.get_max_opponent_reward(board, x, y, z, opponent, depth)
        
        # 自分の報酬 - 相手の最大報酬（重み付き）
        result = my_reward - max_opponent_reward * 0.5
        return result * decay_rate
    
    def find_highest_line_access_move(self, board: Board, player: int):
        """最も高い重み（点数）の位置を探す"""
        best_move = None
        max_score = -1
        
        for x in range(4):
            for y in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    score = self.evaluate_position(board, x, y, z, player, 0)
                    
                    if score > max_score:
                        max_score = score
                        best_move = (x, y)
        
        return best_move
    
    def print_opponent_interference(self, board: Board, player: int) -> None:
        """各マスで妨害できる相手の石数を表示"""
        print(f"\n🚫 プレイヤー{player}の各マスで妨害できる相手の石数:")
        print("  x→   0 1 2 3    （値＝妨害できる相手の石数）")
        
        for y in range(3, -1, -1):
            print(f"y={y} |", end=" ")
            for x in range(4):
                if self.can_place_stone(board, x, y):
                    z = self.get_height(board, x, y)
                    opponent_stones = self.count_opponent_stones_in_lines(board, x, y, z, player)
                    print(f"{opponent_stones:2d}", end=" ")
                else:
                    print(" .", end=" ")
            print()
    
    def find_winning_move(self, board: Board, player: int):
        """勝利できる手を探す"""
        for x in range(4):
            for y in range(4):
                if self.can_place_stone(board, x, y):
                    # 仮想的に石を置いてみる
                    temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
                    z = self.get_height(board, x, y)
                    temp_board[z][y][x] = player
                    
                    if self.check_win(temp_board, x, y, z, player):
                        return (x, y)
        return None
    
    def find_center_move(self, board: Board):
        """中央付近の空いている位置を探す"""
        center_positions = [(1, 1), (1, 2), (2, 1), (2, 2), (0, 1), (1, 0), (2, 3), (3, 2)]
        
        for x, y in center_positions:
            if self.can_place_stone(board, x, y):
                return (x, y)
        return None
    
    def find_first_available_move(self, board: Board):
        """最初に見つかった空いている位置に置く"""
        for x in range(4):
            for y in range(4):
                if self.can_place_stone(board, x, y):
                    return (x, y)
        return (0, 0)  # フォールバック
    
    def can_place_stone(self, board: Board, x: int, y: int):
        """指定位置に石を置けるかチェック"""
        return board[3][y][x] == 0  # 最上段が空いているか
    
    def get_height(self, board: Board, x: int, y: int):
        """指定位置の現在の高さを取得"""
        for z in range(4):
            if board[z][y][x] == 0:
                return z
        return 4  # 満杯
    
    def check_win(self, board: Board, x: int, y: int, z: int, player: int):
        """指定位置で勝利条件を満たしているかチェック"""
        # 6方向の直線をチェック
        directions = [
            (1, 0, 0),   # x軸方向
            (0, 1, 0),   # y軸方向
            (0, 0, 1),   # z軸方向
            (1, 1, 0),   # xy対角線
            (1, 0, 1),   # xz対角線
            (0, 1, 1),   # yz対角線
            (1, 1, 1),   # xyz対角線
            (1, -1, 0),  # xy逆対角線
            (1, 0, -1),  # xz逆対角線
            (0, 1, -1),  # yz逆対角線
            (1, -1, -1), # xyz逆対角線
            (1, 1, -1),  # xy正、z負対角線
            (1, -1, 1),  # xy負、z正対角線
        ]
        
        for dx, dy, dz in directions:
            count = 1  # 現在の石を含む
            
            # 正方向にカウント
            nx, ny, nz = x + dx, y + dy, z + dz
            while 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4 and board[nz][ny][nx] == player:
                count += 1
                nx, ny, nz = nx + dx, ny + dy, nz + dz
            
            # 負方向にカウント
            nx, ny, nz = x - dx, y - dy, z - dz
            while 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 4 and board[nz][ny][nx] == player:
                count += 1
                nx, ny, nz = nx - dx, ny - dy, nz - dz
            
            if count >= 4:
                return True
        
        return False