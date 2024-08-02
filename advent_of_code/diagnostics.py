def import_diagnostics(diagnostics_file):
    with open(diagnostics_file, "r") as file:
        readings = [line.strip() for line in file]
    return readings

def count_bits(bits_length, readings):
    bit_count = [{0: 0, 1: 0} for _ in range(bits_length)]
    
    for reading in readings:
        for current_index, bit in enumerate(reading):
            if int(bit) == 0:
                bit_count[current_index][0] += 1
            else:
                bit_count[current_index][1] += 1
    
    return bit_count

def get_least_common(bit_count):
    least_common = []
    for count in bit_count:
        if count[0] > count[1]:
            least_common.append(1)
        else:
            least_common.append(0)
    return ''.join(map(str, least_common))

def get_most_common(bit_count):
    most_common = []
    for count in bit_count:
        if count[0] > count[1]:
            most_common.append(0)
        else:
            most_common.append(1)
    return ''.join(map(str, most_common))

if __name__ == "__main__":
    print("----")

    diagnostics_joined = import_diagnostics('diagnostics.txt')

    bit_count = count_bits(len(diagnostics_joined[0]), diagnostics_joined)

    for i in bit_count:
        print(i)

    gamma = get_most_common(bit_count)
    epsilon = get_least_common(bit_count)

    print(gamma)
    print(epsilon)
    
    gamma_value = int(gamma, 2)
    epsilon_value = int(epsilon, 2)
    
    print(gamma_value)
    print(epsilon_value)

    print(gamma_value * epsilon_value)