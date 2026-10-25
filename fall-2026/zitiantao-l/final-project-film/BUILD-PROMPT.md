# Rebuild prompt and commands

Prompt: Preserve the prior film. Build a course-version pitch that identifies the student's full RaycastGrasp implementation; shows genuine viewpoint changes for two specific objects; distinguishes gaze from target estimate; illustrates dwell accumulation, resetting and waiting; labels all constructed content; shows supplied setup/dataset images accurately; and gives project-specific verification cases. Keep progress statements scoped to the course version. Use free local narration and original Brutalist compilation/QC.

The exact English narration is in narration-v2.json. Native visual code is in eyespan_v2_draw.py and drawing_base.py. The run script measures actual audio before rendering, and uses original toolkit gates.

From this delivered project:
```powershell
python .\build_windows.py --toolkit 'F:\INFO7375-8\Final Project Pitch Film\brutalist.art' --project . --rerender
```
Add `--refresh-audio` to regenerate all narration with the original toolkit Kokoro script. Retained narration is hashed and reused otherwise. Source imagery is in pantry/, fonts and licence in fonts/, actual logs in reports/. No paid service or API key is required.
