import tkinter as tk
import time
import random
from typing import Callable, TypeAlias, Any
from enum import Enum, auto

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


class Command(Enum):
    INSTANT = auto(),
    DELAYED = auto()


class Loop:
    """A class used to properly manage the scope of 'is_running',
    which is used to exit the redisplay loop upon closing the GUI
    window.

    """
    def __init__(self, delay_secs=1):
        self.is_running = True
        self.delay_secs = delay_secs
        self.default_delay_secs = self.delay_secs

    def run(self, root: tk.Tk, task_queue: list[Task]):
        def close_handler():
            self.is_running = False

        root.protocol("WM_DELETE_WINDOW", close_handler)

        while self.is_running:
            root.update_idletasks()
            root.update()

            if task_queue:
                task = task_queue.pop(0)
                command = task()

                if command == Command.INSTANT:
                    self.delay_secs = 0
                elif command == Command.DELAYED:
                    self.delay_secs = self.default_delay_secs

            time.sleep(self.delay_secs)


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

    def open_direction(self, direction: Direction):
        canvas.itemconfig(self.perimeter[direction], fill="white")


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
        print(x, y)
        cell.open_direction(direction)


if __name__ == "__main__":
    loop = Loop(delay_secs=0.5)
    graph = Graph(canvas, 4, 4, 50)

    task_queue = [
        lambda: Command.INSTANT,
        lambda: graph.create(),
        lambda: Command.DELAYED,
        lambda: graph.remove_random_bar(),
        lambda: Command.INSTANT
    ]

    loop.run(root, task_queue)
