🟢 1. CORE BEHAVIOR (Must-Have)

These show your system basically works.

♻️ Case 1: Target → Collect
Input: Garbage object
Behavior: Detect → classify → move → collect
Output: Object removed
🎥 Clip: clean, smooth collection

🐟 Case 2: Environment Entity → Ignore
Input: Fish / plant
Behavior: Detect → classify → ignore
Output: No action
🎥 Show: bounding box present, robot does nothing

🪨 Case 3: Navigation Hazard → Avoid
Input: Rock / dangerous object
Behavior: Detect → avoid path
Output: Safe navigation
🎥 Show deviation in path

➡️ Case 4: No Object → Continue Exploration
Behavior: Forward movement / scanning
🎥 Simple but important



🟡 2. DECISION INTELLIGENCE (🔥 VERY IMPORTANT)

This is where you stand out.

⚠️ Case 5: Target Near Hazard → Avoid (NOT Collect)
Input: Garbage near hazard
Behavior: Safety prioritized
Output: Not collected
🎥 Must clearly show: both detected, decision = avoid

🎯 Case 6: Multiple Objects (Mixed Types)
Target + hazard + environment
Correct classification & prioritization
🎥 Shows system complexity handling

🧠 Case 7: Sequential Decisions
Detect → collect → move → avoid → continue
👉 This shows pipeline continuity



🔵 3. SYSTEM OPERATIONS (Real-World Feel)

🗑️ Case 8: Bin Full → Unload
Behavior: Stops collection → unload process
🎥 Very important for realism

🏁 Case 9: Mission Complete → Return to Base
Behavior: Coverage done → returns
🎥 Gives “full system lifecycle”



🔴 4. FAILURE & ROBUSTNESS
Most people skip this → YOU SHOULD NOT.

❌ Case 10: Detection Failure / Noisy Frame
Missed detection OR flicker
👉 Show system still stable

⚠️ Case 11: Video Feed / Sensor Issue → Abort
Behavior: Stops / safe state

🎥 Shows safety awareness

🔄 Case 12: Recovery (Optional but Powerful)
Temporary issue → system resumes



🟣 5. ADVANCED (OPTIONAL BUT IMPRESSIVE)

Only if easy to capture:

🗺️ Case 13: Coverage Completion Visualization
Heatmap fills
area covered

🤝 Case 14: Fish + Fly Coordination (if visible)
Drone monitoring
fish acting



🎯 FINAL RECOMMENDED SET (Balanced)

If you want perfect coverage without overload, record these:

✅ MUST INCLUDE (Top 10)
Target → Collect
Environment → Ignore
Hazard → Avoid
No object → Move
Target near hazard → Avoid
Multiple objects
Sequential pipeline
Bin full → Unload
Mission complete → Return
Abort / failure