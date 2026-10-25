# EyeSpan — course project pitch
Zitiantao Lin | INFO7375-8

**1. What?** A gaze-guided assistive robot system for tabletop object selection, intended for people with limited upper-limb movement. The course version will deliver a repository with a system demonstration, implementation code, run instructions and verification records.

**2. Why care?** I independently implemented the full RaycastGrasp prototype, integrating mixed reality, eye tracking, object detection and robot control. Its earlier workflow used screenshots, manual cross-checking and category matching. A category cannot identify one of two cups. EyeSpan will pursue instance correspondence and continuous updates to reduce repeated submissions, retaining explicit confirmation. These are design goals, not measured improvements.

**3. Who?** Robotics perception and HRI hiring managers and engineers. Within their first minute, the finished portfolio will offer an interaction example, my contribution statement and code. This pitch uses labelled illustrations.

**4. What does it prove?** Existing gaze interaction and robot integration are supported by RaycastGrasp materials. Planned course evidence includes explicit prompt contracts and checks for missing inputs, invalid coordinates and unconfirmed execution requests, with actual prompts, revisions and results retained. The stack includes Python, eye tracking, paired camera views and a Franka arm.

**5. Scope and first?** Controlled tabletop, a few stationary objects; moving-object grasping is out. Mapping will use ego/exo images and gaze without requiring a pre-calibrated user-to-robot transform as prediction input. Device calibration and execution coordinates remain separate. The first milestone will replay a small licensed Ego-Exo4D sequence, logging target predictions, timestamps and settings against manually labelled references; ambiguous frames will be flagged. A public or synthetic example will support inspection without dataset access. Physical grasping requires separate robot evidence.

**6. Risk?** Look-alike targets can be confused. Smoothing can preserve an error or delay switching. I will inspect these cases, compare stability and switching response, and retain confirmation and cancellation before execution. Stable-looking, switching and alternating-look cases will accumulate dwell, reset it, or wait. Completing dwell requests confirmation; it does not authorize motion. Target-user evaluation remains future work.

**7. Why?** RaycastGrasp motivated the question of following a specific target across views and changing attention. Existing skills concern gaze interaction and system integration; new course learning concerns explicit contracts, independent verification and reproducibility. I have written the course concept and am starting this course version.

**Exists today**
- RaycastGrasp prototype and project materials; full prototype implementation is my contribution, as confirmed in this session.
- EyeSpan course concept and pitch materials, plus previously supplied background research materials (draft manuscript and figures), distinct from this course-version delivery.
- Ego-Exo4D access permission, confirmed by the author.

**Will exist**
- The documented EyeSpan course-version demonstration, implementation repository and run instructions.
- Additional replay/verification records, public or synthetic example, failure analysis and explicit limitations.
