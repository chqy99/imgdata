import json
import time
from pynput import keyboard, mouse
from threading import Thread, Lock
from typing import Dict, List, Optional
import os

class InputMonitor:
    def __init__(self, keyboard_interval: float = 0.1, mouse_interval: float = 0.1,
                 output_interval: float = 1.0, output_file: str = "input_events.json"):
        self.keyboard_interval = keyboard_interval
        self.mouse_interval = mouse_interval
        self.output_interval = output_interval
        self.output_file = output_file

        self.events: List[Dict] = []
        self.events_lock = Lock()

        self.is_running = False
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_listener: Optional[mouse.Listener] = None
        self.output_thread: Optional[Thread] = None

        self.last_keyboard_time = 0
        self.last_mouse_time = 0

    def on_press(self, key):
        current_time = time.time()
        if current_time - self.last_keyboard_time >= self.keyboard_interval:
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key)

            with self.events_lock:
                self.events.append({
                    'type': 'keyboard',
                    'event': 'press',
                    'key': key_char,
                    'timestamp': current_time
                })
            self.last_keyboard_time = current_time

    def on_release(self, key):
        current_time = time.time()
        if current_time - self.last_keyboard_time >= self.keyboard_interval:
            try:
                key_char = key.char
            except AttributeError:
                key_char = str(key)

            with self.events_lock:
                self.events.append({
                    'type': 'keyboard',
                    'event': 'release',
                    'key': key_char,
                    'timestamp': current_time
                })
            self.last_keyboard_time = current_time

    def on_move(self, x, y):
        current_time = time.time()
        if current_time - self.last_mouse_time >= self.mouse_interval:
            with self.events_lock:
                self.events.append({
                    'type': 'mouse',
                    'event': 'move',
                    'x': x,
                    'y': y,
                    'timestamp': current_time
                })
            self.last_mouse_time = current_time

    def on_click(self, x, y, button, pressed):
        current_time = time.time()
        if current_time - self.last_mouse_time >= self.mouse_interval:
            with self.events_lock:
                self.events.append({
                    'type': 'mouse',
                    'event': 'click',
                    'x': x,
                    'y': y,
                    'button': str(button),
                    'pressed': pressed,
                    'timestamp': current_time
                })
            self.last_mouse_time = current_time

    def on_scroll(self, x, y, dx, dy):
        current_time = time.time()
        if current_time - self.last_mouse_time >= self.mouse_interval:
            with self.events_lock:
                self.events.append({
                    'type': 'mouse',
                    'event': 'scroll',
                    'x': x,
                    'y': y,
                    'dx': dx,
                    'dy': dy,
                    'timestamp': current_time
                })
            self.last_mouse_time = current_time

    def save_events(self):
        while self.is_running:
            time.sleep(self.output_interval)
            with self.events_lock:
                if self.events:
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        for event in self.events:
                            json.dump(event, f)
                            f.write('\n')
                    self.events.clear()

    def start(self):
        if not self.is_running:
            self.is_running = True

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

            # Start keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.keyboard_listener.start()

            # Start mouse listener
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll
            )
            self.mouse_listener.start()

            # Start output thread
            self.output_thread = Thread(target=self.save_events)
            self.output_thread.daemon = True
            self.output_thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False

            if self.keyboard_listener:
                self.keyboard_listener.stop()
            if self.mouse_listener:
                self.mouse_listener.stop()

            # Save remaining events
            with self.events_lock:
                if self.events:
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        for event in self.events:
                            json.dump(event, f)
                            f.write('\n')
                    self.events.clear()