import tkinter as tk
import time
from typing import Callable, TypeAlias
from enum import Enum, auto

Task: TypeAlias = Callable[[], int]

root = tk.Tk()
root.title("Maze Solver")

canvas = tk.Canvas(width=800, height=600)
canvas.pack()


class Direction(Enum):
    NORTH = auto(),
    SOUTH = auto(),
    EAST = auto(),
    WEST = auto()


class Loop:
    """A class used to properly manage the scope of 'is_running',
    which is used to exit the redisplay loop upon closing the GUI
    window.

    """
    def __init__(self, delay_secs=1):
        self.is_running = True
        self.delay_secs = delay_secs

    def run(self, root: tk.Tk, task_queue: list[Task]):
        def close_handler():
            self.is_running = False

        root.protocol("WM_DELETE_WINDOW", close_handler)

        while self.is_running:
            root.update_idletasks()
            root.update()

            if task_queue:
                task = task_queue.pop(0)
                task()
            else:
                # Change this to 0, so we can close the window without
                # there being a noticeable delay.
                self.delay_secs = 0

            time.sleep(self.delay_secs)


class Line:
    def __init__(self, canvas: tk.Canvas, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.canvas = canvas

    def create(self):
        self.line = self.canvas.create_line(self.x1,
                                            self.y1,
                                            self.x2,
                                            self.y2,
                                            width=2,
                                            fill="red")

    def hide(self):
        self.canvas.itemconfig(self.line, fill="gray")


class Cell:
    def __init__(self, canvas: tk.Canvas, x, y, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size

    def create(self):
        self.perimeter = {
            Direction.NORTH: self.canvas.create_line(self.x,
                                                     self.y,
                                                     self.x + 1,
                                                     self.y,
                                                     width=2,
                                                     fill="black"),
            Direction.SOUTH: self.canvas.create_line(self.x,
                                                     self.y + 1,
                                                     self.x + 1,
                                                     self.y + 1,
                                                     width=2,
                                                     fill="black"),
            Direction.EAST: self.canvas.create_line(self.x + 1,
                                                    self.y,
                                                    self.x + 1,
                                                    self.y + 1,
                                                    width=2,
                                                    fill="black"),
            Direction.WEST: self.canvas.create_line(self.x,
                                                    self.y,
                                                    self.x,
                                                    self.y + 1,
                                                    width=2,
                                                    fill="black"),
            }

        for line in self.perimeter.values():
            canvas.scale(line, self.x, self.y, self.size, self.size)

    def hide(self, direction: Direction):
        canvas.itemconfig(self.perimeter[direction], fill="white")


if __name__ == "__main__":
    loop = Loop(delay_secs=0.5)

    line1 = Line(canvas, 20, 30, 100, 150)
    line2 = Line(canvas, 70, 80, 120, 140)

    cell1 = Cell(canvas, 30, 30, 50)

    task_queue = [
        lambda: line1.create(),
        lambda: line2.create(),
        lambda: line1.hide(),
        lambda: line2.hide(),
        lambda: cell1.create(),
        lambda: cell1.hide(Direction.NORTH)
    ]

    loop.run(root, task_queue)
