"""Hydrothermal vents"""

def import_vents(vents_data):
    with open(vents_data, "r") as file:
        vents = file.read()
    vents_list = vents.splitlines()
    return vents_list

def split_numbers(string):
    
    main_list = []

    no_arrow = string.split(" -> ")

    for i in no_arrow:
        main_list.append(i.split(","))

    return main_list

def segment(grid):

    




    

if __name__ == "__main__":

    grid = []
    for i in range(1000):
        grid.append([0 for i in range(1000)])



    vents = import_vents("vents.txt")
    for i in range(10):
        print(vents[i])


