
# Fish & Fly Autonomous Multi-Agent Cleanup System
# Simulation Test Cases & Demo Recording Guide

---

# CAMERA MODES

| Key | Camera |
|------|---------|
| 1 | Overview Camera |
| 2 | Fish Follow Camera |
| 3 | Manatee Follow Camera |
| 4 | Cinematic Camera |
| 5 | Top View Camera |

---

# PRIORITY LEGEND

| Level | Meaning |
|------|------|
| CRITICAL | Must appear in final demo |
| HIGH | Strong portfolio value |
| OPTIONAL | Bonus showcase |

---

# 1. TARGET DETECTION & COLLECTION
Priority: CRITICAL

## Objective
Validate autonomous garbage detection, navigation, and collection pipeline.

## Input
- Garbage object spawned in workspace

## Expected Behavior
- Detect object
- Classify as target
- Navigate toward target
- Collect object
- Remove object from environment

## Recording Plan
- Start: Overview Camera (2 sec)
- Main: Fish Follow Camera (6–8 sec)

## Key Visuals
- Bounding box on target
- Smooth navigation
- Successful collection

---

# 2. ENVIRONMENT ENTITY IGNORE
Priority: HIGH

## Objective
Validate intelligent filtering of non-target environment entities.

## Input
- Fish / plant / harmless entity

## Expected Behavior
- Detection occurs
- Entity classified correctly
- No collection attempt

## Recording Plan
- Fish Follow Camera throughout

## Key Visuals
- Bounding box visible
- Robot ignores object
- Continued exploration

---

# 3. NAVIGATION HAZARD AVOIDANCE
Priority: CRITICAL

## Objective
Validate safe autonomous navigation behavior.

## Input
- Rock / dangerous object

## Expected Behavior
- Hazard detection
- Path deviation
- Safe traversal

## Recording Plan
- Elevated Fish Follow Camera

## Key Visuals
- Hazard blinking
- Visible path change
- Safe navigation

---

# 4. AUTONOMOUS EXPLORATION
Priority: HIGH

## Objective
Validate continuous exploration behavior.

## Input
- No objects nearby

## Expected Behavior
- Continuous forward movement
- Area scanning behavior

## Recording Plan
- Overview Camera

## Key Visuals
- Smooth exploration
- Coverage motion

---

# 5. TARGET NEAR HAZARD DECISION
Priority: CRITICAL

## Objective
Validate safety-prioritized decision intelligence.

## Input
- Garbage object near hazard

## Expected Behavior
- Detect both entities
- Prioritize safety
- Avoid collection attempt

## Recording Plan
- Overview Camera
- Switch to Fish Follow during decision moment

## Key Visuals
- Multiple detections
- No collection
- Safe avoidance

---

# 6. MULTI-OBJECT CLASSIFICATION
Priority: CRITICAL

## Objective
Validate simultaneous multi-object handling.

## Input
- Garbage
- Hazard
- Environment entity

## Expected Behavior
- Correct classification
- Correct prioritization
- Appropriate action selection

## Recording Plan
- Overview Camera

## Key Visuals
- Multiple bounding boxes
- Different system responses

---

# 7. SEQUENTIAL AUTONOMOUS DECISIONS
Priority: CRITICAL

## Objective
Validate continuous decision pipeline.

## Expected Behavior
- Detect target
- Collect
- Continue navigation
- Avoid hazard
- Resume exploration

## Recording Plan
- Mixed Overview + Fish Follow

## Key Visuals
- Smooth state transitions
- Continuous autonomy

---

# 8. MANATEE BOUNDARY PATROL
Priority: HIGH

## Objective
Validate persistent perimeter navigation.

## Expected Behavior
- Continuous patrol
- Smooth corner turns
- Stable orientation changes

## Recording Plan
- Overview Camera (3 sec)
- Manatee Follow during corner turn (4 sec)
- Overview Camera (3 sec)

## Key Visuals
- Boundary following
- Smooth corner rotation

---

# 9. DUMP POINT COLLECTION MISSION
Priority: CRITICAL

## Objective
Validate autonomous logistics dispatch workflow.

## Input
- Filled dump point

## Expected Behavior
- Dump highlighted
- Manatee dispatched
- Garbage collection performed
- Dump restored to normal state

## Recording Plan
- Overview Camera (start)
- Manatee Follow (movement)
- Overview Camera (completion)

## Key Visuals
- Dump color change
- Autonomous dispatch
- Collection completion

---

# 10. BIN FULL → HQ UNLOAD
Priority: CRITICAL

## Objective
Validate resource management workflow.

## Expected Behavior
- Bin full detection
- Mission interruption
- Return to HQ
- Unloading operation
- Resume mission

## Recording Plan
- Manatee Follow
- Cinematic Camera at HQ
- Overview during mission resume

## Key Visuals
- HQ unloading
- Resume from checkpoint

---

# 11. MISSION COMPLETE → RETURN HQ
Priority: HIGH

## Objective
Validate mission lifecycle completion.

## Expected Behavior
- Cleanup completed
- Return to HQ

## Recording Plan
- Overview Camera

## Key Visuals
- Workspace cleaned
- Return behavior

---

# 12. SYSTEM FAILURE / ABORT
Priority: HIGH

## Objective
Validate safe-failure handling.

## Input
- Sensor failure / invalid state

## Expected Behavior
- Abort triggered
- Safe stop behavior

## Recording Plan
- Overview Camera

## Key Visuals
- Abort debug text
- System halt

---

# 13. RECOVERY & RESUME
Priority: OPTIONAL

## Objective
Validate robustness and mission recovery.

## Expected Behavior
- Temporary issue occurs
- System resumes correctly

## Recording Plan
- Overview Camera

## Key Visuals
- Recovery continuity

---

# 14. MULTI-AGENT COORDINATION
Priority: CRITICAL

## Objective
Validate distributed autonomous orchestration.

## Expected Behavior
- Fish active
- Manatee active
- Hazard system active
- Dump system active

## Recording Plan
- Top View Camera

## Key Visuals
- Simultaneous agent activity
- Coordinated operations

---

# 15. FULL AUTONOMOUS CLEANUP SCENARIO
Priority: CRITICAL

## Objective
Validate complete integrated system workflow.

## Expected Behavior
- Detection
- Collection
- Hazard avoidance
- Dispatch coordination
- HQ unloading
- Mission completion

## Recording Plan
- Mixed cinematic shots

## Key Visuals
- Entire ecosystem functioning together




$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


## FOR FUTURE:


16. PARTIAL OCCLUSION DETECTION

Priority: HIGH

Objective

Validate robustness when object is partially hidden.

Example
garbage partially behind rock
partially underwater
overlapping entities
Expected Behavior
stable detection OR safe ignore
no unstable oscillation
Why Important

Shows:

real-world perception robustness


17. FALSE POSITIVE REJECTION

Priority: HIGH

Objective

Validate prevention of wrong collection.

Example

Object visually similar to garbage.

Expected Behavior
detection confidence low
no collection triggered
Why Powerful

Recruiters LOVE this.

Because:

avoiding bad decisions > making decisions


18. DYNAMIC OBSTACLE AVOIDANCE

Priority: VERY HIGH

Objective

Validate reaction to moving hazards/entities.

Example
moving fish crosses path
moving obstacle enters route
Expected Behavior
reroute
pause
continue safely
Why Huge

This upgrades project from:

scripted navigation

to:

reactive autonomy

Massive difference.


19. DISPATCH PRIORITIZATION

Priority: VERY HIGH

Especially important for Manatee.

Example

Multiple filled dump points.

Expected Behavior
nearest/highest-priority selected
efficient dispatch
Why Important

Shows:

mission planning intelligence

VERY strong robotics systems signal.


20. INTERRUPTED COLLECTION RESUME

Priority: CRITICAL

You ALREADY partially built this with:

freezed_checkpoint

This is a VERY powerful scenario.

Flow
Manatee collecting dump
bin full
unload HQ
RETURN to same mission checkpoint
continue collection
Why Important

This is:

true autonomous task persistence

VERY advanced behavior.

Honestly:
this is one of your strongest backend engineering features.

Definitely record this later.


21. COVERAGE GAP HANDLING

Priority: OPTIONAL

Objective

Validate unexplored area revisit.

Example
skipped area due to hazard
revisit later
Why Important

Shows:

intelligent exploration completeness


22. HAZARD SATURATION SCENARIO

Priority: OPTIONAL BUT IMPRESSIVE

Example

Many hazards clustered together.

Expected Behavior
stable navigation
no oscillation
safe fallback
Why Powerful

Stress test.

Shows:

system stability under complexity


23. SIMULATION RECOVERY AFTER STEP FAILURE

Priority: VERY HIGH

You already implemented:

step_retry_count
max_step_retry_count

This deserves a dedicated test.

Example
simulated motion mismatch
retry mechanism activates
Why Strong

Shows:

fault-tolerant robotics execution

VERY professional engineering signal.


24. MANATEE ORIENTATION CONSISTENCY

Priority: HIGH

Objective

Validate realistic vessel turning.

Expected Behavior
orientation aligns with movement
no snapping glitches
Why Important

Makes simulation feel:

believable


25. CAMERA SYSTEM DEMO

Priority: OPTIONAL

Honestly:
this can become a GREAT LinkedIn clip.

Example

Press:

1 overview
2 fish
3 manatee
4 cinematic
Why Valuable

Shows:

tooling + developer experience engineering

Most students NEVER build this.