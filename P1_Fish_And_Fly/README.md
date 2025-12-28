# Fish and Fly project

This project has 2 machine: Fish(undewater) and Fly(aerial).

If you want to change the video input, change from `vision.yaml` file.


# Lifecycle Ownership stands:
```
| Component      | Responsibility                |
| -------------- | ----------------------------- |
| Aggregator     | Owns memory & lifecycle state |
| Decision       | Requests lifecycle changes    |
| Selector       | Remembers intent (lock)       |
| VisionPipeline | Applies commands              |
```