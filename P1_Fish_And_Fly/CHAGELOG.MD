# Changelog

All notable architectural, behavioral, and pipeline-level changes to the Fish and Fly project
are documented in this file.

This project is developed incrementally towards an MVP and a simulation-backed v1,
with emphasis on perception-driven decision making and robotic action pipelines.

The format is inspired by *Keep a Changelog*, adapted for research-style development.

---

```
v1.1.0
 ↑ ↑ ↑
 | | └─ PATCH: bug fixes only
 | └── MINOR: new features (no breaking changes)
 └──── MAJOR: breaking architecture changes

```

## [Unreleased]
### Known Issues
- World projection currently relies on approximate depth estimation using bounding box scale.
- PyBullet integration uses kinematic control; no physics-based grasping yet.
- Underwater dynamics are approximated and not fluid-simulated.

---------------------------------------------------------------------------------------------------
# TODO

## [v1.0.0] - 2026
### Added
- Coverage grid–based navigation visualization for motion and area analysis.

---



## [v1.1.0] - 2026-01-31
### Added
- Initial PyBullet simulation bridge for mirroring perception-driven world state.

### Changed
- Navigation updated to support simulation-driven pose updates instead of direct position teleporting.

### Refactored
- Cleaned action-to-simulation integration via adapter interfaces.

---


## [v1.0.0] - 2026-01-30
### Added
- World projection layer to convert image-space detections into robot-centric coordinates.
- Structured world object representation decoupled from visualization and action intent.
- Added class_id feature in 'WorldObject' object to mirror the same object in simulation.

### Changed
- Visualization pipeline updated to consume precomputed world objects instead of computing projections inline.

### Refactored
- Separated world projection, visualization, decision, and simulation concerns into explicit modules.

---

## [v0.9.0] - 2026-01-24
### Added
- Advanced visualization for tracked vs selected objects using distinct color coding.
- Grasp threshold line overlay for debugging action feasibility.
- Trajectory and coverage visualization for navigation debugging.

### Changed
- Visualization logic decoupled from decision and projection logic.
- Action intent highlighting standardized across visualization pipeline.

---

## [v0.8.0] - 2026-01-20
### Added
- Garbage unload behavior after successful grasp.
- Environment modeling for unloading, including docking point estimation.
- Cost models for selecting optimal unload/docking locations.
- Result logger to persist tracked, grasped, and unloaded objects into CSV format.

### Changed
- Action pipeline extended to support post-grasp behaviors.
- Mission planner updated to include unload as a terminal action.

---

## [v0.7.0] - 2026-01-15
### Added
- Mission planner to orchestrate high-level task execution.
- Navigation module with lawn-mower path generation for surface and underwater coverage.
- Bin manager for managing garbage capacity and storage constraints.

### Changed
- Action module structured into planner, navigator, and execution subcomponents.

---

## [v0.6.0] - 2026-01-10
### Added
- Action pipeline to execute navigation and manipulation behaviors.
- Action intent abstraction for selecting target garbage objects.
- Reach and grasp threshold logic for action feasibility checks.

---

## [v0.5.0] - 2026-01-05
### Added
- World and object visualization utilities.
- Video overlay for drawing tracked objects and debugging perception outputs.

### Changed
- Visualization standardized to support multiple pipelines consistently.

---

## [v0.4.0] - 2025-12-30
### Added
- Decision pipeline for selecting action intent from tracked objects.
- Heuristic-based decision logic integrating confidence, distance, and feasibility.

### Changed
- Tight integration between vision output and decision-making stage.

---

## [v0.3.0] - 2025-12-24
### Added
- Vision pipeline for object detection and tracking.
- Support for multi-object tracking with persistent track IDs.

### Changed
- Vision pipeline structured for extensibility and future model upgrades.

---

## [v0.2.0] - 2025-12-18
### Added
- Core infrastructure modules:
  - Configuration manager
  - Logging framework
  - Alerts and notifications system
- Config-driven architecture using separate YAML files:
  - vision.yaml
  - decision.yaml
  - action.yaml
  - language.yaml
  - simulation.yaml

### Changed
- Application behavior fully driven by external configuration files.

---

## [v0.1.0] - 2025-12-12
### Added
- Initial project scaffolding.
- Main orchestration loop integrating vision and decision pipelines.
- Common utilities and base project structure.

---

*This changelog intentionally tracks architectural and behavioral milestones, not every individual commit or code-level change.*



















---
*This changelog is maintained manually to reflect architectural and behavioral changes,
not every commit.*
