# Vision Module responsibilities:
Lifecycle-aware but decision-blind

1.) Track objects over time.
   - Uses `GarbageDetector` + `GarbageTracker`

2.) Maintain memory via aggregations.
   - Uses `GarbageAggregator`

3.) Promote NEW → STABLE
   - Uses `GarbageAggregator`

4.) Mark LOST when gone
   - Uses `GarbageAggregator`

5.) NEVER select targets
   - Relies on Decision module for command to make Lifecycle tranformation changes.


VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV



# Import concepts used :-

## 1. Aggregations:
Detection filtering & aggregation (per frame → per second)

### Reason:
- This is the correct next step for Fish given:
```flowing water -> noisy detections -> tracking already working -> decision layer coming next ```
- If we skip this, the decision layer will be unstable and brittle.


### Goal of this step:
- Right now you have this:
```Frame → [Detection, Detection, Detection]```

- What you need is this:
```
Multiple frames (1–2 sec)
        ↓
Stable tracked objects
        ↓
Filtered, aggregated detections
        ↓
Decision-ready objects
```
- This step turns vision output → intelligence input.


### Key Design Principles (important)
- Tracking ID is the anchor, not frame index
- Decisions should be based on temporal evidence, not single frames
- Vision module must output stable facts, not raw noise
- This logic belongs in Vision, not Decision
- So we introduce a Vision Aggregator.


### GarbageAggregator
Location: ```src/fish/stage1_vision/aggregator.py```

Responsibility: 
- Group detections by track_id
- maintain short history (buffer)
- compute aggregated properties


### Data Flow (after this step)
```
Camera/Frame
   ↓
Detector + Tracker (DONE)
   ↓
Detections (DONE)
   ↓
GarbageAggregator (NEW)
   ↓
AggregatedGarbageObjects (STABLE)
   ↓
Decision Module (NEXT)
```

- Now Vision outputs TrackedGarbage, not raw detections.
(We’ll use min_age in Decision layer next.)


### What you have achieved after this step
- Stable object understanding
- Noise-resistant vision
- Flow-aware garbage perception
- Clean handoff to Decision module

--------------------------------------------------------------------------------------------------------------------------------------------

## 2. Vision I/O Abstraction layer

### What you have achieved after this step
- Vision pipeline is now input-agnostic.
- Same code works for:
   - camera
   - video
   - simulation (later)

--------------------------------------------------------------------------------------------------------------------------------------------

