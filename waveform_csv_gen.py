import threading
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from tkinter import Tk, messagebox, simpledialog
from tkinter.filedialog import askopenfilenames
import mplcursors  # Required for tooltips

class FileNavigator:
    def __init__(self, file_paths, fps=30):
        self.file_paths = file_paths
        self.index = 0
        self.fps = fps
        self.speed = 1 / fps  # Convert FPS to delay in seconds
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.2, top=0.85)  # Adjust space to fit the file name
        self.plot_file()

        # Keyboard control
        self.key_pressed = None
        self.running = False
        self.thread = threading.Thread(target=self.keyboard_loop)
        self.thread.daemon = True
        self.thread.start()

        # Connect key press and release events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_key_release)

    def downsample_data(self, data, max_points=1000):
        """Downsample data to a manageable size for better performance."""
        if len(data) > max_points:
            step = len(data) // max_points
            return data.iloc[::step]
        return data

    def plot_file(self):
        self.ax.clear()
        try:
            file_path = self.file_paths[self.index]
            waveform_data = pd.read_csv(file_path, skiprows=5, header=None, names=["Time", "Amplitude"])

            # Downsample data for faster interactivity
            waveform_data = self.downsample_data(waveform_data)

            # Plot the data
            line, = self.ax.plot(waveform_data["Time"], waveform_data["Amplitude"], label="Waveform")
            self.ax.set_title("Oscilloscope Waveform")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Amplitude (V)")
            self.ax.grid(True)
            self.ax.legend()

            # Add file name as a title above the plot
            self.fig.suptitle(f"File: {file_path}", fontsize=10, y=0.95)

            # Add tooltip for hover functionality
            cursor = mplcursors.cursor(line, hover=True)
            cursor.connect("add", lambda sel: sel.annotation.set_text(
                f"Time: {sel.target[0]:.6f} s\nAmplitude: {sel.target[1]:.2f} V"
            ))
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', transform=self.ax.transAxes)
        self.fig.canvas.draw()

    def next_file(self):
        if self.index < len(self.file_paths) - 1:
            self.index += 1
            self.plot_file()

    def previous_file(self):
        if self.index > 0:
            self.index -= 1
            self.plot_file()

    def on_key_press(self, event):
        if event.key in ("right", "left"):
            self.key_pressed = event.key
            self.running = True

    def on_key_release(self, event):
        if event.key in ("right", "left"):
            self.key_pressed = None
            self.running = False

    def keyboard_loop(self):
        while True:
            if self.running and self.key_pressed:
                if self.key_pressed == "right":
                    self.next_file()
                elif self.key_pressed == "left":
                    self.previous_file()
                time.sleep(self.speed)  # Control navigation speed based on FPS

def browse_files():
    """Function to browse and select multiple files"""
    Tk().withdraw()  # Hide the main tkinter window
    file_paths = askopenfilenames(filetypes=[("CSV Files", "*.csv")])
    return file_paths

def main():
    # Ask the user to set FPS (optional)
    Tk().withdraw()  # Hide tkinter window
    fps = simpledialog.askinteger("Set FPS", "Enter frames per second (FPS):", minvalue=1, maxvalue=60, initialvalue=30)

    file_paths = browse_files()
    if file_paths:
        navigator = FileNavigator(file_paths, fps=fps)

        # Add navigation buttons
        axprev = plt.axes([0.3, 0.05, 0.1, 0.075])  # Position of "Previous" button
        axnext = plt.axes([0.6, 0.05, 0.1, 0.075])  # Position of "Next" button
        bprev = Button(axprev, 'Previous')
        bnext = Button(axnext, 'Next')
        bprev.on_clicked(lambda event: navigator.previous_file())
        bnext.on_clicked(lambda event: navigator.next_file())

        plt.show()
    else:
        messagebox.showinfo("No File", "No files were selected.")

if __name__ == "__main__":
    main()
