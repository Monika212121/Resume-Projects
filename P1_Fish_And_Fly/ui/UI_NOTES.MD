# Important Notes:


┌──────────────┐
│   main.py    │  (control loop)
│              │
│ Fish + Fly   │
│ Pipelines    │
└──────┬───────┘
       │
       │  (events / telemetry)
       ▼
┌────────────────────┐
│ garbage_log.csv    │  ← SINGLE SOURCE OF TRUTH
│ (or JSONL later)   │
└──────┬─────────────┘
       │
       ▼
┌────────────────────┐
│ Streamlit UI       │  (read-only)
│ app.py             │
└────────────────────┘


# Why this design?

```
Concern	Solution
Real-time system safety	main() runs alone
UI crashes	main keeps running
Mission replay	CSV can be replayed
Debugging	Logs are inspectable
Scaling	Replace CSV → DB later
```


# Mission progress tab

## Area-based Cleaning Assumption (v1)

This system uses an area-coverage abstraction for underwater cleaning:

- The Fish machine does not require prior knowledge of garbage locations
- Any region traversed underwater is considered cleaned
- Surface traversal represents pollution reduction (floating garbage collection)
- Spatial coverage is evaluated based on navigation path, not object density

This assumption simplifies perception uncertainty and aligns with
real-world coverage-based autonomous cleaning systems.

Future versions may incorporate object-density and confidence-weighted cleaning.


## Semantic story with color choice
```Dirty → Less dirty → Cleaning → Clean```

*Grid state → Color meaning*

| State                    | Meaning                  | Color            |
| ------------------------ | ------------------------ | ---------------- |
| **UNVISITED**            | Unknown                  | very light gray  |
| **POLLUTED_BASE**        | Highly polluted region   | **dark orange**  |
| **SURFACE_TRAVERSED**    | Floating garbage reduced | **light orange** |
| **CLEANED**              | Fully cleaned            | **dark blue**    |


### Why this works
- Orange always = pollution
- Blue always = clean
- Intensity change shows progress
- Final state visually converges to blue grid



