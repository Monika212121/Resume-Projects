

# DEMO VIDEO FLOW — WHAT TO SAY + WHAT TO SHOW

---

## 1. INTRO (0:00 – 0:20)

### 🎥 SHOW

* Hero clips
* Fish movement
* Drone aerial view
* UI flashes
* Detection overlays
* Cinematic shots only

### 🎙️ SAY

Hi, I’m Monika Gadewar — a Software Developer.

Over the last few months I’ve been exploring how autonomous systems could contribute toward solving real world problems.

So, I am here to introduce you my project Fish & Fly, emerged from my growing concern about increasing water pollution and the long-term impact it has on aquatic ecosystems. 

It motivated me to explore how autonomous systems could evolve beyond passive monitoring into active environmental intervention.

---

## 2. QUICK DOCUMENTATION SHOWCASE (0:20 – 0:35)

### 🎥 SHOW

* Open Notion documentation
* Fast smooth scroll through sections
* Pause briefly on:

  * architecture
  * mission workflow
  * runtime visualization
  * recovery section
  * test cases

### 🎙️ SAY

I’ve fully documented the system architecture, coordination workflows, simulation framework, recovery mechanisms, and all runtime validation scenarios inside the project documentation linked in the description.

Instead of walking through every section individually, I’ll focus on a few runtime behaviors that best represent how the projet's ecosystem actually operates.

---

## 3. AUTONOMOUS TRAVERSAL + COLLECTION (0:35 – 1:00)

### 🎥 SHOW

Split screen:

* Perception
* Simulation
* UI

Show:

* nearest-object selection
* traversal
* collection

### 🎙️ SAY

The Fish agent continuously traverses the workspace while performing real-time environmental perception using the YOLO and OpenCV pipeline.

Detected entities are dynamically classified into waste targets, hazards, and environmental objects, allowing the system to make contextual navigation and collection decisions during runtime.

Here, the agent is autonomously prioritizing the nearest valid collection target during traversal.

---

## 4. HAZARD AVOIDANCE (1:00 – 1:20)

### 🎥 SHOW

* Rock avoidance
* Dolphin avoidance
* trajectory change
* path restore

### 🎙️ SAY

In this scenario, the agent encounters navigation hazards during active traversal.

Instead of continuing directly toward the target, the system dynamically modifies the trajectory, safely bypasses the obstacle region, and then re-aligns toward the original mission path once safe traversal conditions are restored.

---

## 5. COLLISION PREVENTION (1:20 – 1:35)

### 🎥 SHOW

* Fish stopping near Manatee
* Safe distance restore
* Fish resumes movement

### 🎙️ SAY

This sequence demonstrates coordinated multi-agent safety behavior.

When the Manatee unit enters the predefined operational threshold radius, the Fish agent temporarily pauses traversal until safe inter-agent separation is restored, preventing collision during concurrent execution.

---

## 6. DISPATCH + DUMP WORKFLOW (1:35 – 2:00)

### 🎥 SHOW

* collection increasing
* dispatch generation
* manatee traversal
* unloading
* dump color change

### 🎙️ SAY

As collection thresholds increase, the ecosystem transitions into coordinated logistics behavior.

Dispatch workflows are autonomously generated, allowing the Manatee unit to perform garbage transfer, unloading, and dump-cycle management within the active mission pipeline.

The dump-state visualization also transitions progressively as disposal accumulation increases across repeated unloading operations.

---

## 7. MISSION CONTROL INTERFACE (2:00 – 2:30)

### 🎥 SHOW

FAST cuts:

* Mission Intelligence
* Waste Analytics
* AI Decision Analytics
* Health Intelligence

Zoom slightly into graphs and insights.

### 🎙️ SAY

One of the most important parts of the ecosystem is runtime observability.

The Mission Control Interface provides synchronized telemetry visualization, traversal analytics, AI decision reasoning, operational health monitoring, and real-time mission-state awareness across the complete autonomous environment.

The AI Decision Analytics layer specifically tracks why objects are collected, ignored, avoided, or lost during runtime execution.

---

## 8. FAILURE RECOVERY (2:30 – 3:00)

### 🎥 SHOW

* fish abort
* return HQ
* failed recovery
* rescue dispatch
* manatee retrieval

### 🎙️ SAY

The ecosystem also incorporates layered fault-recovery behavior.

If the Fish agent encounters critical runtime instability, the active mission is safely aborted and the system transitions into autonomous recovery mode.

And if independent HQ recovery fails, an emergency rescue workflow is triggered through heartbeat-level synchronization, allowing the Manatee unit to autonomously retrieve and transport the failed agent back to HQ.

---

## 9. OUTRO (3:00 – 3:15)

### 🎥 SHOW

* clean environment
* all agents return HQ
* cinematic wide shot

### 🎙️ SAY

Fish & Fly is still evolving, but the long-term vision is to explore how scalable autonomous ecosystems could contribute toward real-world environmental monitoring and aquatic cleanup operations.

Thanks for watching.
