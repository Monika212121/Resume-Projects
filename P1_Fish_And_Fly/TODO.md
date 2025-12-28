# DO them after MVP is created ad tested:

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

✅ You are now building a real autonomous system, not a demo.
Next best step (choose ONE):

1️⃣ Implement Decision layer with lifecycle respect
2️⃣ Add temporal priority smoothing
3️⃣ Add multi-target scheduling
4️⃣ Add failure recovery (SELECTED → STABLE)



# Next you should implement:

SELECTED → DONE / LOST feedback

Action reports completion

Planner releases lock

Aggregator updates lifecycle

When you’re ready, say:

“Implement DONE / LOST feedback loop”

You’re building something very real.