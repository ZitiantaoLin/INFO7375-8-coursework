"""Collect the verified EyeSpan film and reproducible materials for Canvas/GitHub.

Read-only with respect to the working project. Copies an explicit allowlist,
checks the original compiler's hashes/reports, and verifies ZIP byte identity.
No upload, Git commit, invented human review, or publishing is performed.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def source_file(project, relative):
    relative=Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError(f'Expected a project-relative source: {relative}')
    candidate=project/relative
    if not candidate.is_file() or project not in candidate.resolve().parents:
        raise FileNotFoundError(f'Required project file missing or outside project: {candidate}')
    return candidate


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    project=args.project.resolve();out=args.out.resolve()
    if not project.is_dir():raise FileNotFoundError(project)
    if out==project or project in out.parents:
        raise ValueError('Keep the submission output outside the working project.')
    state=read_json(source_file(project,'build-state.json'))
    if state.get('status')!='ready':raise ValueError('Original compiler has not marked the film ready.')
    sheet=read_json(source_file(project,'beat_sheet.json'))
    beats=sheet.get('beats',[])
    build=sheet.get('metadata',{}).get('build',{})
    if len(beats)!=13 or build.get('slates') or build.get('filled')!=13:
        raise ValueError('Expected the verified 13/13 filled build, without slates.')
    master=source_file(project,'eyespan-final-project-pitch.mp4')
    if digest(master)!=state.get('sha256'):
        raise ValueError('The MP4 changed after verification; rebuild before packaging.')
    verified=read_json(source_file(project,'eyespan-final-project-pitch.verified.json'))
    if verified.get('sha256')!=state['sha256'] or verified.get('status')!='ready':
        raise ValueError('Final verification sidecar disagrees with the current master.')
    inputs=state.get('input_sha256',{})
    if len(inputs)<26:raise ValueError('Compiler input-hash inventory is incomplete.')
    for name,expected in inputs.items():
        file=Path(name).resolve()
        if project not in file.parents:
            raise ValueError(f'Unexpected compiler input outside this project: {file}')
        if not file.is_file() or digest(file)!=expected:
            raise ValueError(f'An audio/visual source changed after verification: {file}')
    type_report=source_file(project,'TYPECHECK.md').read_text(encoding='utf-8')
    frame_report=source_file(project,'reports/FINAL-REPORT.md').read_text(encoding='utf-8')
    if 'Overall: PASS' not in type_report:
        raise ValueError('Typography report does not show an overall pass.')
    if not re.search(r'BLOCKER:\s*0\b',frame_report) or not re.search(r'MAJOR:\s*0\b',frame_report):
        raise ValueError('Final frame report contains unresolved defects.')

    required=[
        'README.md','PROJECT-BRIEF.md','beat_sheet.json','BUILD-PROMPT.md',
        'SOURCES.md','FRICTIONAL.md','SHOTLIST.md','FACTCHECK.md','PROMPTS.md',
        'TYPECHECK.md','build-state.json','eyespan-final-project-pitch.mp4',
        'eyespan-final-project-pitch.verified.json','eyespan_draw.py',
        'build_windows.py','render-plan.json','BUILD-WINDOWS-ZH.md',
        'fonts/DejaVuSans.ttf','fonts/DejaVuSerif.ttf','fonts/DEJAVU-LICENSE.txt',
        'pantry/raycast_setup.png','pantry/dataset_overview_supplied.png',
        'reports/TYPECHECK.md','reports/FINAL-REPORT.md','reports/FINAL-contact_sheet.png',
        'reports/build-safety.log','reports/beat-lint.log','reports/gate-shape.log',
        'reports/type-check.log','reports/compile-final.log',
        'reports/toolkit-source-hashes.json','reports/visual-render.json',
    ]
    if (project/'v2-build.json').is_file():
        required.extend(['run_v2.py','drawing_base.py','eyespan_v2_draw.py','narration-v2.json','v2-build.json'])
    for b in beats:
        bid=b['beat_id']
        if not re.fullmatch(r'B\d\d',bid):raise ValueError(f'Unexpected beat ID: {bid}')
        required.extend([b['audio_file'],f'media/{bid}.mp4'])
    optional=[
        'NARRATION-EN.md','VISUAL-REVIEW-ZH.md','pantry/README.md',
        'pantry/raycast_pipeline.png','pantry/gazecast_system_diagram_supplied.png',
        'pantry/gazecast_photo_montage_supplied.png','mp3/timings.json',
        'reports/LOCAL-VALIDATION.md',
    ]
    # Validate the whole allowlist before creating a package.
    sources={name:source_file(project,name) for name in required}
    for name in optional:
        if (project/name).is_file():sources[name]=source_file(project,name)
    out.mkdir(parents=True,exist_ok=True)
    if (out/'fall-2026').exists() or (out/'Lin_Zitiantao_INFO7375_FinalProjectFilm.zip').exists():
        out=out/('revision-'+datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f'))
        out.mkdir()
    with tempfile.TemporaryDirectory(prefix='.pack-',dir=out) as scratch:
        scratch=Path(scratch)
        stage=scratch/'fall-2026/zitiantao-l/final-project-film';stage.mkdir(parents=True)
        for name,src in sources.items():
            dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        shutil.copyfile(Path(__file__).resolve(),stage/'prepare_submission.py')
        (stage/'.gitignore').write_text(
            '__pycache__/\n*.pyc\nnode_modules/\nclips/\n_work/\n_superseded/\n'
            'reports/superseded/\n*.candidate.mp4\n.env\n',encoding='utf-8')
        when=datetime.now().astimezone().isoformat(timespec='seconds')
        with (stage/'FRICTIONAL.md').open('a',encoding='utf-8') as f:
            f.write('\n\n## '+when+' — Submission package assembled\n'
                    'The packaging script checked the original compiler\'s ready state, the verified master hash, the unchanged audio/visual input hashes, Gate T, and the final frame report. It copied only the listed film, documentation, rebuild inputs and actual reports. It excluded caches, credentials, raw dataset bundles and conversation transcripts. ZIP bytes were checked against the matching GitHub folder. No GitHub commit or Canvas upload is claimed by this entry; full human playback is not inferred from automated checks.\n')
        manifest={str(p.relative_to(stage)).replace('\\','/'):digest(p)
                  for p in sorted(stage.rglob('*')) if p.is_file()}
        (stage/'SUBMISSION-MANIFEST.json').write_text(json.dumps({
            'assembled_at':when,'film_sha256':state['sha256'],
            'runtime_s':state['duration_s'],'files_sha256':manifest,
            'human_playback':'not inferred or certified by packaging',
            'github_commit':'not yet supplied','canvas_upload':'not performed',
        },indent=2)+'\n',encoding='utf-8')
        candidate=scratch/'Lin_Zitiantao_INFO7375_FinalProjectFilm.zip'
        files=sorted(p for p in stage.rglob('*') if p.is_file())
        with zipfile.ZipFile(candidate,'w',zipfile.ZIP_DEFLATED) as z:
            for p in files:z.write(p,Path('final-project-film')/p.relative_to(stage))
        with zipfile.ZipFile(candidate) as z:
            if z.testzip() is not None:raise ValueError('ZIP CRC check failed.')
            for p in files:
                name=(Path('final-project-film')/p.relative_to(stage)).as_posix()
                if hashlib.sha256(z.read(name)).hexdigest()!=digest(p):
                    raise ValueError('ZIP differs from the GitHub folder: '+name)
        destination=out/'fall-2026'
        shutil.move(str(scratch/'fall-2026'),destination)
        archive=out/candidate.name;shutil.move(str(candidate),archive)
    print('PACKAGED VERIFIED FILES — no upload or commit performed.')
    print('Canvas ZIP: '+str(archive))
    print('GitHub folder: '+str(destination/'zitiantao-l/final-project-film'))
    print('Film runtime: '+str(state['duration_s'])+' s')
    print('Film SHA256: '+state['sha256'])
    print('Watch the complete film, commit the matching folder, then include its URL and real commit hash in Canvas.')


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('PACKAGING STOPPED: '+str(exc),file=sys.stderr)
        raise SystemExit(2)
