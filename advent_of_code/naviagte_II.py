def import_route(route_file):
    with open(route_file, "r") as file:
        directions = [line.strip() for line in file]
    return directions


def track_aim(current_aim, new_movement):

    movement_parts = new_movement.split(" ")

    if 'down' in movement_parts[0]:
        current_aim += int(movement_parts[1])
    else:
        current_aim -= int(movement_parts[1])

    return current_aim


def move(current_location, current_depth, current_aim, new_movement):

    movement_parts = new_movement.split(" ")

    current_location += int(movement_parts[1])
    current_depth += current_aim * int(movement_parts[1])

    return current_location, current_depth


def aim_and_move(current_location, current_depth, current_aim, new_movement):

    if 'forward' in new_movement:
        current_location, current_depth = move(current_location, current_depth, current_aim, new_movement)
    else:
        current_aim = track_aim(current_aim, new_movement)

    return current_location, current_depth, current_aim


if __name__ == "__main__":

    sample_directions = [
        "forward 5",
        "down 5",
        "forward 8",
        "up 3",
        "down 8",
        "forward 2"
    ]

    directions = import_route('route.txt')
    # directions = sample_directions  # for testing 

    current_aim = 0
    current_location = 0
    current_depth = 0

    for instruction in directions:
        current_location, current_depth, current_aim = aim_and_move(
            current_location, current_depth, current_aim, instruction)

    print(f"Horizontal Position: {current_location}")
    print(f"Depth: {current_depth}")
    print(f"Result (Position * Depth): {current_location * current_depth}")