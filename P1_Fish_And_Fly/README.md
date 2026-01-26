# Fish and Fly project

This project has 2 machine: Fish(undewater) and Fly(aerial).

If you want to change the video input, change from `vision.yaml` file.


## Mental model:

```
Vision (what is this)
        ↓
Decision (what to do)
        ↓
Mission Planner (how to do it)
        ↓
     Action (do it)
        ↓
Navigation Controller (move)
        ↓
Manipulator Controller (grasp/collect)
        ↓
Simulator (PyBullet)
        ↓
Feedback (success / fail)

```


# Lifecycle Ownership stands:
```
| Component      | Responsibility                |
| -------------- | ----------------------------- |
| Aggregator     | Owns memory & lifecycle state |
| Decision       | Requests lifecycle changes    |
| Selector       | Remembers intent (lock)       |
| VisionPipeline | Applies commands              |
```



One sentence that should lock it in your brain

Robots don’t “finish tasks” — they keep ticking until the mission state changes.