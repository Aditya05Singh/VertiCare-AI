# Computer-Vision Eye Movement Screening Pipeline

This document describes the computer-vision architecture, facial/ocular landmark tracking, coordinate normalization, temporal kinematic feature extraction, and medical safety boundaries for the Eye Movement Screening subsystem in VertiCare AI.

---

## 1. System Overview & Purpose

The Computer Vision subsystem extracts objective, numerical eye-movement measurements from standard consumer webcams during a controlled 10-second screening protocol.

```
Webcam Video Stream
       │
       ▼
OpenCV Frame Preprocessing (Validation, 640x480 RGB normalization)
       │
       ▼
MediaPipe Facial Landmark Adapter (Controlled 468-point mesh mapping)
       │
       ▼
Scale-Normalized Ocular Coordinates (Inter-ocular distance baseline)
       │
       ▼
Temporal Sequence Processing (Actual timestamp delta_t, velocity, displacement)
       │
       ▼
Kinematic Feature Extraction (Amplitudes, velocities, direction changes, blinks)
       │
       ▼
Technical Quality Assessment (Valid tracking ratio >= 0.70)
       │
       ▼
Structured Feature Persistence (PostgreSQL eye_analysis_sessions & eye_movement_features)
```

---

## 2. Controlled Landmark Topology

Ocular landmarks use stable 3D mesh indices defined in `cv/src/landmarks.py`:

- **Left Eye Landmark Group:** Outer corner (33), Inner corner (133), Upper eyelid (159, 158), Lower eyelid (145, 144), Iris center (468).
- **Right Eye Landmark Group:** Outer corner (362), Inner corner (263), Upper eyelid (386, 385), Lower eyelid (374, 373), Iris center (473).
- **Facial Reference Points:** Nose tip (1), Chin (152), Forehead (10).

---

## 3. Coordinate Normalization Formula

To make ocular displacement independent of subject-to-camera distance and display resolution, coordinates are normalized by the inter-ocular distance $D$:

$$D = \sqrt{(x_{\text{right\_outer}} - x_{\text{left\_outer}})^2 + (y_{\text{right\_outer}} - y_{\text{left\_outer}})^2}$$

$$\bar{x} = \frac{x_{\text{center}} - x_{\text{midpoint}}}{D}, \quad \bar{y} = \frac{y_{\text{center}} - y_{\text{midpoint}}}{D}$$

---

## 4. Kinematic Feature Calculations

1. **Velocity ($\Delta t$ dependent):**
   $$v_x(t) = \frac{x(t) - x(t-1)}{t - (t-1)}, \quad v_y(t) = \frac{y(t) - y(t-1)}{t - (t-1)}$$
   *Zero or negative $\Delta t$ intervals are explicitly filtered.*
2. **Peak-to-Peak Amplitude:**
   $$A_h = \max(x) - \min(x), \quad A_v = \max(y) - \min(y)$$
3. **Direction Changes:**
   Counts sign changes in velocity where $|v(t)| > 0.01$ (noise gate).
4. **Eye Aspect Ratio (EAR) & Blink Rate:**
   $$\text{EAR} = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$
   Blinks are logged when $\text{EAR} < 0.20$ followed by reopen $\ge 0.24$.

---

## 5. Technical Quality Score & Safety Handling

- **Valid Frame Ratio:** $R = \frac{N_{\text{valid}}}{N_{\text{total}}}$
- If $R < 0.70$ or $N_{\text{valid}} < 10$: session is flagged as `INSUFFICIENT_QUALITY`.
- Patients are shown a neutral troubleshooting suggestion (adjust lighting / camera angle) rather than misleading medical feedback.

---

## 6. Privacy & Data Handling Architecture

- **No Raw Video Storage:** Raw webcam streams are processed locally in real time. Video frames are never written to disk or transmitted to backend databases.
- **Strict Numerical Feature Persistence:** Only validated floating-point kinematic measurements are saved to `eye_movement_features`.

---

## 7. Medical Safety & Non-Diagnostic Boundary

> [!CAUTION]
> **Academic Prototype Notice**
>
> This computer-vision module is an academic screening prototype.
> - It does **NOT** diagnose nystagmus, Benign Paroxysmal Positional Vertigo (BPPV), or central neurological lesions.
> - It does **NOT** replace clinical Videonystagmography (VNG), electronystagmography, or formal examination by a neurotologist.
> - All outputs represent observed computational features intended for physician consultation support.

