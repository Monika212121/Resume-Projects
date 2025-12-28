"""
template.py — Auto-create Fish & Fly Project Architecture
Run once: python template.py
"""

import os

# === FOLDER STRUCTURE ===
folders = [
    # Top-level configs and data
    "configs",
    "data/raw/fish",
    "data/raw/fly",
    "data/processed",
    "data/annotations",

    # Models
    "models/yolo",
    "models/classifier",
    "models/vlm/paligemma",
    "models/clip",
    "models/llm",

    # ===========================
    # FISH MODULE (Underwater)
    # ===========================
    "fish/stage1_vision",
    "fish/stage2_language",
    "fish/stage3_decision",
    "fish/stage4_action",
    "fish/sim/assets",
    "fish/utils",

    # ===========================
    # FLY MODULE (Surveillance)
    # ===========================
    "fly/stage1_vision",
    "fly/stage2_language",
    "fly/stage3_decision",
    "fly/sim/assets",
    "fly/utils",

    # Shared Code
    "shared/utils",
    "shared/configs",
    "shared/models",

    # Analysis and results
    "notebooks",
    "tests",
    "results/images",
    "results/videos",
    "results/logs",
    "docs"
]

# === FILES WITH STARTER CONTENT ===
files = {
    # Root files
    "README.md":
    "# 🐟 Fish & Fly: Vision–Language–Action Autonomous Water Cleaning System\n\n"
    "A modular robotics system combining underwater garbage collection (Fish) and aerial surveillance (Fly).\n"
    "Project structure auto-generated using template.py\n",

    "requirements.txt":
    "torch\n"
    "torchvision\n"
    "transformers\n"
    "ultralytics\n"
    "opencv-python\n"
    "pybullet\n"
    "numpy\n"
    "matplotlib\n"
    "pyyaml\n",

    ".gitignore":
    "__pycache__/\n"
    "*.pt\n"
    "*.pth\n"
    "*.mp4\n"
    "*.avi\n"
    "*.log\n"
    "*.cache\n"
    ".env\n",

    # Configs
    "configs/fish.yaml":
    "vision_model: yolov8n\n"
    "vlm_model: paligemma\n"
    "safety_threshold: 0.7\n",

    "configs/fly.yaml":
    "altitude: 20\n"
    "fov: 75\n"
    "mission_mode: surveillance\n",

    "configs/vlm.yaml":
    "model_name: paligemma-3b\n"
    "json_enforce: true\n",

    # ==========================
    # FISH MODULE FILES
    # ==========================
    "fish/stage1_vision/detector.py":
    "# YOLO + classifier detection for underwater garbage\n",

    "fish/stage1_vision/tracker.py":
    "# Object tracking for underwater objects\n",

    "fish/stage2_language/vlm_reasoner.py":
    "# Vision-Language reasoning for safety, garbage validation, ambiguity resolution\n",

    "fish/stage3_decision/decision_gate.py":
    "# Decide when to call VLM & combine classifier+VLM outputs\n",

    "fish/stage3_decision/policy.py":
    "# Policies for when to APPROACH / ABORT / GRASP\n",

    "fish/stage4_action/fsm.py":
    "# Fish robot Finite State Machine\n",

    "fish/stage4_action/controller.py":
    "# Low-level underwater robot movement\n",

    "fish/sim/env.py":
    "# PyBullet environment for underwater simulation\n",

    "fish/utils/logger.py":
    "# Logging utilities for fish module\n",

    # ==========================
    # FLY MODULE FILES
    # ==========================
    "fly/stage1_vision/detector.py":
    "# Fly module detection (surface view)\n",

    "fly/stage2_language/vlm_scene_reasoner.py":
    "# VLM for pollution severity, zone labeling, summarization\n",

    "fly/stage3_decision/zone_planner.py":
    "# Decide priority zones for fly robot\n",

    "fly/sim/env.py":
    "# Drone simulation environment\n",

    "fly/utils/logger.py":
    "# Logging utilities for fly module\n",

    # Shared code
    "shared/utils/image_ops.py": "# Shared image utilities\n",
    "shared/utils/config_loader.py": "# YAML/JSON config loader\n",
    "shared/utils/geometry.py": "# Distance, angles, projections\n",

    # Integration
    "shared/models/loader.py": "# Generic model loader\n",

    # Notebooks
    "notebooks/01_train_yolo.ipynb": "",
    "notebooks/02_fish_vlm_experiments.ipynb": "",
    "notebooks/03_fly_scene_understanding.ipynb": "",

    # Tests
    "tests/test_fish_pipeline.py": "",
    "tests/test_fly_pipeline.py": "",
    "tests/test_vlm.py": "",

    # Main runner
    "main.py":
    "from fish.stage1_vision.detector import *\n"
    "from fish.stage4_action.fsm import *\n\n"
    "print('🚀 Fish & Fly system initialized.')\n"
}

# === CREATE DIRECTORIES ===
for folder in folders:
    os.makedirs(folder, exist_ok=True)


# === CREATE FILES SAFELY ===
for file_path, content in files.items():
    if os.path.exists(file_path):
        print(f"⚠️  Skipped (already exists): {file_path}")
        continue

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"✅ Created: {file_path}")



print("Fish & Fly architecture created successfully!")