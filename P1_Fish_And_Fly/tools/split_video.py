import subprocess
from pathlib import Path

INPUT_ROOT = Path("dataset/test_footage")
OUTPUT_ROOT = Path("dataset/test_footage_split")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

SEGMENT_TIME = 10


def split_video(video_path: Path, output_folder: Path):

    output_folder.mkdir(parents=True, exist_ok=True)

    output_pattern = output_folder / f"{video_path.stem}_%03d.mp4"

    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(SEGMENT_TIME),
        "-f", "segment",
        "-reset_timestamps", "1",
        str(output_pattern)
    ]

    print(f"Splitting: {video_path.name}")
    subprocess.run(command)


def process_category(category: str):

    input_folder = INPUT_ROOT / category
    output_folder = OUTPUT_ROOT / category

    if not input_folder.exists():
        print(f"Skipping missing folder: {category}")
        return

    for video in input_folder.iterdir():

        if video.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        split_video(video, output_folder)


def main():

    for category in ["surface", "underwater"]:
        process_category(category)


if __name__ == "__main__":
    main()