print("=== Fish & Fly Environment Check ===")

# ---- PYTORCH ----
try:
    import torch
    print("[PyTorch]       OK  | Version:", torch.__version__)
    print("                CUDA available:", torch.cuda.is_available())
except Exception as e:
    print("[PyTorch] ERROR:", e)

# ---- YOLO / ULTRALYTICS ----
try:
    from ultralytics import YOLO
    print("[YOLOv10]       OK")
except Exception as e:
    print("[YOLOv10] ERROR:", e)

# ---- OpenCV ----
try:
    import cv2
    print("[OpenCV]        OK  | Version:", cv2.__version__)
except Exception as e:
    print("[OpenCV] ERROR:", e)

# ---- Transformers ----
try:
    from transformers import AutoProcessor
    print("[Transformers]  OK")
except Exception as e:
    print("[Transformers] ERROR:", e)


print("\n=== Environment Check Completed ===")