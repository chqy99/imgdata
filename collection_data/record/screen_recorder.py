import numpy as np
import mss
import subprocess
import time
from typing import Tuple, Optional
import cv2


class ScreenRecorder:
    def __init__(self,
                 output_file: str,
                 region: Optional[Tuple[int, int, int, int]] = None,
                 fps: int = 30,
                 max_frames: Optional[int] = None):
        """
        屏幕录制类，使用 mss + FFmpeg 输出标准 MP4
        Args:
            output_file: 输出文件路径（自动加 .mp4）
            region: 录制区域 (left, top, width, height)，None 表示全屏
            fps: 帧率
            max_frames: 最大帧数
        """
        if not output_file.lower().endswith(".mp4"):
            output_file += ".mp4"
        self.output_file = output_file

        self.region = region
        self.fps = fps
        self.max_frames = max_frames

        self.is_recording = False

    def start_recording(self):
        self.is_recording = True

        with mss.mss() as sct:
            # 获取屏幕区域
            if not self.region:
                screen = sct.monitors[0]
                self.region = (screen['left'], screen['top'], screen['width'], screen['height'])

            left, top, width, height = self.region

            # 修正宽高为偶数
            if width % 2 != 0:
                width += 1
            if height % 2 != 0:
                height += 1

            print(f"🎬 Recording region: ({left}, {top}, {width}, {height}), fps={self.fps}")

            # FFmpeg 命令
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",  # overwrite output
                "-f", "rawvideo",
                "-pix_fmt", "rgb24",
                "-s", f"{width}x{height}",
                "-r", str(self.fps),
                "-i", "-",  # 从 stdin 读取
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                "-preset", "veryfast",
                self.output_file
            ]

            process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

            frame_interval = 1.0 / self.fps
            total_frames = 0
            last_time = time.time()
            start_time = last_time

            try:
                while self.is_recording:
                    now = time.time()
                    if now - last_time >= frame_interval:
                        frame = np.array(sct.grab({
                            "left": left,
                            "top": top,
                            "width": self.region[2],
                            "height": self.region[3]
                        }))
                        # mss 返回 BGRA → 转 RGB
                        frame = frame[:, :, :3][:, :, ::-1]

                        # 保证帧大小为偶数
                        frame = cv2.resize(frame, (width, height))

                        # 写入 FFmpeg stdin
                        process.stdin.write(frame.tobytes())
                        total_frames += 1
                        last_time = now

                        if total_frames % self.fps == 0:
                            elapsed = now - start_time
                            print(f"⏱ Captured {total_frames} frames ({total_frames/elapsed:.2f} fps)")

                        if self.max_frames and total_frames >= self.max_frames:
                            print(f"🎯 Reached max_frames={self.max_frames}")
                            break
                    else:
                        time.sleep(0.001)
            except KeyboardInterrupt:
                print("🛑 Recording interrupted by user")
            finally:
                self.is_recording = False
                process.stdin.close()
                process.wait()
                duration = time.time() - start_time
                print(f"✅ Saved {total_frames} frames in {duration:.2f}s ({total_frames/duration:.2f} fps)")
                print(f"📦 Video saved to: {self.output_file}")

    def stop_recording(self):
        self.is_recording = False
