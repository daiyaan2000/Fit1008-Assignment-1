# tests
from grid import Grid
from data_structures.referential_array import ArrayR
from layers import rainbow, black, lighten, invert, red, green, blue, sparkle, darken
# from data_structures.sorted_list_adt import  SortedList

from data_structures.array_sorted_list import ArraySortedList


class Test:
    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.data = [['X'] * cols for row in range(rows)]

    #def __iter__(self):
        #yield from self.data

    def __getitem__(self, row):
        return self.data[row]
        # what should this be?


def main():
    """ Main function """

    t = Test(2, 3)

    for x in t:
        print(x)

    print(t[0][1])

    mygrid = Grid("some", 4, 4)
    print(mygrid[1][0])
    mygrid[3][2] = 'Hello'
    # look at the following
    print(mygrid[3][2])

    r = rainbow()
    print(r)
if __name__ == "__main__":
    main()