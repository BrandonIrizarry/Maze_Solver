import tkinter as tk
import random
from typing import Callable, TypeAlias, Any, Generator
from enum import Enum, auto
from functools import partialmethod


Task: TypeAlias = Callable[[], int | Any | None]
Point: TypeAlias = tuple[int, int]


def configure_gui(num_columns, num_rows, cell_size):
    width = cell_size * num_columns
    height = cell_size * num_rows

    root = tk.Tk()
    root.geometry(f"{width + cell_size * 4}x{height + cell_size * 4}")
    root.title("Maze Solver")

    canvas = tk.Canvas(root,
                       width=width + cell_size * 2,
                       height=height + cell_size * 2,
                       bg="white")

    canvas.pack(anchor=tk.CENTER, expand=True)

    # Define the graph here as well.
    graph = Graph(canvas, num_columns, num_rows, cell_size)

    return root, canvas, graph


class Direction(Enum):
    NORTH = auto(),
    SOUTH = auto(),
    EAST = auto(),
    WEST = auto()


class Cell:
    def __init__(self, canvas: tk.Canvas, x, y, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size

    def create(self):
        x_scaled = self.x * self.size
        y_scaled = self.y * self.size

        northwest = (x_scaled, y_scaled)
        northeast = (x_scaled + self.size, y_scaled)
        southwest = (x_scaled, y_scaled + self.size)
        southeast = (x_scaled + self.size, y_scaled + self.size)

        self.perimeter = {
            Direction.NORTH: self.canvas.create_line(northwest,
                                                     northeast,
                                                     width=2,
                                                     fill="black"),
            Direction.SOUTH: self.canvas.create_line(southwest,
                                                     southeast,
                                                     width=2,
                                                     fill="black"),
            Direction.EAST: self.canvas.create_line(northeast,
                                                    southeast,
                                                    width=2,
                                                    fill="black"),
            Direction.WEST: self.canvas.create_line(northwest,
                                                    southwest,
                                                    width=2,
                                                    fill="black"),
            }

    def _configure_direction(self, direction: Direction, do_open: bool):
        # For some reason, 'Canvas.itemconfig' doesn't work when
        # configuring Direction.EAST. So we instead create a new line
        # from scratch, and reassign to the appropriate perimeter
        # entry.
        x1, y1, x2, y2 = self.canvas.coords(self.perimeter[direction])
        line = self.canvas.create_line(x1, y1, x2, y2, width=2,
                                       fill="white" if do_open else "black")

        self.perimeter[direction] = line

    open_direction = partialmethod(_configure_direction, do_open=True)
    close_direction = partialmethod(_configure_direction, do_open=False)

    def compute_center(self) -> Point:
        """Return scaled center point.

        """
        x_scaled = self.x * self.size
        y_scaled = self.y * self.size

        center_x = x_scaled + self.size / 2
        center_y = y_scaled + self.size / 2

        return (center_x, center_y)

    def draw_connecting_line(self, dest_cell: "Cell", fill: str):
        cx, cy = self.compute_center()
        dx, dy = dest_cell.compute_center()

        self.canvas.create_line(cx, cy, dx, dy, width=2, fill=fill)

def get_neighbors(x, y, xlimit=1000, ylimit=1000):
    """Helper function to obtain neighboring 2D Cartesian coordinates
    within a certain boundary.

    """
    result = []

    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if (i == 0) ^ (j == 0):
                xprime = x + i
                yprime = y + j

                if xprime in range(xlimit) and yprime in range(ylimit):
                    result.append((xprime, yprime))

    return result


class Graph:
    def __init__(self, canvas: tk.Canvas, num_columns, num_rows, cell_size):
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.graph: list[list[Cell]] = []
        self.open_neighbors: dict[Point, list[Point]] = dict()

        for x in range(num_columns):
            self.graph.append([])

            for y in range(num_rows):
                self.graph[-1].append(Cell(canvas, x + 1, y + 1, cell_size))

                self.open_neighbors[(x, y)] = []

    def create(self):
        for column in self.graph:
            for cell in column:
                cell.create()

    def remove_random_bar(self) -> None:
        x: int = random.randint(0, self.num_columns - 1)
        y: int = random.randint(0, self.num_rows - 1)
        direction: Direction = random.choice(list(Direction))
        cell = self.graph[x][y]

        cell.open_direction(direction)

    def open_path(self) -> Generator:
        """Perform a random depth-first search on this graph, opening
        a path that will be the maze.

        To integrate each individual call to 'Cell.open_direction'
        with the animation loop, this method is implemented as a
        generator.

        """
        visited: set[Point] = set()

        # Use an ordinary list as a stack, representing the history of
        # visited nodes.
        history_stack: list[Point] = [(0, 0)]
        visited.add((0, 0))

        while history_stack != []:
            neighbor_coords: list[Point] = []
            x, y = None, None

            # Move backwards along the stack until we find a
            # searchable node in the graph.
            while True:
                x, y = history_stack[-1]
                neighbor_coords = get_neighbors(x,
                                                y,
                                                self.num_columns,
                                                self.num_rows)

                neighbor_coords = [n for n in neighbor_coords
                                   if n not in visited]

                if neighbor_coords != []:
                    break

                history_stack.pop()

                if history_stack == []:
                    return

            xn, yn = random.choice(neighbor_coords)

            # Open a path from the current cell to the selected
            # neighbor.
            #
            # This is also where the draw-directive takes place.
            if xn == x and yn == y - 1:
                self.graph[x][y].open_direction(Direction.NORTH)
            elif xn == x and yn == y + 1:
                self.graph[x][y].open_direction(Direction.SOUTH)
            elif yn == y and xn == x + 1:
                self.graph[x][y].open_direction(Direction.EAST)
            elif yn == y and xn == x - 1:
                self.graph[x][y].open_direction(Direction.WEST)

            yield

            history_stack.append((xn, yn))
            visited.add((xn, yn))

            self.open_neighbors[(x, y)].append((xn, yn))

    def solve(self) -> Generator:
        if self.open_neighbors[(0, 0)] == []:
            raise Exception("Maze hasn't been constructed yet")

        visited: set[Point] = set()

        # Use an ordinary list as a stack, representing the history of
        # visited nodes.
        history_stack: list[Point] = [(0, 0)]
        visited.add((0, 0))

        # The maze is considered solved when the DFS reaches the
        # bottom-right cell.
        destination: Point = (self.num_columns - 1, self.num_rows - 1)

        while history_stack != []:
            neighbor_coords: list[Point] = []
            x, y = None, None

            # Move backwards along the stack until we find a
            # searchable node in the graph.
            while True:
                x, y = history_stack[-1]
                neighbor_coords = self.open_neighbors[(x, y)]
                neighbor_coords = [n for n in neighbor_coords
                                   if n not in visited]

                if neighbor_coords != []:
                    break

                history_stack.pop()

                xb, yb = history_stack[-1]
                cell = self.graph[xb][yb]

                self.graph[x][y].draw_connecting_line(cell, "gray")

                yield

                if history_stack == []:
                    return


            xn, yn = neighbor_coords[0]
            neighbor_cell = self.graph[xn][yn]

            self.graph[x][y].draw_connecting_line(neighbor_cell, fill="red")
            yield

            if (xn, yn) == destination:
                return

            history_stack.append((xn, yn))
            visited.add((xn, yn))


if __name__ == "__main__":
    root, canvas, graph = configure_gui(100, 100, 5)

    # This is essentially a task queue, but implemented as a
    # generator.
    def tasks():
        graph.create()
        yield
        steps = graph.open_path()

        while True:
            try:
                next(steps)
            except StopIteration:
                break

            yield

        solution = graph.solve()

        while True:
            try:
                next(solution)
            except StopIteration:
                break

            yield

    iter = tasks()

    def animate(delay_millis):
        try:
            next(iter)
        except StopIteration:
            return

        canvas.after(delay_millis, animate, delay_millis)

    animate(1)
    root.mainloop()
