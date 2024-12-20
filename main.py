import tkinter as tk
import random
from typing import Callable, TypeAlias, Any
from enum import Enum, auto
from functools import partialmethod


Task: TypeAlias = Callable[[], int | Any | None]

cell_size = 50
num_columns = 4
num_rows = 4

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


class Graph:
    def __init__(self, canvas: tk.Canvas, num_columns, num_rows, cell_size):
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.graph: list[list[Cell]] = []

        for x in range(num_columns):
            self.graph.append([])

            for y in range(num_rows):
                self.graph[-1].append(Cell(canvas, x + 1, y + 1, cell_size))

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


if __name__ == "__main__":
    graph = Graph(canvas, 4, 4, 50)

    task_queue = [
        lambda: graph.create(),
    ]

    for i in range(10):
        task_queue.append(lambda: graph.remove_random_bar())

    def animate():
        if task_queue:
            task = task_queue.pop(0)
            task()

        canvas.after(500, animate)

    animate()
    root.mainloop()
