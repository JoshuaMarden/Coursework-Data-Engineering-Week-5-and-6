def import_depths(depth_file):
    with open(depth_file, "r") as file:
        depths = [int(record.strip()) for record in file]
    return depths


def depth_change_counter(depths_list):
    increase_counter = 0

    for index in range(1, len(depths_list)):
        if depths_list[index] > depths_list[index - 1]:
            increase_counter += 1

    return increase_counter


if __name__ == "__main__":
    depths_list = import_depths('depth_readings.txt')
    count = depth_change_counter(depths_list)
    print(count)
