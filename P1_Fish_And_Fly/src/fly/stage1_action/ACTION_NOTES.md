

# 1.) Heartbeat Monitor

I am using a technique `Cross-system reconciliation` for monitoring purpose. It means:

`Fish claims it sent a heartbeat at T — Fly received it at T+Δ`

That Δ is:
- latency
- scheduling delay
- simulation stall

This is how mature systems detect communication degradation, not just death.

## Meaning:

“I don’t just want to know if Fish is dead. I want to know if it’s lying, stuck, or slowing down.”

I  want Fly to detect:

- Communication loss → Fish dead / disconnected
- Execution freeze → Fish alive but not progressing
- System lag → Fish alive but slow / overloaded
- Mission stall → Same mission phase for too long


## Mental model:
```
Fly does not trust Fish.
Fly cross-checks Fish.
```


## All using delta analysis between:

`Fish’s claimed timestamp` and `Fly’s receipt time`


## Key idea: Track two clocks, not one

You need to track three times, not two:
```
Name	            |                        Meaning	                        |                Owner
-------------------------------------------------------------------------------------------------------------
fish_ts	            |                When Fish claims it sent heartbeat	        |             Fish
recv_ts	            |                    When Fly received it	                |              Fly
last_recv_ts	    |                  When Fly last heard anything	            |              Fly

```

From these you get two deltas:
```
Δ_comm = recv_ts - fish_ts                              (latency / scheduling lag)
Δ_silence = now - last_recv_ts                          (true liveness)
```


## What each condition means?

🟥 DEAD
`now - last_recv_ts > timeout`

It means Fly heard nothing → Fish unreachable


🟧 LAGGING
`now - fish_ts > freeze`

It means Fish is running, but:
- CPU overloaded
- blocked on IO
- slowed simulation
- message delivery delayed


🟨 FROZEN
`curr_emitted_fish_ts did not advance`

Fish loop is stuck:
- infinite loop
- blocking call
- deadlock
- mission planner not progressing


## Why this technique is used?

✅ Works in sync & async
✅ No false positives on startup
✅ Separates death from degradation
✅ Uses Fish timestamp correctly



## 2.) Flight Controller

### Why is FlightController so simple?
```
In v1, Fly acts as a supervisory agent.

The controller exposes intent-level actions only.

Physical control is intentionally abstracted so the focus stays on inter-robot coordination and fault detection.
```