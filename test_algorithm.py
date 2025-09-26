#!/usr/bin/env python3
"""
アルゴリズムのテスト用スクリプト
"""

import time
from main import MyAI

def create_test_board():
    """テスト用の盤面を生成"""
    # 4x4x4の空の盤面
    board = [[[0 for x in range(4)] for y in range(4)] for z in range(4)]
    
    # いくつかの石を配置
    # プレイヤー1（先手）の石
    board[0][0][0] = 1  # (0,0,0)
    board[0][1][1] = 1  # (1,1,0)
    board[1][0][0] = 1  # (0,0,1)
    
    # プレイヤー2（後手）の石
    board[0][0][1] = 2  # (1,0,0)
    board[0][1][0] = 2  # (0,1,0)
    board[1][1][1] = 2  # (1,1,1)
    
    return board

def print_board(board):
    """盤面を表示"""
    print("\n" + "=" * 50)
    print("テスト盤面")
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

def test_evaluate_position():
    """evaluate_position関数のテスト"""
    print("\n" + "=" * 50)
    print("evaluate_position関数のテスト")
    print("=" * 50)
    
    ai = MyAI()
    board = create_test_board()
    print_board(board)
    
    # テストする位置
    test_positions = [
        (0, 0, 2),  # (x, y, z)
        (1, 1, 2),
        (2, 2, 0),
        (3, 3, 0)
    ]
    
    for x, y, z in test_positions:
        print(f"\n位置 ({x}, {y}, {z}) の評価:")
        
        # 各深度での評価
        for depth in range(5):
            start_time = time.time()
            score = ai.evaluate_position(board, x, y, z, 1, depth)
            end_time = time.time()
            
            print(f"  depth={depth}: スコア={score:6.1f}, 時間={end_time-start_time:.4f}秒")

def test_find_best_move():
    """find_best_move関数のテスト"""
    print("\n" + "=" * 50)
    print("find_best_move関数のテスト")
    print("=" * 50)
    
    ai = MyAI()
    board = create_test_board()
    print_board(board)
    
    # プレイヤー1の最適手を探す
    print("\nプレイヤー1の最適手を探索中...")
    start_time = time.time()
    best_move = ai.find_best_move(board, 1)
    end_time = time.time()
    
    print(f"最適手: {best_move}")
    print(f"探索時間: {end_time-start_time:.4f}秒")
    
    # プレイヤー2の最適手を探す
    print("\nプレイヤー2の最適手を探索中...")
    start_time = time.time()
    best_move = ai.find_best_move(board, 2)
    end_time = time.time()
    
    print(f"最適手: {best_move}")
    print(f"探索時間: {end_time-start_time:.4f}秒")

def test_calculate_reward():
    """calculate_reward関数のテスト"""
    print("\n" + "=" * 50)
    print("calculate_reward関数のテスト")
    print("=" * 50)
    
    ai = MyAI()
    board = create_test_board()
    print_board(board)
    
    # テストする位置
    test_positions = [
        (0, 0, 2),  # (x, y, z)
        (1, 1, 2),
        (2, 2, 0),
        (3, 3, 0)
    ]
    
    for x, y, z in test_positions:
        print(f"\n位置 ({x}, {y}, {z}) の報酬:")
        
        # プレイヤー1の報酬
        reward1 = ai.calculate_reward(board, x, y, z, 1)
        print(f"  プレイヤー1: {reward1}点")
        
        # プレイヤー2の報酬
        reward2 = ai.calculate_reward(board, x, y, z, 2)
        print(f"  プレイヤー2: {reward2}点")

def test_get_max_opponent_reward():
    """get_max_opponent_reward関数のテスト"""
    print("\n" + "=" * 50)
    print("get_max_opponent_reward関数のテスト")
    print("=" * 50)
    
    ai = MyAI()
    board = create_test_board()
    print_board(board)
    
    # テストする位置
    test_positions = [
        (0, 0, 2),  # (x, y, z)
        (1, 1, 2),
        (2, 2, 0),
        (3, 3, 0)
    ]
    
    for x, y, z in test_positions:
        print(f"\n位置 ({x}, {y}, {z}) での相手の最大報酬:")
        
        # プレイヤー1の視点での相手（プレイヤー2）の最大報酬
        max_reward1 = ai.get_max_opponent_reward(board, x, y, z, 2, 0)
        print(f"  プレイヤー1の視点: {max_reward1}点")
        
        # プレイヤー2の視点での相手（プレイヤー1）の最大報酬
        max_reward2 = ai.get_max_opponent_reward(board, x, y, z, 1, 0)
        print(f"  プレイヤー2の視点: {max_reward2}点")

def main():
    """メイン関数"""
    print("アルゴリズムテスト開始")
    print("=" * 50)
    
    try:
        # 各関数のテスト
        test_calculate_reward()
        test_get_max_opponent_reward()
        test_evaluate_position()
        test_find_best_move()
        
        print("\n" + "=" * 50)
        print("テスト完了")
        print("=" * 50)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
