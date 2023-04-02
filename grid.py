from __future__ import annotations
from data_structures.referential_array import ArrayR
from data_structures.array_sorted_list import ArraySortedList
from layer_store import SetLayerStore
class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 1
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style: str, x: int, y: int) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.
        Should also intialise the brush size to the DEFAULT provided as a class variable.
        """

        #checking for correcr draw style
        if draw_style in self.DRAW_STYLE_OPTIONS:
            self.draw_style = draw_style
        else:
            print('Draw style not correct')
        self.brush_size = self.DEFAULT_BRUSH_SIZE

        #a grid is created based on the number of rows and columns i.e. x and y axis
        #Then each box in the grid is set with a layer depending on the draw style used
        self.rows = x
        self.cols = y
        self.grid = ArrayR(self.rows)

        for i in range(0, self.rows):
            self.grid[i] = ArrayR(self.cols)
            for j in range(self.cols):
                if self.draw_style == 'Set':
                    self.grid[i][j] = SetLayerStore()
                elif self.draw_style == 'Additive':
                    self.grid[i][j] = AdditiveLayerStore()
                elif self.draw_style == 'Sequential':
                    self.grid[i][j] = SequenceLayerStore()

    #the two magic methods below access each square in the grid. __getitem__ returns the layer implemented in the grid while __setitem__ enters a layer on the grid.
    def __getitem__(self, key: int) -> ArrayR[LayerStore]:
        """
        Return the specified row of the grid.

        Parameters:
        key (int): The index of the row to return.

        Returns:
        The specified row of the grid.
        """
        return self.grid[key]

    def __setitem__(self, item: LayerStore, row: int, col: int) -> None:
        """
        Set the layer store of a given position in the grid.

        Parameters:
        item (LayerStore): The layer store to set.
        row (int): The row index of the grid.
        col (int): The column index of the grid.

        """
        self.grid[row][col] = item

    # raise NotImplementedError()

    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size < self.MAX_BRUSH:
            self.brush_size += 1

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size > self.MIN_BRUSH:
            self.brush_size -= 1

    def special(self):
        """
        Activate the special affect on all grid squares.
        """
        raise NotImplementedError()
