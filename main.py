import tkinter as tk


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

    def run(self, root: tk.Tk):
        def close_handler():
            self.is_running = False

        root.protocol("WM_DELETE_WINDOW", close_handler)

        while self.is_running:
            root.update_idletasks()
            root.update()


if __name__ == "__main__":
    loop = Loop()
    loop.run(root)
