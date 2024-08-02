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

def play_bingo(numbers, boards):
    for number in numbers:
        for board in boards:
            mark_number(board, number)
            if is_winner(board):
                return calculate_score(board, number)

# Read input from file
with open('bingo_input.txt', 'r') as file:
    input_str = file.read()

numbers, boards = parse_input(input_str)
score = play_bingo(numbers, boards)
print("Final score:", score)