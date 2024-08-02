def import_route(route_file):
    with open(route_file, "r") as file:
        directions = [line for line in file]
    return directions


def sum_numbers_for_condition(directions, condition):

    total = 0
    for command in directions:
        if condition in command:
            split_string = command.split(" ")

            total += int(split_string[1])

    return total


if __name__ == "__main__":

    directions = import_route('route.txt')

    total_down = sum_numbers_for_condition(directions, "down")
    total_up = sum_numbers_for_condition(directions, "up")
    total_forward = sum_numbers_for_condition(directions, "forward")

    depth = total_down - total_up

    print(depth * total_forward)
