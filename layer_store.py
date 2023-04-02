from __future__ import annotations
from abc import ABC, abstractmethod
from layer_util import Layer
from data_structures.referential_array import ArrayR
from data_structures.queue_adt import Queue, CircularQueue, TestQueue
from data_structures.stack_adt import Stack, ArrayStack, ArrayR
from data_structures.array_sorted_list import ArraySortedList
from layers import rainbow, black, lighten, invert, red, green, blue, sparkle, darken

class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass

class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - get_color: Get the color for a pixel in the layer.
    - special: Invert the color output for all layers.
    """

    def __init__(self) -> None:
        """
        Initialize the SetLayerStore object.
        """
        self.layer: Optional[Layer] = None
        self.layers: ArrayR[Optional[Layer]] = ArrayR(20)

    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the layer store.

        Args:
        - layer: The layer to be added.

        Returns:
        - A boolean indicating whether the addition was successful or not.
        """
        if layer is not None:
            self.layers[layer.index] = layer
            self.layer = layer
            return True
        else:
            return False

    def erase(self, layer: Layer) -> bool:
        """
        Remove a layer from the layer store.

        Args:
        - layer: The layer to be removed.

        Returns:
        - A boolean indicating whether the removal was successful or not.
        """
        if self.layers[layer.index] is not None:
            self.layers[layer.index] = None
            self.layer = None
            return True
        else:
            return False

    def get_color(self, start: Tuple[int, int, int], timestamp: int, x: int, y: int) -> Tuple[int, int, int]:
        """
        Get the color for a pixel in the layer.

        Args:
        - start: The starting color.
        - timestamp: The timestamp.
        - x: The x-coordinate of the pixel.
        - y: The y-coordinate of the pixel.

        Returns:
        - A tuple containing the RGB values of the color of the pixel.
        """
        if self.layer is not None:
            return self.layer.apply(start, timestamp, x, y)
        else:
            return start

    def special(self) -> None:
        """
        Invert the color output for all layers.
        """
        for i in range(len(self.layers)):
            if self.layers[i] is not None:
                self.layers[i].apply = self.invert_color(self.layers[i].apply)

    @staticmethod
    def invert_color(f):
        """
        Invert the color of a pixel.

        Args:
        - f: A function that applies a color to a pixel.

        Returns:
        - A function that inverts the color of a pixel.
        """
        def inv(start, timestamp, x, y):
            r, g, b = f(start, timestamp, x, y)
            return 255 - r, 255 - g, 255 - b

        return inv
class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self) -> None:
        """Initializes the store with an empty stack and queue."""
        self.stack: ArrayStack = ArrayStack(max_capacity=100)
        self.queue: CircularQueue = CircularQueue(max_capacity=100)

    def add(self, layer: Optional[Layer]) -> None:
        """Adds a layer to the store."""
        self.stack.push(layer)
        self.queue.append(layer)

    def special(self) -> None:
        """Adds the top layer to the bottom."""
        layer = self.stack.top()
        self.stack.pop()
        self.stack.push(layer)
        self.queue.append(layer)
        for i in range(len(self.queue) - 1):
            self.queue.append(self.queue.serve())

    def get_color(self, background_color: Tuple[int, int, int], x: int, y: int, z: int) -> Tuple[int, int, int]:
        """Returns the additive color of all layers in the store."""
        color = list(background_color)
        temp_stack = ArrayStack(max_capacity=100)
        while not self.stack.is_empty():
            layer = self.stack.pop()
            layer_color = layer.color if isinstance(layer, Layer) else (0, 0, 0)
            for i in range(3):
                color[i] += layer_color[i]
            temp_stack.push(layer)
        while not temp_stack.is_empty():
            self.stack.push(temp_stack.pop())
        return tuple(color)

    def erase(self, index: int) -> None:
        """Erases the layer at the given index."""
        # create temporary queue to store layers being removed
        temp_queue = CircularQueue(max_capacity=100)
        # remove layers from stack and add to temp_queue until reaching the layer at the index to be removed
        for i in range(len(self.stack)):
            layer = self.stack.peek()
            if i == index:
                self.stack.pop()
                break
            else:
                self.stack.pop()
                temp_queue.append(layer)
        # add back layers from temp_queue to stack in reverse order
        while not temp_queue.is_empty():
            self.stack.push(temp_queue.serve())
        # remove layers from queue and add back to queue until reaching the layer at the index to be removed
        for i in range(len(self.queue)):
            layer = self.queue.serve()
            if i == index:
                break
            else:
                self.queue.append(layer)
        # add back layers from temp_queue to queue
        while not temp_queue.is_empty():
            self.queue.append(temp_queue.serve())

class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    def __init__(self) -> None:
        """ SequenceLayerStore object initialiser. """

        # calling the initialiser for the LayerStore
        super().__init__()

        # initialising the internal array sorted list
        self.layers = ArraySortedList(100)

    def add(self, layer: Layer) -> bool:
        """ Add a layer to the store.
            Returns true if the SequenceLayerStore was actually changed.
        """

        # checking if layer already exists in the store
        if layer in self.layers:
            return False

        # adding layer to the store
        self.layers.add(layer)
        return True

    def get_color(self, start: int, timestamp: int, x: int, y: int) -> Tuple[int, int, int]:
        """ Returns the colour this square should show, given the current layers. """

        # creating a stack of valid layers based on start and timestamp
        valid_layers = Stack()
        curr_layer = None
        for layer in self.layers:
            if layer.timestamp <= timestamp and layer.start <= start:
                curr_layer = layer
                valid_layers.push(curr_layer)

        # processing layers in the order of their indices in valid_layers, starting from the top
        color = curr_layer.get_color(x, y)
        while not valid_layers.is_empty():
            layer = valid_layers.pop()
            if layer.get_color(x, y) != curr_layer.get_color(x, y):
                color = layer.get_color(x, y)
                curr_layer = layer

        return color

    def erase(self, layer: Layer) -> bool:
        """ Complete the erase action with this layer
            Returns true if the SequenceLayerStore was actually changed.
        """

        # removing layer from the store if it exists
        if layer in self.layers:
            self.layers.remove(layer)
            return True

        return False

    def special(self) -> None:
        """ Of all currently applied layers, remove the one with median `name`.
            In the event of two layers being the median names, pick the lexicographically smaller one.
        """

        # creating a queue to store all layers
        layer_queue = CircularQueueQueue()
        for layer in self.layers:
            layer_queue.append(layer)

        # sorting the queue of layers by their names
        layer_queue.sort(key=lambda x: x.name)

        # finding the median layer(s)
        median_layers = List()
        while not layer_queue.is_empty():
            median_layers.append(layer_queue.serve())
            if not layer_queue.is_empty():
                layer_queue.serve()
        median_layers.sort()

        # removing the median layer(s) from the store
        for layer in median_layers:
            self.erase(layer)
