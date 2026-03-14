

import subprocess
from pathlib import Path

INPUT_ROOT = Path("dataset/test_footage")
OUTPUT_ROOT = Path("dataset/test_footage_demo")

TARGET_RESOLUTION = "960:540"
TARGET_FPS = 15
MAX_DURATION = 10  # seconds


def convert_video(input_path: Path, output_path: Path):

    command = [
        "ffmpeg",
        "-i", str(input_path),
        "-vf", f"scale={TARGET_RESOLUTION}",
        "-r", str(TARGET_FPS),
        "-t", str(MAX_DURATION),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "28",
        "-an",
        str(output_path)
    ]

    subprocess.run(command)


def process_folder(input_folder: Path, output_folder: Path):

    output_folder.mkdir(parents=True, exist_ok=True)

    for video in input_folder.glob("*"):

        if video.suffix.lower() not in [".mp4", ".avi", ".mov"]:
            continue

        output_path = output_folder / (video.stem + ".mp4")

        print(f"Converting {video.name}")

        convert_video(video, output_path)


def main():

    for category in ["surface", "underwater"]:

        process_folder(
            INPUT_ROOT / category,
            OUTPUT_ROOT / category
        )


if __name__ == "__main__":
    main()