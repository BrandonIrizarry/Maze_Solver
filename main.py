import tkinter as tk
import time
from typing import Callable, TypeAlias

Task: TypeAlias = Callable[[], int]

root = tk.Tk()
root.title("Maze Solver")

canvas = tk.Canvas(width=800, height=600)
canvas.pack()


class Loop:
    """A class used to properly manage the scope of 'is_running',
    which is used to exit the redisplay loop upon closing the GUI
    window.

    """
    def __init__(self):
        self.is_running = True

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

            time.sleep(2)


if __name__ == "__main__":
    loop = Loop()

    task_queue = [
        lambda: canvas.create_line(20, 30, 40, 50, width=2, fill="red"),
        lambda: canvas.create_line(70, 80, 90, 100, width=3, fill="blue")
    ]

    loop.run(root, task_queue)
