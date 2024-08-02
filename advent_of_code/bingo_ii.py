import numpy as np

def parse_input(input_str):
    parts = input_str.strip().split("\n\n")
    numbers = list(map(int, parts[0].split(',')))
    boards = []

    for part in parts[1:]:
        board = []
        for line in part.split('\n'):
            board.append(list(map(int, line.split())))
        boards.append(np.array(board))

    return numbers, boards

def mark_number(board, number):
    board[board == number] = -1

def is_winner(board):
    for row in board:
        if np.all(row == -1):
            return True
    for col in board.T:
        if np.all(col == -1):
            return True
    return False

def calculate_score(board, last_number):
    unmarked_sum = np.sum(board[board != -1])
    return unmarked_sum * last_number

def play_bingo_last_winner(numbers, boards):
    boards_won = [False] * len(boards)
    last_score = 0

    for number in numbers:
        for idx, board in enumerate(boards):
            if not boards_won[idx]:
                mark_number(board, number)
                if is_winner(board):
                    boards_won[idx] = True
                    last_score = calculate_score(board, number)

    return last_score

# Read input from file
with open('bingo_input.txt', 'r') as file:
    input_str = file.read()

numbers, boards = parse_input(input_str)
last_winner_score = play_bingo_last_winner(numbers, boards)
print("Final score of the last winning board:", last_winner_score)