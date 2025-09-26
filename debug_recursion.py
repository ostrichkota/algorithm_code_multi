#!/usr/bin/env python3
"""
再帰の動作を詳細にデバッグするスクリプト
"""

import time
from main import MyAI

def create_simple_board():
    """シンプルなテスト盤面を生成"""
    board = [[[0 for x in range(4)] for y in range(4)] for z in range(4)]
    
    # 最小限の石を配置
    board[0][0][0] = 1  # プレイヤー1
    board[0][0][1] = 2  # プレイヤー2
    
    return board

def print_board(board):
    """盤面を表示"""
    print("\n盤面:")
    for z in range(3, -1, -1):
        print(f"Z={z}: ", end="")
        for y in range(4):
            for x in range(4):
                if board[z][y][x] == 0:
                    print("・", end="")
                elif board[z][y][x] == 1:
                    print("●", end="")
                elif board[z][y][x] == 2:
                    print("○", end="")
            print(" ", end="")
        print()

def debug_evaluate_position(ai, board, x, y, z, player, depth=0, indent=""):
    """evaluate_positionの動作をデバッグ"""
    print(f"{indent}evaluate_position(depth={depth}, player={player}, pos=({x},{y},{z}))")
    
    if depth >= 4:
        print(f"{indent}  → depth制限で停止: 0")
        return 0
    
    decay_rate = 0.9 ** depth
    print(f"{indent}  decay_rate={decay_rate:.3f}")
    
    # 自分の報酬を計算
    my_reward = ai.calculate_reward(board, x, y, z, player)
    print(f"{indent}  → 自分の報酬: {my_reward}")
    
    # 相手の最大報酬を計算（常に再帰）
    opponent = 3 - player
    print(f"{indent}  → 相手({opponent})の最大報酬を計算...")
    
    # 仮想的に自分の石を置く
    temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
    temp_board[z][y][x] = player
    
    max_reward = 0
    move_count = 0
    
    for opp_x in range(4):
        for opp_y in range(4):
            if ai.can_place_stone(temp_board, opp_x, opp_y):
                opp_z = ai.get_height(temp_board, opp_x, opp_y)
                move_count += 1
                
                print(f"{indent}    手{move_count}: 相手が({opp_x},{opp_y},{opp_z})に置く")
                
                # 再帰呼び出し
                opponent_reward = debug_evaluate_position(ai, temp_board, opp_x, opp_y, opp_z, opponent, depth + 1, indent + "      ")
                max_reward = max(max_reward, opponent_reward)
    
    # 自分の報酬 - 相手の最大報酬（重み付き）
    result = (my_reward - max_reward * 0.5) * decay_rate
    print(f"{indent}  → 最終計算: ({my_reward} - {max_reward} * 0.5) * {decay_rate:.3f} = {result:.1f}")
    return result

def test_recursion_expansion():
    """再帰の展開をテスト"""
    print("=" * 60)
    print("再帰の展開テスト")
    print("=" * 60)
    
    ai = MyAI()
    board = create_simple_board()
    print_board(board)
    
    # テスト位置
    test_x, test_y, test_z = 1, 1, 0
    
    print(f"\n位置({test_x}, {test_y}, {test_z})での再帰展開:")
    print("-" * 60)
    
    start_time = time.time()
    result = debug_evaluate_position(ai, board, test_x, test_y, test_z, 1, 0, "")
    end_time = time.time()
    
    print("-" * 60)
    print(f"最終結果: {result:.1f}")
    print(f"計算時間: {end_time - start_time:.4f}秒")

def count_possible_moves(ai, board):
    """可能な手の数をカウント"""
    count = 0
    for x in range(4):
        for y in range(4):
            if ai.can_place_stone(board, x, y):
                count += 1
    return count

def test_move_expansion():
    """手の展開をテスト"""
    print("\n" + "=" * 60)
    print("手の展開テスト")
    print("=" * 60)
    
    ai = MyAI()
    board = create_simple_board()
    print_board(board)
    
    print(f"初期盤面の可能な手数: {count_possible_moves(ai, board)}")
    
    # 各深度での手の展開を確認
    for depth in range(5):
        print(f"\ndepth={depth}での手の展開:")
        
        # 仮想的に石を置いて手の数を確認
        temp_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        if depth > 0:
            temp_board[0][1][0] = 1  # 仮想的に石を置く
        
        move_count = count_possible_moves(ai, temp_board)
        print(f"  可能な手数: {move_count}")

def main():
    """メイン関数"""
    try:
        test_recursion_expansion()
        test_move_expansion()
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
