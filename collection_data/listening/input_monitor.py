import json
import time
from pynput import keyboard, mouse
from threading import Thread, Lock
from typing import Dict, List, Optional, Tuple, Set
import os

class InputMonitor:
    def __init__(self, keyboard_interval: float = 0.1, mouse_interval: float = 0.1,
                 output_interval: float = 1.0, output_file: str = "input_events.json",
                 region: Optional[Tuple[int, int, int, int]] = None):
        self.keyboard_interval = keyboard_interval
        self.mouse_interval = mouse_interval
        self.output_interval = output_interval
        self.output_file = output_file
        self.region = region

        self.events: List[Dict] = []
        self.events_lock = Lock()

        self.is_running = False
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_listener: Optional[mouse.Listener] = None
        self.output_thread: Optional[Thread] = None

        self.last_keyboard_time = 0
        self.last_mouse_time = 0
        # Track currently pressed keys and per-key throttle timestamps
        self.pressed_keys: Set[str] = set()
        self.key_last_time: Dict[str, float] = {}

    # --- Keyboard helpers ---
    def _normalize_key(self, key) -> str:
        """Normalize pynput key/keycode into a concise, stable name.
        Examples: Key.ctrl_l -> 'Ctrl', Key.shift -> 'Shift', 'a' -> 'a', Key.f1 -> 'F1'."""
        try:
            # KeyCode with printable character
            if hasattr(key, 'char') and key.char is not None:
                return key.char
        except Exception:
            pass

        # Fallback to string form
        name = str(key)
        if name.startswith('Key.'):
            name = name[4:]
        # Unify left/right modifier keys and common specials
        aliases = {
            'ctrl': 'Ctrl', 'ctrl_l': 'Ctrl', 'ctrl_r': 'Ctrl',
            'shift': 'Shift', 'shift_l': 'Shift', 'shift_r': 'Shift',
            'alt': 'Alt', 'alt_l': 'Alt', 'alt_r': 'Alt',
            'cmd': 'Meta', 'cmd_l': 'Meta', 'cmd_r': 'Meta', 'super': 'Meta', 'cmd_r': 'Meta', 'super_l': 'Meta', 'super_r': 'Meta',
            'enter': 'Enter', 'return': 'Enter', 'space': 'Space', 'tab': 'Tab', 'esc': 'Esc', 'escape': 'Esc',
            'backspace': 'Backspace', 'delete': 'Delete', 'home': 'Home', 'end': 'End', 'page_up': 'PageUp', 'page_down': 'PageDown',
            'up': 'Up', 'down': 'Down', 'left': 'Left', 'right': 'Right'
        }
        if name in aliases:
            return aliases[name]
        if name.startswith('f') and name[1:].isdigit():
            return name.upper()  # F1-F24
        # Default: capitalize words joined by '-'
        return name.replace('_', ' ').title().replace(' ', '')

    def _sorted_pressed(self) -> List[str]:
        order = {'Ctrl': 0, 'Shift': 1, 'Alt': 2, 'Meta': 3}
        return sorted(self.pressed_keys, key=lambda k: (order.get(k, 4), k))

    def on_press(self, key):
        now = time.time()
        key_name = self._normalize_key(key)

        # Update current pressed set (prevent duplicates)
        if key_name not in self.pressed_keys:
            self.pressed_keys.add(key_name)

        # Per-key throttle to avoid auto-repeat flood, but don't block other keys
        last = self.key_last_time.get(key_name, 0)
        if now - last >= self.keyboard_interval:
            with self.events_lock:
                data = {
                    'type': 'keyboard',
                    'event': 'press',
                    'key': key_name,
                    'pressed_keys': self._sorted_pressed(),
                    'combo': '+'.join(self._sorted_pressed()) if len(self.pressed_keys) > 1 else key_name,
                    'timestamp': now
                }
                self.events.append(data)
            self.key_last_time[key_name] = now

    def on_release(self, key):
        now = time.time()
        key_name = self._normalize_key(key)

        # Remove from pressed set, but compute combo after removal to reflect state change
        if key_name in self.pressed_keys:
            self.pressed_keys.remove(key_name)

        last = self.key_last_time.get(key_name, 0)
        if now - last >= self.keyboard_interval:
            with self.events_lock:
                data = {
                    'type': 'keyboard',
                    'event': 'release',
                    'key': key_name,
                    'pressed_keys': self._sorted_pressed(),
                    'combo': '+'.join(self._sorted_pressed()) if len(self.pressed_keys) > 1 else (self._sorted_pressed()[0] if self.pressed_keys else ''),
                    'timestamp': now
                }
                self.events.append(data)
            self.key_last_time[key_name] = now

    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
        self.region = region

    def _is_point_in_region(self, x: float, y: float) -> bool:
        if not self.region:
            return True
        left, top, width, height = self.region
        px, py = int(x), int(y)
        return left <= px < left + width and top <= py < top + height

    def on_move(self, x, y):
        current_time = time.time()
        if current_time - self.last_mouse_time >= self.mouse_interval and self._is_point_in_region(x, y):
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
        if current_time - self.last_mouse_time >= self.mouse_interval and self._is_point_in_region(x, y):
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
        if current_time - self.last_mouse_time >= self.mouse_interval and self._is_point_in_region(x, y):
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
        first_timestamp = None
        while self.is_running:
            time.sleep(self.output_interval)
            with self.events_lock:
                if self.events:
                    if first_timestamp is None and self.events:
                        first_timestamp = self.events[0]['timestamp']
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        for event in self.events:
                            if first_timestamp is not None:
                                event['timestamp'] = event['timestamp'] - first_timestamp
                            json.dump(event, f)
                            f.write('\n')
                    self.events.clear()

    def start(self):
        if not self.is_running:
            self.is_running = True

            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(self.output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

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
            first_timestamp = None
            with self.events_lock:
                if self.events:
                    if first_timestamp is None and self.events:
                        first_timestamp = self.events[0]['timestamp']
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        for event in self.events:
                            if first_timestamp is not None:
                                event['timestamp'] = event['timestamp'] - first_timestamp
                            json.dump(event, f)
                            f.write('\n')
                    self.events.clear()