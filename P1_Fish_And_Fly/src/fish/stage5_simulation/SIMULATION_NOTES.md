

# Perception-driven digital twin simulation

Perception runs on real video → simulation mirrors reality → actions execute in sim.


## 1.) One-way sim-to-real bridge (NOT full physics realism)

### Pipeline:
```Video → Detection / Tracking → World Mapper → PyBullet Scene → Action Execution```

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

### You’re building a 3-layer system:
```
Perception (real video / DL)
        ↓
World State Mapper (THIS is the key)
        ↓
Simulation Executor (PyBullet)
```

### The most important module you haven’t named yet

You need a World Mapper / Sync Layer.

This module:
- converts pixel detections → world coordinates
- maintains object IDs
- decides when to spawn / delete objects
- keeps sim in sync with perception

This is where your deep learning + robotics skill actually shows.

PyBullet itself is secondary.



### Roles (very important)

1.) WorldStateManager

- Input: perception detections
- Owns:
    - object registry
    - timeouts
- Decides:
    - spawn / update / remove


2.) ObjectAdapter

- Maps:
   - class_label → URDF
   - world pose → PyBullet pose


3.) RobotAdapter

- Owns robot body ID
- Exposes:
```
set_pose(x, y, z)
attach_object(object_id)
detach_object(object_id)
```


4.) Navigator

Calls:
```
move_to(target)
```

------------------------------------------------------------------------------------------------------------------------------------------------------------

# IMPORTANT POINTS:

```
Tracked Objects (image space, tracker IDs)
            ↓
World Object Projection (pure data)
            ↓
Simulation / PyBullet
```


1.)  Motion Ownership

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


## Benefits of this **Design Decision**

- Motion logic is centralized in Navigation.
- Simulation mirrors state and environment only.

- Rationale:
    - Deterministic planner behavior
    - Clear separation of concerns
    - Easier debugging and testing
    - Future-safe transition to physics-driven control



2.) Simulation costraints

🏆 What interviewers / reviewers expect

They expect you to say:
```
“Workspace boundaries are enforced at the planning layer.
Simulation mirrors valid robot states, not raw physics.”
```

3.) Spawning garbage objects

Authoritative rule for simulation garbage position:
```Garbage position = projected in front of fish using WorldObject.distance```

We will:

- ignore world_object.position.x/y
- use only distance
- project along fish yaw
- clamp to workspace
- spawn once per track_id
