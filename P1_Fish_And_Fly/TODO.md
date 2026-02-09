# DO them after MVP is created and tested:

## 1.) TO increase accuracy in detection:

```class_id=4, class_name='other'```

This means: Most debris falls into “other”, Class imbalance still exists (as seen in metrics earlier)

⚠️ This is expected, not a bug.

Later you can:
- merge low-frequency classes
- re-weight loss
- add class-specific confidence thresholds

But do NOT fix this now.


----------------------------------------------------------------------------------------------------------------------------------------------------------

### 2.) Later, RuleFilter can be split into:

Safety rules

Mission rules”


### tommorow start here:

1. ) FOR TRAJECTORY/ COVERAGE LOGGING

- show how to export trajectory to JSON
- design the heatmap grid algorithm
- help you color underwater vs surface
- or tell you when exactly to refactor later


2.) visualize world frame

- Add exponential smoothing to world coordinates
- Create a top-down mini-map
- Help tune thresholds live
- Prepare projection for PyBullet swap


3.) Decision pipeline,

- In later versions, add a filter in Decision module to add a separate code logic.

- Reason: This is to consider distance of tracked garbages from fish, so that nearest garbage is attempted first.

- Right now, it is working fine but later, add this condition.


# todo:

NEXT (only one line)

👉 If you want next: PyBullet fish movement + hydrodynamics
or
👉 Fly → Fish mission assignment protocol

👉 Add mission replay + metrics




design the log schema cleanly

write a replay_simulation.py skeleton

show how to sync videos

help storyboard the demo