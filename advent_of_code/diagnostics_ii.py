def import_diagnostics(diagnostics_file):
    with open(diagnostics_file, "r") as file:
        readings = [line.strip() for line in file]
    return readings

def filter_numbers(readings, bit_criteria, position):
    bit_count = {0: 0, 1: 0}
    
    for reading in readings:
        bit = int(reading[position])
        bit_count[bit] += 1

    if bit_criteria == 'most_common':
        if bit_count[1] >= bit_count[0]:
            desired_bit = '1'
        else:
            desired_bit = '0'
    elif bit_criteria == 'least_common':
        if bit_count[0] <= bit_count[1]:
            desired_bit = '0'
        else:
            desired_bit = '1'
    
    filtered_readings = [reading for reading in readings if reading[position] == desired_bit]
    return filtered_readings

def find_rating(readings, bit_criteria):
    filtered_readings = readings[:]
    bit_length = len(readings[0])
    
    for position in range(bit_length):
        filtered_readings = filter_numbers(filtered_readings, bit_criteria, position)
        if len(filtered_readings) == 1:
            break
    
    return filtered_readings[0]

if __name__ == "__main__":
    diagnostics_joined = import_diagnostics('diagnostics.txt')
    
    oxygen_generator_rating = find_rating(diagnostics_joined, 'most_common')
    co2_scrubber_rating = find_rating(diagnostics_joined, 'least_common')

    oxygen_generator_value = int(oxygen_generator_rating, 2)
    co2_scrubber_value = int(co2_scrubber_rating, 2)
    
    life_support_rating = oxygen_generator_value * co2_scrubber_value
    
    print(f"Oxygen Generator Rating (binary): {oxygen_generator_rating}")
    print(f"Oxygen Generator Rating (decimal): {oxygen_generator_value}")
    print(f"CO2 Scrubber Rating (binary): {co2_scrubber_rating}")
    print(f"CO2 Scrubber Rating (decimal): {co2_scrubber_value}")
    print(f"Life Support Rating: {life_support_rating}")