# Decision module responsibilities:

1.) Read current state of detections, received from the Vision module.
- Only consider STABLE
- Ignore NEW / LOST / DONE

2.) Filter tracked garbage objects
- Uses `RuleFilter`, `PriorityReasoner`, `Planner`.

3.) Rank garbage
- Uses `PriorityReasoner`

3.) Select ONE target
- Lock onto one `track_id`

4.) Emit lifecycle command to Vision module's aggregations to update the locked object's state to `SELECTED`/`DONE`. 
`SELECT` → Vision marks as `SELECTED`

VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV


# Important concepts used:-

## 1. Lifecycle States:
```
NEW        → seen but not trusted yet
STABLE     → persistent, decision-eligible
SELECTED   → chosen by decision layer
DONE       → action completed
LOST       → disappeared / expired

```

### After this step:
- Every tracked garbage object will be in one of 5 explicit states.
- States will change automatically based on time & decisions.
- Decision layer will consume lifecycle, not guess stability.
- No phantom tracks, no flip-flopping, no duplicate actions.


### Core Design Principle (read this first)
- Lifecycle state is global memory. But state transitions are owned by specific layers.
- If you violate ownership → system becomes un-debuggable.


### State Semantics/ State Ownership Contract (NON-NEGOTIABLE)
```
    State	                            Who can SET it?	                            Why

    NEW	                                Vision Aggregator	                    First time observed
    STABLE	                            Vision Aggregator	                    Observed long enough
    SELECTED	                          Decision Layer	                    Target chosen
    DONE	                              Action Layer	                        Garbage collected
    LOST	                            Vision Aggregator	                    Disappeared
```
⚠️ Decision must NEVER set DONE or LOST
⚠️ Vision must NEVER set SELECTED


## 2.) Decision Pipeline sequence

## STEP 1️⃣ — Decision Input Filtering

### Goal
Decision layer should never see:
- NEW
- LOST
- DONE

It only sees:
- STABLE

### Why this step is critical?

If you skip this:
- Decision logic becomes noisy
- Selection oscillates
- Robot behaves erratically
- Real-world failure guaranteed

--------------------------------------------------------------------------------------------------------------------------------------------------

## 2. Selector Lock:

### Core Principle (lock this in)
```
Vision OWNS lifecycle state
Decision REQUESTS lifecycle transitions
```
- Decision should never mutate objects directly.
- It should issue commands / intents that Vision (or Aggregator) applies.


### Correct Architecture for Lifecycle Changes
```
Vision Aggregator (memory owner)
        ↑
   LifecycleCommand
        ↑
Decision Selector (intent owner)
```

So the flow is:
- Vision produces tracked objects (with states)
- Decision selects ONE object
- Decision emits a LifecycleCommand
- Aggregator applies the state change


### Selection Lock + Lifecycle Transition
This means:
- Once an object is SELECTED
- Decision should stick to it
- Until it becomes DONE or LOST

This is the bridge between Decision and Action.


### Why this step is mandatory?

a.) Without it:
- Robot keeps changing targets every frame
- Garbage collection never finishes
- Vision + Decision fight each other

b.) With it:
- System behaves purposefully
- Looks intelligent
- Works in real water flow

-----------------------------------------------------------------------------------------------------------------------------------------------