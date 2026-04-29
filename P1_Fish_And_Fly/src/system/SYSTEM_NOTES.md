

# Project Architecture


```
Fish → heartbeat → Fly

Fly:
    → normal DMS decisions
    → ALSO checks mission_state

    if FAILED → RESCUE
    if COMPLETED → FINAL SWEEP

Manatee:
    → executes

Fly:
    → receives outcome
    → if FINAL SWEEP done → STOP SYSTEM

```