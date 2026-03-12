# Simulation notes

Control flow diagram:
```
Perception
   ↓
MissionPlanner
   ↓
SimulationBridge
   ↓
ObjectManager
   ↓
ObjectFactory
   ↓
PyBullet
```

# Perception-driven digital twin simulation

Perception runs on real video → simulation mirrors reality → actions execute in sim.


## 1.) One-way sim-to-real bridge (NOT full physics realism)

### Pipeline:
```Video → Detection / Tracking → Fish Frame Mapper -> World Mapper → PyBullet Scene → Action Execution```

### Key constraints:
- No sensor feedback from PyBullet back into perception
- PyBullet is a mirror, not a source of truth
- Perception drives everything



## 2.) Object spawning based on perception (GOOD idea)

This part is strong: 

`If video detects “plastic bottle” at (x, y, t), spawn a plastic bottle URDF in PyBullet at mapped (x′, y′)`



## 3.) Visual similarity, not physical accuracy

### You do not need:
- realistic water physics
- hydrodynamics
- buoyancy forces
- fluid simulation

### For v1:
- textured plane
- background image
- approximate scale

That is enough to demonstrate the concept.



### 4️.) Architectural truth (this matters)

What you’re actually building is NOT “PyBullet integration”.

### I am building a 4-layer system:
```
Perception (real video / DL)
        ↓
Fish frame Mapper (Used in Action module)
        ↓
World State Mapper (Used in Simulation module only, THIS is the key)
        ↓
Simulation Executor (PyBullet)
```


## 5.) Benefits of this Design Decision

- Motion logic is centralized in Navigation.
- Simulation mirrors state and environment only.

- Rationale:
    - Deterministic planner behavior
    - Clear separation of concerns
    - Easier debugging and testing
    - Future-safe transition to physics-driven control


------------------------------------------------------------------------------------------------------------------------------------------------------------

# IMPORTANT POINTS:

## 1.)  Motion Ownership

Motion computation is intentionally owned by the Navigation layer.

- Navigation computes the next robot pose deterministically (based on path, speed, dt, and mission logic).
- The Simulation layer is responsible ONLY for:
    - Applying the provided pose to the simulated robot
    - Maintaining environment state (objects, grasp, removal)
    - Rendering / physics mirroring

- The Simulation module MUST NOT:
    - Recompute incremental motion
    - Integrate velocity or time
    - Modify robot pose independently

- This separation avoids double-integration, drift, and planner–simulation conflicts.

NOTE: **If physics-based control is introduced in future versions, motion ownership must be explicitly transferred to Simulation and removed from Navigation.**

- In that case, I need to make changes in both places, in `step_forward()`, I need to remove calculation of new_position and add the same in `step()` in Simulation.



## 2.) Simulation constraints

🏆 What interviewers / reviewers expect

They expect you to say:
```
“Workspace boundaries are enforced at the planning layer.
Simulation mirrors valid robot states, not raw physics.”
```


## 3.) Spawning garbage objects

We will:

- ignore world_object.position.x/y
- use only distance
- project along fish yaw
- clamp to workspace
- spawn once per track_id

- I am spawning garbage object, at OFFSET = 5 units, far in front, than the actual garbage position. 

- This is for realistic visualization for Fish approaching garbage, stopping and collecting garbage object.

- NOTE: Spawn offset is simulation-only, to allow approach & collection time.


### Spawning shapes

| Category  | Shape   | Color      |
| --------- | ------- | ---------- |
| Garbage   | Sphere  | Red        |
| Collected | Sphere  | Green      |
| Fish      | Capsule | Cyan       |
| Plant     | Box     | Dark green |
| Rock      | Big box | Brown      |
| Hazard    | Cone    | Yellow     |


## 4.) WorldObject

- This object must represent an entity already expressed in WORLD frame and owned by simulation / digital twin, not perception.

- A garbage object is received in `Fish frame`, from Action module and it's frame is transformed in `World frame`, in Simulation module.

Key invariants:
- world_position never changes after spawn
- Independent of Fish pose
- Independent of perception noise




## sIMUALTION OF SEMANCTI CATEGORY ITEMS

sphere → (radius,)
box → (x, y, z)
capsule → (radius, height)
cylinder → (radius, height)



# Object Lifetime Design

| Object           | Behavior       |
| ---------------- | -------------- |
| Garbage          | permanent      |
| Rock             | permanent      |
| Fish entity      | timeout + fade |
| Plants           | timeout + fade |
| Dangerous animal | timeout + fade |
