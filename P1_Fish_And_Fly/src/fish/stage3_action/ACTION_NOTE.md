# Action module responsibilities

## Action Mental Model
```
Sensors / PyBullet
        ↓
EnvironmentModel
        ↓
Cost Models
        ↓
Mission Decision
        ↓
Navigation Execution
```


## Navigation pattern:

```
SURFACE:
A(surface)  ───────▶  B(surface)
(clean floating debris)

DESCEND

UNDERWATER:
B'(under)  ◀───────  A'(under)
(clean submerged debris)

ASCEND

RETURN:
A(surface) ───────▶  H (HQ)

```

# Unloading Garbage bin

- I am using Cost based deterministic minimization function to locate the nearest D-point(dump/docking point).
- Correct cost decomposition (industry-grade)
- Let’s rewrite your cost in a robot-usable way:

TOTAL_COST =
    w_time        * travel_time
  + w_energy      * energy_consumption
  + w_current     * current_opposition
  + w_drag        * hydrodynamic_drag
  + w_risk        * collision_risk
  + w_uncertainty * localization_uncertainty


### Each term must be:

- cheap to compute
- monotonic (higher = worse)
- comparable after normalization


### How to compute EACH term (practical & realistic)?

🔹 1. Travel time (easy, reliable)
```travel_time = planar_distance / nominal_speed```

Use cruise speed, not max speed.

✔ very reliable
✔ used everywhere


🔹 2. Energy consumption (THIS is key)

- Industry trick: ```Energy ∝ drag force × distance```

- From fluid dynamics (simplified): ```𝐹𝑑𝑟𝑎𝑔 = (𝜌 * 𝐶𝑑 * 𝐴𝑣2) / 2```
	​
But you do NOT need exact physics online.

- Practical proxy (recommended): 

```energy = drag_coeff * (relative_speed ** 2) * distance```


Where:

```relative_speed = robot_speed + opposing_current```

drag_coeff → from PyBullet or calibration

✔ correlates strongly with real energy
✔ simple
✔ stable


🔹 3. Current opposition (direction matters)

- Use vector projection, not magnitude.
```current_opposition = max(0, dot(current_vector, path_direction))```

0 → helping or neutral

positive → resisting motion

✔ modern AUV practice
✔ avoids penalizing helpful currents


🔹 4. Hydrodynamic drag (from PyBullet)

- Since you already simulate drag in PyBullet, reuse it.

- Best practice: Precompute average drag per meter

- Use that as a cost scalar

```drag_cost = avg_drag_force * distance```

✔ avoids per-step simulation

✔ consistent with physics engine


🔹 5. Collision risk (simple but effective)

- Industry does NOT predict collisions probabilistically online.

- Use a density-based heuristic:

```collision_risk = obstacle_density(target_area)```


sonar map,
occupancy grid,
known static structures

✔ cheap

✔ conservative


🔹 6. Localization uncertainty (important underwater)

- Simple and effective:

```uncertainty = covariance_trace(position_cov)```


Or even: ```uncertainty = distance_since_last_fix```

✔ very realistic

✔ used in long-range AUVs




## Goal of the Environment Abstraction

- Provide environmental estimates (currents, risk, uncertainty) to cost_models, navigation, and mission logic without exposing sensors or PyBullet directly.


### Why NOT pass raw sensors / PyBullet directly?

Because:
- planners must be deterministic
- sensors are noisy & asynchronous
- simulation ≠ real world
- Planners query estimates, not raw data.


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Reasons of code logic I used:

1.) In ```mission_planner.py/tick()``` line 112

### Why stepping forward is in else condition?

- If there are many objects at the same location, then I need to collect them all from the same position.
- So I cannot move ahead just after 1 collection. Eg: if there are 3 objects in the same position, and I collected 1 and move forward. 
- `Problem`: If I do so, then other 2 objects will be left ,as we already moved forward.
- I need to stay at the same position, till there are no objects left in reach(all nearby objects collected). 
- Hence, the fish machine can move forward only, when there is not a single object left in reach(means all 3 collected, so 3 times while loop iterate -> 3 times tick() called).



2.) In `main.py` line 52 and 61, I passed a same navigator object in 2 different classes.

- If I create 1 PathNavigator object in main() and pass the same object reference to: ```FishMissionPlanner and UnloadGarbageBehavior```

- then any mutation (e.g. current position, phase, internal state) done by either will be visible to the other.

- This is by design in Python.


```
MissionPlanner ─┐
                ├──► PathNavigator (same memory)
UnloadBehavior ─┘
```

- In robotics, this is called a: Shared navigation state (single source of truth)
```
Python passes object references, not copies.
Shared object = shared truth.
```

#### NOTE:
```
- Mission planner moves fish → navigator updates position
- Garbage unload uses navigator → it sees updated position
- Garbage unload changes state → mission planner sees it
```

3.) ONE TIME LOGGING GUARD
A one-time logging guard guarantees that each logical object (track_id) is logged exactly once for a terminal event like: `DONE`, `LOST`, `FAILED` 


4.) If any sub-module fails in creating action_intent or no object is detected in frame or selection didn't work, the fish machine should move forward in the Lawn-mower path.

- So we took `navigation_only` flag and making it `True`, if action_intent is None or selection failed or No tracked objects.


5.) Explicit updating `feedback.status` = SUCCESS.

- In case action is failed for first time, I am calling handle_failure to re-attempt the same action for 3 times, before finally aborting the mission.

- The thing is if the action is success in these 3 attempts, we are passing boolean confirmation to `handle_target()`.

- But we are not passing the new action_feedback(SUCCESS), so that feedback value is still the old one of status = FAILED, but now the action is SUCCESS after re-attempt.

- So we are just updating the status from FAILED -> SUCCESS here for further processing of action_feedback. 


6.) In `main.py`, if after receiving action_feedback from `tick()`:

Test case1: If action_intent is valid(not None), action_feedback.status = NONE, then continue.

- Then the control flow will contiue and will not go through the handle_feedback() and will not release the locked target id from memory, this will create issue in next iteration or handling next target.


Test case2: If action_intent is valid(not None) but target is at a far distance, then according to code logic, only navigation will execute.

- But the selected object must remain locked and not released until action is taken on that object to return status = SUCCESS/FAILED.


7.) In `selector.py` file, I made soem changes.

Test case1: If action_track_id = valid, means an object is already locked in a fresh iteration.

- It means the object is still UNATTEMPTED, so we need to attemp and apply action pipeline first.


8.) There is mainly 2 tasks Fish machine is performing:-

- Garbage collection

- Navigation


9.) In case of approach to last waypoint of a set path, if Fish machine is too close to the last waypoint, then advancing index can raise `error: out of index`.

- So, to avoid this error, I added a check of path_is_finsihed(), and returned the last target waypoint as the return new poisition.

- The control will traverse to the tick(), where path_is_finished() check is present to trigger advance phase of the mission and set another path.


10.) Perception(image Frame) → World Frame→ Mission Space Projection (x,y=same, z=depth)

- Perception outputs 2D bounding boxes in the camera frame.
- These are transformed into world-frame WorldObjects using perception-to-world projection.
- The resulting world objects initially have z = 0 (surface reference).
- During mission execution, the MissionPlanner injects the correct z value based on the current phase:
    - SURFACE → z = depths.surface
    - UNDERWATER → z = depths.underwater

This ensures:
- In Navigation: Correct 3D distance computation between the fish and garbage,
- In Simulation: Accurate simulation mirroring of objects at the active mission depth,
- Clean separation between perception space, world frame, and mission space.

Depth is treated as a mission-level attribute, not a perception property.
