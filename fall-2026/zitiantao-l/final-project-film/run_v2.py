"""Build EyeSpan V2 beside V1; retain V1, update changed narration and render locally."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path,data):
    p=Path(path);tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');tmp.replace(p)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()


def run(cmd,log):
    print('\n[v2] '+log.name,flush=True)
    with log.open('w',encoding='utf-8') as f:
        f.write('Arguments: '+json.dumps(list(map(str,cmd)))+'\n\n')
        proc=subprocess.Popen(list(map(str,cmd)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf-8',errors='replace')
        for line in proc.stdout:print(line,end='',flush=True);f.write(line);f.flush()
        rc=proc.wait();f.write('\nExit code: '+str(rc)+'\n')
    if rc:raise RuntimeError(f'Stopped at {log.name}, exit {rc}. Actual log retained; V1 is unchanged.')


def append_journal(p,title,text):
    with (p/'FRICTIONAL.md').open('a',encoding='utf-8') as f:
        f.write('\n\n## '+datetime.now().astimezone().isoformat(timespec='seconds')+' — '+title+'\n'+text+'\n')


def documents(p,toolkit):
    (p/'PROJECT-BRIEF.md').write_text('''# EyeSpan — course project pitch
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
''',encoding='utf-8')
    (p/'SOURCES.md').write_text('''# Sources and contributions

- Student: Zitiantao Lin supplied and revised the project concept, confirmed independent implementation of the full RaycastGrasp prototype, obtained dataset permission, ran the local build and reviewed the V1 narration/film. V2 full playback is not assumed.
- RaycastGrasp prototype: student implementation integrates MR, eye tracking, object detection and robot control. Paper authorship/other research credit remains as listed in the supplied manuscript; sole implementation does not erase coauthor credit.
- `pantry/raycast_setup.png`: supplied existing setup image, received 2026-10-24. The original capture date was not supplied. Scaling and explanatory guides do not establish live execution or measured performance.
- `pantry/dataset_overview_supplied.png`: scene montage prepared/supplied by the author, received 2026-10-24. The supplied background draft describes it as Ego-Exo4D scene examples and describes manual reference annotation. This pitch uses it as scene context; every prediction/reference comparison drawn beside it is constructed, not an executed result. The draft's numerical results were not independently reproduced and are not presented here as new course measurements.
- Temporal charts: original native drawings based on the student-supplied Formation/Switching/Deliberation concept. Constructed behaviour examples, not measured traces. Dwell completion is labelled as requesting confirmation; no universal optimal threshold or proven safety is claimed.
- Ego-Exo4D: author confirmed licensed access. No raw dataset bundle, credentials or private transcripts are included. Official documentation: https://docs.ego-exo4d-data.org/ . Public sharing must follow the actual license held.
- Brutalist: https://github.com/nikbearbrown/brutalist.art . Original local Kokoro generation, compiler and applicable QC are invoked without bypasses. Toolkit source, node_modules and model weights are not bundled.
- Voice: local Kokoro am_onyx preset. Script speaks as Zitiantao Lin; no instructor persona, portrait, greeting or channel credit is used.
- Visuals: original Pillow/FFmpeg drawings and media-slot composition prepared with ChatGPT, using the toolkit's show-tell palette vocabulary. Concept frames are labelled Constructed. No paid generation, stock music or external media account is used.
- Fonts: bundled unchanged DejaVu Sans and Serif; fonts/DEJAVU-LICENSE.txt contains the license notice.
- ChatGPT: narration revision, translations, shot design, native rendering code, build scripts and review suggestions. Claude contribution: none confirmed.
- Automated QC does not establish scientific correctness, intended-user validation or complete human playback. Reports are actual local command outputs; Manim-only A/W/B and publishing-only 4K passes are not claimed.
''',encoding='utf-8')
    (p/'BUILD-PROMPT.md').write_text('''# Rebuild prompt and commands

Prompt: Preserve the prior film. Build a course-version pitch that identifies the student's full RaycastGrasp implementation; shows genuine viewpoint changes for two specific objects; distinguishes gaze from target estimate; illustrates dwell accumulation, resetting and waiting; labels all constructed content; shows supplied setup/dataset images accurately; and gives project-specific verification cases. Keep progress statements scoped to the course version. Use free local narration and original Brutalist compilation/QC.

The exact English narration is in narration-v2.json. Native visual code is in eyespan_v2_draw.py and drawing_base.py. The run script measures actual audio before rendering, and uses original toolkit gates.

From this delivered project:
```powershell
python .\\build_windows.py --toolkit 'TOOLKIT_PATH' --project . --rerender
```
Add `--refresh-audio` to regenerate all narration with the original toolkit Kokoro script. Retained narration is hashed and reused otherwise. Source imagery is in pantry/, fonts and licence in fonts/, actual logs in reports/. No paid service or API key is required.
'''.replace('TOOLKIT_PATH',str(toolkit)),encoding='utf-8')
    (p/'FACTCHECK.md').write_text('''# Claim review — not an algorithm evaluation report

RaycastGrasp independent prototype implementation: author's explicit confirmation. Existing setup photograph supports equipment context, not every implementation claim or performance. Retain correct paper/team credit.

EyeSpan starting work: refers to this course version. Earlier supplied draft/figures are recorded as background materials; nothing is asserted to have been absent or invented from zero. Planned artifact, target population, three interaction responses, mapping-input boundary, checks and scope are future commitments.

Ego-Exo4D permission: author confirmation. Scene collage is not EyeSpan prediction evidence. Reference/estimate drawings and temporal traces are labelled constructed. No fabricated users, numerical results or testimonials. Prior draft performance is not repackaged as new course work. Target-user evaluation remains future work.
''',encoding='utf-8')
    (p/'PROMPTS.md').write_text('# Visual work order\n\nUse one scene per beat from narration-v2.json. Keep gaze, estimate and confirmation distinct; show the same physical A/B instances from different constructed viewpoints. Photograph and dataset examples have source-status labels. No fake executed output. See SHOTLIST.md and native scene source.\n',encoding='utf-8')
    plans=[
     'Two constructed viewpoints of the same tabletop instances; a shared target is indicated.',
     'Same objects from different viewpoints; gaze, mapped instance, confirmation and illustrative grasp are staged.',
     'Large supplied RaycastGrasp setup photo beside the four modules implemented by the student.',
     'Category ambiguity versus the proposed instance-level goal; no measured comparison.',
     'Three explicit temporal traces: dwell accumulation, reset and waiting. Completion requests confirmation.',
     'Two view inputs and gaze inside the mapping boundary; calibration/execution remain separate.',
     'Constructed first-minute portfolio with demo, code and contribution statement.',
     'Course concept written; course build beginning; repository delivery planned.',
     'Supplied dataset scene context plus a separate constructed reference/prediction comparison.',
     'Controlled stationary tabletop; intended-user evaluation explicitly future.',
     'Gaze and estimate traces illustrate delayed switching; no measured latency. Confirm/cancel before execution.',
     'Concrete proposed contract: views/gaze/time to target/state, with three rejected-input/request cases.',
     'A target changes across distinct views; student name and intended role close the pitch.'
    ]
    (p/'SHOTLIST.md').write_text('# V2 shot plan\n\n| Beat | Scene | Status |\n|---|---|---|\n'+'\n'.join(f'| B{i:02d} | {text} | '+('Existing setup; illustrative composition' if i==2 else 'Supplied scenes; constructed check' if i==8 else 'Constructed')+' |' for i,text in enumerate(plans))+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,help='V1 project, read-only; needed only on first run')
    ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--toolkit',type=Path,required=True)
    ap.add_argument('--rerender',action='store_true')
    ap.add_argument('--refresh-audio',action='store_true')
    ap.add_argument('--prepare-only',action='store_true',help='Write/validate a V2 work folder without generating new audio or a film.')
    a=ap.parse_args();p=a.project.resolve();toolkit=a.toolkit.resolve()
    scripts=toolkit/'runtime/scripts';qc=toolkit/'runtime/qc'
    for f in [scripts/'generate_audio_kokoro.py',scripts/'build_safety.py',scripts/'type_check.py',scripts/'compile.py',qc/'final_frame_check.py']:
        if not f.is_file():raise FileNotFoundError(f)
    os.environ.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONUNBUFFERED='1')
    temp=p.parent/'.cache/eyespan-v2-tmp';temp.mkdir(parents=True,exist_ok=True)
    for key in ['TEMP','TMP','TMPDIR']:os.environ[key]=str(temp)
    narration=read(ROOT/'narration-v2.json');fingerprint=sha(ROOT/'narration-v2.json')
    marker=p/'v2-build.json'
    if p.exists() and not marker.is_file():raise ValueError('Destination already exists without a V2 marker. Choose a fresh --project path.')
    first=not p.exists()
    if first:
        if not a.source:raise ValueError('--source is required for the first V2 build.')
        source=a.source.resolve()
        if source==p or source in p.parents or p in source.parents:raise ValueError('Use a separate sibling destination to preserve V1.')
        original=read(source/'beat_sheet.json')
        if len(original.get('beats',[]))!=13:raise ValueError('Expected 13 V1 beats.')
        p.mkdir(parents=True);(p/'mp3').mkdir();(p/'reports').mkdir()
        if (source/'FRICTIONAL.md').is_file():shutil.copyfile(source/'FRICTIONAL.md',p/'FRICTIONAL.md')
        else:(p/'FRICTIONAL.md').write_text('# Frictional journal\n',encoding='utf-8')
        changed=[];sheet=copy.deepcopy(original)
        for b,n in zip(sheet['beats'],narration['beats']):
            if b['beat_id']!=n['beat_id']:raise ValueError('Beat order differs.')
            track=source/b.get('audio_file',f"mp3/beat-{b['beat_id']}.mp3")
            if not track.is_file():raise FileNotFoundError(track)
            shutil.copyfile(track,p/'mp3'/track.name)
            if b['narration_text']!=n['narration_text']:
                changed.append(b['beat_id']);b.pop('actual_duration_s',None)
            b['narration_text']=n['narration_text'];b['estimated_duration_s']=round(len(n['narration_text'].split())/140*60,2)
            b['audio_file']=f"mp3/beat-{b['beat_id']}.mp3"
            b.pop('build',None);b.pop('render_duration_s',None);b.pop('qc',None)
            b['shot']={'type':'COMPOSITE','lane':'vox','source':'own','treatment':'none','renderer':'eyespan_v2_draw.py','render_status':'planned'}
        sheet['metadata'].pop('build',None);sheet['metadata']['revision']='v2'
        sheet['metadata']['production_status']='v2_narration_pending'
        write(p/'beat_sheet.json',sheet)
        if (source/'mp3/timings.json').is_file():shutil.copyfile(source/'mp3/timings.json',p/'mp3/timings.json')
        write(marker,{'version':'eyespan-course-pitch-v2','narration_fingerprint':fingerprint,'changed_beats':changed,'source_project':str(source),'audio_complete':False})
        documents(p,toolkit)
        append_journal(p,'V2 revision started','V1 was retained in its original directory. The author confirmed independent RaycastGrasp prototype implementation and requested clearer temporal mechanisms and stronger visual explanation. Starting work is scoped to the course version. Prior research materials remain distinguished from course outputs. No new algorithm result is claimed.')
    state=read(marker)
    if state.get('narration_fingerprint')!=fingerprint:raise ValueError('This destination belongs to a different V2 narration revision.')
    for name in ['run_v2.py','build_windows.py','eyespan_draw.py','eyespan_v2_draw.py','drawing_base.py','prepare_submission.py','narration-v2.json','BUILD-WINDOWS-ZH.md']:
        src=ROOT/name;dst=p/name
        if src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
    for folder in ['fonts','pantry']:
        for src in (ROOT/folder).rglob('*'):
            if src.is_file():
                dst=p/src.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True)
                if src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
    reports=p/'reports'
    run([sys.executable,scripts/'build_safety.py',p],reports/'build-safety.log')
    if a.prepare_only:
        print('[v2] Prepared and validated configuration only; no V2 narration or master generated.');return 0
    need=state['changed_beats']
    if a.refresh_audio:need=[b['beat_id'] for b in narration['beats']]
    audio_valid=state.get('audio_complete') and all((p/name).is_file() and sha(p/name)==value for name,value in state.get('audio_hashes',{}).items())
    if not audio_valid or a.refresh_audio:
        print('[v2] Generating changed narration: '+', '.join(need),flush=True)
        if need:run([sys.executable,scripts/'generate_audio_kokoro.py',p,'--speed','1.0','--only',*need],reports/'narration-v2.log')
        sheet=read(p/'beat_sheet.json')
        state['audio_complete']=True
        state['audio_hashes']={b['audio_file']:sha(p/b['audio_file']) for b in sheet['beats']}
        write(marker,state)
    else:print('[v2] Retained completed V2 narration.',flush=True)
    sheet=read(p/'beat_sheet.json');total=sum(b['actual_duration_s'] for b in sheet['beats'])
    print(f'[v2] MEASURED NARRATION: {total:.2f}s',flush=True)
    if total>240:raise ValueError('Measured narration exceeds four minutes; revise before final rendering.')
    signature=sha(p/'eyespan_v2_draw.py')+sha(p/'drawing_base.py')
    force=a.rerender or state.get('render_signature')!=signature
    run([sys.executable,p/'eyespan_draw.py','--project',p]+(['--force'] if force else []),reports/'native-render-v2.log')
    inventory=read(reports/'text-inventory.json')
    for b in sheet['beats']:
        b['qc']={'typography_regions':inventory[b['beat_id']],'typography_reason':'Complete authored text inventory, including alternate labels. Diagram edges and supplied image texture are not text. Full unmasked frames still undergo original Gate V without sparse, full-bleed or regional-contrast waivers.'}
        b['shot']['render_status']='rendered_visual_only'
        b['duration_status']='measured_local_kokoro'
        b.pop('build',None);b.pop('render_duration_s',None)
    sheet['metadata'].pop('build',None);sheet['metadata']['production_status']='v2_audio_and_visuals_ready_master_pending'
    write(p/'beat_sheet.json',sheet);write(p/'render-plan.json',{'beats':sheet['beats'],'narration_fingerprint':fingerprint})
    state['render_signature']=signature;write(marker,state)
    run([sys.executable,qc/'beat_lint.py',p],reports/'beat-lint.log')
    run([sys.executable,qc/'gate_shape.py',p],reports/'gate-shape.log')
    run([sys.executable,scripts/'type_check.py',p],reports/'type-check.log')
    shutil.copyfile(p/'TYPECHECK.md',reports/'TYPECHECK.md')
    write(reports/'toolkit-source-hashes.json',{str(f.relative_to(toolkit)):sha(f) for f in [scripts/'compile.py',scripts/'type_check.py',qc/'final_frame_check.py']})
    run([sys.executable,scripts/'compile.py',p,'--height','1080','--fps','24','--out',p],reports/'compile-final.log')
    final=read(p/'build-state.json');master=Path(final['output'])
    if final.get('status')!='ready' or sha(master)!=final['sha256']:raise ValueError('Final verification state/hash is inconsistent.')
    for f in ['REPORT.md','contact_sheet.png']:shutil.copyfile(p/'_qc'/f,reports/('FINAL-'+f))
    (p/'README.md').write_text('# EyeSpan — Final Project Pitch Film, V2\n\nAuthor: Zitiantao Lin  \nCourse: INFO7375-8  \nTarget role: robotics perception / HRI engineer  \nWorking title: EyeSpan: Gaze Across Views and Time  \nRuntime: '+str(final['duration_s'])+' seconds (1920 x 1080, 24 fps).\n\nThis is a course-version pitch. Concept scenes, temporal traces and reference comparisons are constructed. The supplied RaycastGrasp photo shows existing work. Dataset scene images are not prediction results. No new scientific performance or intended-user validation is claimed.\n\n## Rebuild\nActivate the existing local Python environment with Pillow, NumPy, SciPy and FFmpeg, and keep narration/source files and fonts. Use the original Brutalist checkout:\n```powershell\npython .\\build_windows.py --project . --toolkit \''+str(toolkit)+'\' --rerender\n```\nAdd --refresh-audio for full narration regeneration; omit it to retain measured MP3s. Original gates and compiler verify the actual film; no Manim-only or publishing-only passes are claimed.\n\n## Submission\nCanvas: Lin_Zitiantao_INFO7375_FinalProjectFilm.zip. GitHub: fall-2026/zitiantao-l/final-project-film/. Keep matching contents and add the real folder URL/commit hash in Canvas. Full human playback remains to be confirmed.\n',encoding='utf-8')
    append_journal(p,'V2 original compiler completed',f'Actual revised narration totals {total:.2f}s. The original compiler verified the {final["duration_s"]:.3f}s film, audio, source hashes and full decoding; 13 visual slots were filled. Actual Gate T and final Gate V reports are retained. Human full playback and GitHub/Canvas submission are not inferred from these automated results.')
    print('\n[v2] VERIFIED MASTER: '+str(master),flush=True)
    print('[v2] V1 was preserved. Watch V2 completely before final packaging.',flush=True)
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as exc:
        print('[v2] STOPPED: '+str(exc),file=sys.stderr);raise SystemExit(2)
