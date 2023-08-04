import tkinter as tk

class BubbleWindow(tk.Tk):

    class BubbleCanvas(tk.Canvas):
        def __init__(self, master, width, height, bg="white"):
            super().__init__(master, width=width, height=height, bg=bg)
            self.master = master
            self.width = width
            self.height = height

        def create_circle(self, x, y, radius, color="black"):
            self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

    def __init__(self, width, height, step_function=None):
        super().__init__()

        self.title("Bubbles")
        self.setup_canvas(width, height)
        self.setup_label()

        self.after(1, self.event_loop)

        self.step_function = step_function # function to be called every frame
    
    @property
    def status_text(self):
        return self._status_text.get()
    
    @status_text.setter
    def status_text(self, text):
        self._status_text.set(text)

    def setup_canvas(self, width, height):
        self.canvas = self.BubbleCanvas(self, width=width, height=height)
        self.canvas.grid(row=0, column=0)

    def setup_label(self):
        self._status_text = tk.StringVar(value="Starting...")
        status_label = tk.Label(self, textvariable=self._status_text)
        status_label.grid(row=1, column=0)


    def event_loop(self):
        self.canvas.delete("all")
        if self.step_function is not None:
            self.step_function()
        self.after(1, self.event_loop)

    def start(self):
        self.mainloop()

    def stop(self):
        self.quit()