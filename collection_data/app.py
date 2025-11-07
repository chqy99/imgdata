import os
import json
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from threading import Thread, Event
from typing import Optional, Dict, Any

from window_manager import WindowManager, WindowInfo
from listening.input_monitor import InputMonitor
from record.screen_recorder import ScreenRecorder

class RecorderUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Screen Recorder with Input Monitoring')
        self.geometry('600x400')

        # Initialize components
        self.window_manager = WindowManager()
        self.input_monitor: Optional[InputMonitor] = None
        self.screen_recorder: Optional[ScreenRecorder] = None
        self.recorder_thread: Optional[Thread] = None
        self.input_monitor_thread: Optional[Thread] = None
        self.stop_event = Event()

        # Setup UI
        self.setup_ui()

        # Setup window list update
        self.after(1000, self.update_window_list)

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Window selection
        ttk.Label(main_frame, text="Select Window:").grid(row=0, column=0, sticky=tk.W)
        self.window_combo = ttk.Combobox(main_frame, width=40)
        self.window_combo.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.window_combo.bind('<<ComboboxSelected>>', self.on_window_selected)

        # FPS settings
        ttk.Label(main_frame, text="FPS:").grid(row=1, column=0, sticky=tk.W)
        self.fps_var = tk.StringVar(value="30")
        self.fps_spin = ttk.Spinbox(main_frame, from_=1, to=60, textvariable=self.fps_var, width=10)
        self.fps_spin.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Intervals frame
        intervals_frame = ttk.LabelFrame(main_frame, text="Monitoring Intervals", padding="5")
        intervals_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Keyboard interval
        ttk.Label(intervals_frame, text="Keyboard (s):").grid(row=0, column=0, sticky=tk.W)
        self.keyboard_var = tk.StringVar(value="0.1")
        self.keyboard_spin = ttk.Spinbox(intervals_frame, from_=0.01, to=1.0, increment=0.01,
                                       textvariable=self.keyboard_var, width=10)
        self.keyboard_spin.grid(row=0, column=1, sticky=tk.W, padx=5)

        # Mouse interval
        ttk.Label(intervals_frame, text="Mouse (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.mouse_var = tk.StringVar(value="0.1")
        self.mouse_spin = ttk.Spinbox(intervals_frame, from_=0.01, to=1.0, increment=0.01,
                                    textvariable=self.mouse_var, width=10)
        self.mouse_spin.grid(row=0, column=3, sticky=tk.W)

        # Output interval
        ttk.Label(intervals_frame, text="Output (s):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.output_var = tk.StringVar(value="1.0")
        self.output_spin = ttk.Spinbox(intervals_frame, from_=0.1, to=5.0, increment=0.1,
                                     textvariable=self.output_var, width=10)
        self.output_spin.grid(row=0, column=5, sticky=tk.W)

        # Output directory
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W)
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(self.output_dir, exist_ok=True)

        self.output_path = ttk.Label(output_frame, text=self.output_dir)
        self.output_path.grid(row=0, column=1, sticky=tk.W, padx=5)

        self.change_output_btn = ttk.Button(output_frame, text="Change",
                                          command=self.change_output_directory)
        self.change_output_btn.grid(row=0, column=2, sticky=tk.E)

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.start_btn = ttk.Button(button_frame, text="Start Recording",
                                  command=self.start_recording)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="Stop Recording",
                                 command=self.stop_recording, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def update_window_list(self):
        try:
            windows = self.window_manager.list_windows()
            current_selection = self.window_combo.get()

            # Update combobox values
            window_titles = [w.title for w in windows]
            self.window_combo['values'] = window_titles            # Try to restore previous selection
            if current_selection in window_titles:
                self.window_combo.set(current_selection)
            elif window_titles:
                self.window_combo.set(window_titles[0])
        finally:
            # Schedule next update
            self.after(1000, self.update_window_list)

    def on_window_selected(self, event=None):
        window = self.get_selected_window()
        if window:
            try:
                self.window_manager.focus_window(window.title, window.index)
            except Exception as e:
                print(f"Error focusing window: {e}")

    def change_output_directory(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_path['text'] = dir_path

    def get_selected_window(self) -> Optional[WindowInfo]:
        title = self.window_combo.get()
        windows = self.window_manager.list_windows()
        for window in windows:
            if window.title == title:
                return window
        return None

    def start_recording(self):
        # Get selected window
        window_data = self.get_selected_window()
        if not window_data:
            return

        # Create output filenames
        timestamp = int(time.time())
        video_file = os.path.join(self.output_dir, f'recording_{timestamp}.mp4')
        input_file = os.path.join(self.output_dir, f'inputs_{timestamp}.json')

        rect_info = window_data.rect.to_dict()
        region = (
            rect_info['left'],
            rect_info['top'],
            rect_info['width'],
            rect_info['height']
        )

        # Reset stop event
        self.stop_event.clear()

        # Start input monitoring
        self.input_monitor = InputMonitor(
            keyboard_interval=float(self.keyboard_var.get()),
            mouse_interval=float(self.mouse_var.get()),
            output_interval=float(self.output_var.get()),
            output_file=input_file,
            region=region
        )

        def input_monitor_thread():
            self.input_monitor.start()

        self.input_monitor_thread = Thread(target=input_monitor_thread)
        self.input_monitor_thread.start()

        # Start screen recording
        # Ensure window is active and get geometry
        try:
            self.window_manager.focus_window(window_data.title, window_data.index)
            time.sleep(0.5)  # Give window manager time to focus the window
        except Exception as e:
            print(f"Error focusing window: {e}")

        # Refresh region in case the window manager adjusted geometry when focusing
        rect = window_data.rect.to_dict()
        region = (
            rect['left'],
            rect['top'],
            rect['width'],
            rect['height']
        )
        self.input_monitor.set_region(region)
        self.screen_recorder = ScreenRecorder(
            output_file=video_file,
            region=(rect['left'], rect['top'],
                   rect['width'], rect['height']),
            fps=int(self.fps_var.get())
        )

        def recorder_thread():
            self.screen_recorder.start_recording()

        self.recorder_thread = Thread(target=recorder_thread)
        self.recorder_thread.start()

        # Update UI
        self.start_btn['state'] = tk.DISABLED
        self.stop_btn['state'] = tk.NORMAL
        self.window_combo['state'] = tk.DISABLED
        self.change_output_btn['state'] = tk.DISABLED

    def stop_recording(self):
        if self.input_monitor:
            self.input_monitor.stop()
            if self.input_monitor_thread and self.input_monitor_thread.is_alive():
                self.input_monitor_thread.join()
            self.input_monitor = None
            self.input_monitor_thread = None

        if self.screen_recorder:
            self.screen_recorder.stop_recording()
            if self.recorder_thread and self.recorder_thread.is_alive():
                self.recorder_thread.join()
            self.screen_recorder = None
            self.recorder_thread = None

        # Update UI
        self.start_btn['state'] = tk.NORMAL
        self.stop_btn['state'] = tk.DISABLED
        self.window_combo['state'] = tk.NORMAL
        self.change_output_btn['state'] = tk.NORMAL

    def on_closing(self):
        self.stop_recording()
        self.destroy()

if __name__ == '__main__':
    app = RecorderUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
