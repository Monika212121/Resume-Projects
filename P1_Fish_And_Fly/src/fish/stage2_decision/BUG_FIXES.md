# Bugs fixes:

1.) In `aggregation.py` file

### What was the original bug?

You observed this:
```
if idle_frames > max_idle_frames (30)               → a new detection appears with age = 1, last_seen_frame = 6, track_id = 2

But when: idle_frames < 30                          → the detection disappears
```
- This felt inconsistent — but it was actually a lifecycle logic mismatch, not a YOLO or tracker issue.

### Root cause (what was wrong earlier)

- Earlier, your aggregation logic was implicitly doing two conflicting things:
- Removing old tracks
    - Allowing YOLO+BoTSORT to re-introduce the same physical object with a new track_id
    - But the aggregator didn’t clearly distinguish:

```“same physical object reappearing” vs “brand-new object”```

So the behavior looked wrong.

### What changed (and why it’s now correct)
- Correct lifecycle semantics now in place
- With our 5-state lifecycle:
```
NEW → STABLE → SELECTED → DONE
              ↘
               LOST
```
and config:
```
aggregation:
  max_history: 15
  stable_age: 5
  max_idle_frames: 30
```

we are now correctly enforcing:

### 1.) When object disappears briefly (idle_frames < 30)         

- Expected behavior
    - Object remains in aggregator memory                                
    - State → LOST
    - No new detection emitted
    - No new track created


### Benefits:
👉 This prevents flickering & duplication
👉 This is correct


### 2.) When object disappears too long (idle_frames > 30)

Expected behavior

- Old track is finalized (DONE or removed)
- Memory entry is released
- If YOLO later sees something:
    - It is treated as a new physical object
    - New track_id
    - age = 1
    - last_seen_frame = current

👉 This is correct real-world behavior

Because after 30 frames, you explicitly said:

“I no longer trust this to be the same object”


### Now we have results saying:
```
when idle_frame > 30 → new detection appears with age=1
when idle_frame < 30 → detection is gone
```
That means:

✅ Lifecycle expiration works
✅ Memory cleanup works
✅ No zombie tracks
✅ No false continuity
✅ Aggregator is doing its job, not YOLO’s