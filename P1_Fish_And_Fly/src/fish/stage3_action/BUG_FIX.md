# Bugs I faced and how I solve them


```
YOLO bbox (image frame)
        ↓
Camera → World projection   ← THIS IS MISSING
        ↓
WorldObject (robot-centric)
        ↓
target_is_near(world_object, fish_state)

```

- I am earlier doing this: 
```
distance(
    target_bbox_center   ← IMAGE / CAMERA FRAME
    fish_position        ← WORLD / TOP-DOWN FRAME
)
```
These two live in different coordinate systems.


### Concept: 
You must NEVER compute distance across different frames. Before computing distance, both must be in the same coordinate frame.



### What I have earlier?

THE THREE FRAMES YOU CURRENTLY HAVE

Let’s name them explicitly:

1️⃣ Image frame (Camera / YOLO)

Pixels, Origin: `top-left`, Units: `pixels`, Axes: `+x right, +y down`


2️⃣ UI / Visualization frame

Still pixels, `Resized`, Just for display


3️⃣ Robot/world frame (Fish machine)

Origin: `fish center or map origin`, Units: `meters / arbitrary units`, Axes: `+x forward, +y sideways (usually)`



# Solution:

1️⃣ CameraToWorldProjector.py

📌 Purpose

- Convert YOLO bbox (image frame) → robot-centric 2D world
- Fish is always at (0, 0)
- Output is usable for distance checks

📌 Assumptions (explicit & realistic)

- Monocular camera
- Forward-facing
- Larger bbox ⇒ closer object

We only need relative distance, not metric perfection


# Explanation:

1️⃣ First: What problem are we solving?

You have:
- A camera image (pixels)
- A robot (fish) that moves forward
- Detected garbage as bounding boxes in pixels

You want to answer one simple question: ```“Is this object close enough in front of me to act?”```

You are NOT trying to:
- measure exact meters
- recover true 3D geometry
- do photogrammetry

So we build a relative, robot-centric approximation.


2️⃣ Coordinate frames involved

### Image frame (YOLO output)
```
(0,0) ─────────▶ x (pixels)
  │
  │
  ▼
  y
```
- Origin = top-left
- x → right
- y → down
- Units = pixels


### Robot-centric frame (what we want)
```
          +y (forward)
           ▲
           │
(-x) ◀─────┼─────▶ (+x)
           │
           │
         Fish (0,0)

```

- Origin = fish center
- x → left/right
- y → forward
- Units = relative distance



3️⃣ Step-by-step explanation of the formulas

Let’s take this bounding box: ```bbox = (x1, y1, x2, y2)```

🔹 STEP 1: Bounding box center
```
cx = (x1 + x2) / 2
cy = (y1 + y2) / 2
```
Why?

- The center of the box best represents object location
- Corners don’t tell where the object actually is

📌 This is still in pixel space

🔹 STEP 2: Normalize x (left / right)
```nx = (cx - img_width / 2) / (img_width / 2)```

### Break it down:
```
Expression	                                |                Meaning
------------------------------------------------------------------------------
img_width / 2	                                |               center of image
cx - center	                                |               offset from center
divide by half-width	                        |               scale to [-1, +1]
```

### Result:
```
nx = -1 → far left

nx = 0 → center (straight ahead)

nx = +1 → far right
```
📌 This matches robot left/right


🔹 STEP 3: Normalize y (far → near)
```ny = 1.0 - (cy / img_height)```

Why this works:

- cy increases downward
- Near objects appear lower in image
- Far objects appear higher

So we invert it:
```
cy	ny
top	~1.0 (far)
middle	~0.5
bottom	~0.0 (near)
```

📌 This is a depth proxy, not real depth


🔹 STEP 4: Distance from bounding box size
```
bbox_height = y2 - y1
distance = scale / bbox_height
```


### Intuition:

Same object:
```
far away → small bbox

close → large bbox
```
So:
```
larger height ⇒ smaller distance

smaller height ⇒ larger distance
```

📌 This is monocular depth estimation 101


🔹 STEP 5: Robot-centric world coordinates
```
world_x = nx * lateral_scale
world_y = distance
```

### Meaning:
```
world_x: left/right offset

world_y: forward distance
```
Fish is always at (0,0).
