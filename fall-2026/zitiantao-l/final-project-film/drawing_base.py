"""EyeSpan pitch: original local vector-style drawings, Pillow -> FFmpeg.

The output is illustrative media for Brutalist's documented media/<beat>.mp4
slots. Nothing in these drawings is a recorded robot or algorithm execution.
Read the measured beat sheet; never regenerate or retime narration here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BG = '#F2F0E9'
INK = '#3D3929'
ACCENT = '#D97757'
GREY = '#8B8F96'
KRAFT = '#DCC9AA'
PALE = '#FAF9F5'
TITLES = {
    'B00': 'Different views. One target.',
    'B01': 'EyeSpan',
    'B02': 'The research foundation',
    'B03': 'Which cup?',
    'B04': 'Attention changes over time',
    'B05': 'Two views and a gaze point',
    'B06': 'A portfolio people can inspect',
    'B07': 'Existing research. Course delivery.',
    'B08': 'Verify the target mapping',
    'B09': 'Start with a controlled tabletop',
    'B10': 'A wrong target can persist',
    'B11': 'Specify. Check. Revise.',
    'B12': 'EyeSpan',
}


def ease(t):
    t = min(1., max(0., t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return tuple(x + (y-x)*t for x, y in zip(a, b))


@lru_cache(maxsize=64)
def font(size, serif=False):
    return ImageFont.truetype(str(ROOT/'fonts'/('DejaVuSerif.ttf' if serif else 'DejaVuSans.ttf')), size)


@lru_cache(maxsize=32)
def scaled_image(path, width, height):
    im = Image.open(path).convert('RGB')
    im.thumbnail((width, height), Image.Resampling.LANCZOS)
    return im


class Canvas:
    def __init__(self, height=1080):
        self.s = height / 1080
        self.im = Image.new('RGB', (round(1920*self.s), height), BG)
        self.d = ImageDraw.Draw(self.im)
        self.texts = []

    def pt(self, p):
        return tuple(round(v*self.s) for v in p)

    def txt(self, text, x, y, size=40, anchor='mm', serif=False):
        f = font(max(1, round(size*self.s)), serif)
        xy = self.pt((x, y))
        self.d.text(xy, text, fill=INK, font=f, anchor=anchor)
        b = self.d.textbbox(xy, text, font=f, anchor=anchor)
        w, h = self.im.size
        box = [max(0., (b[0]-8*self.s)/w), max(0., (b[1]-8*self.s)/h),
               min(1., (b[2]+8*self.s)/w), min(1., (b[3]+8*self.s)/h)]
        if b[0] < 96*self.s or b[2] > 1824*self.s or b[1] < 54*self.s or b[3] > 1026*self.s:
            raise ValueError(f'Text outside safe area: {text!r}: {b}')
        self.texts.append({'label': text, 'box': box})

    def line(self, pts, color=INK, width=5):
        self.d.line([self.pt(p) for p in pts], fill=color, width=max(1, round(width*self.s)), joint='curve')

    def poly(self, pts, fill=KRAFT, outline=INK, width=4):
        ps = [self.pt(p) for p in pts]
        self.d.polygon(ps, fill=fill)
        if outline:
            self.d.line(ps+[ps[0]], fill=outline, width=max(1, round(width*self.s)), joint='curve')

    def rect(self, box, fill=PALE, outline=INK, width=4, radius=14):
        self.d.rounded_rectangle(self.pt(box), radius=round(radius*self.s), fill=fill,
                                 outline=outline, width=max(1, round(width*self.s)))

    def ellipse(self, box, fill=None, outline=INK, width=4):
        self.d.ellipse(self.pt(box), fill=fill, outline=outline, width=max(1, round(width*self.s)))

    def dot(self, x, y, r=10, color=ACCENT):
        self.ellipse((x-r,y-r,x+r,y+r),fill=color,outline=None)

    def ring(self, x, y, r=47, color=INK):
        self.ellipse((x-r,y-r,x+r,y+r),outline=color,width=6)

    def arrow(self, a, b, color=INK, width=5, head=17):
        self.line([a,b],color,width)
        ang = math.atan2(b[1]-a[1],b[0]-a[0])
        tip1=(b[0]-head*math.cos(ang-.5),b[1]-head*math.sin(ang-.5))
        tip2=(b[0]-head*math.cos(ang+.5),b[1]-head*math.sin(ang+.5))
        self.poly([b,tip1,tip2],color,None)

    def image(self, path, box):
        x0,y0,x1,y1=box
        im=scaled_image(str(path),round((x1-x0)*self.s),round((y1-y0)*self.s))
        x=round((x0+x1)*self.s/2-im.width/2);y=round((y0+y1)*self.s/2-im.height/2)
        self.im.paste(im,(x,y))
        return x/self.s,y/self.s,(x+im.width)/self.s,(y+im.height)/self.s


def cup(c,x,y,s=1.,stripe=False):
    c.ellipse((x+22*s,y-50*s,x+100*s,y+25*s),fill=BG,width=6)
    c.rect((x-58*s,y-90*s,x+53*s,y+55*s),fill=KRAFT,radius=20*s,width=5)
    c.ellipse((x-58*s,y-103*s,x+53*s,y-70*s),fill=PALE,width=5)
    if stripe:c.line([(x-53*s,y+13*s),(x+48*s,y+13*s)],color=GREY,width=12*s)


def box3d(c,x,y,w=200,d=95,h=105):
    # Same elementary x/y/z isometric projection as the toolkit's show-tell kit.
    c.poly([(x-w/2,y),(x,y+d/2),(x,y+d/2-h),(x-w/2,y-h)],'#C7AE86')
    c.poly([(x,y+d/2),(x+w/2,y),(x+w/2,y-h),(x,y+d/2-h)],KRAFT)
    c.poly([(x-w/2,y-h),(x,y-h-d/2),(x+w/2,y-h),(x,y-h+d/2)],'#F3E9D8')


def camera(c,x,y,s=1.,direction=1):
    c.rect((x-85*s,y-58*s,x+75*s,y+52*s),fill=KRAFT,radius=14*s)
    c.ellipse((x-35*s,y-35*s,x+37*s,y+37*s),fill=PALE,width=7)
    c.dot(x,y,13*s,INK)
    c.poly([(x+75*s*direction,y-26*s),(x+125*s*direction,y-50*s),
            (x+125*s*direction,y+45*s),(x+75*s*direction,y+22*s)],fill=GREY)


def tabletop(c,x=960,y=600,s=1.):
    c.poly([(x-450*s,y),(x-70*s,y-150*s),(x+450*s,y),(x+70*s,y+150*s)],fill='#C7AE86')
    c.line([(x-405*s,y+18*s),(x-405*s,y+150*s)],width=9)
    c.line([(x+405*s,y+18*s),(x+405*s,y+150*s)],width=9)
    c.line([(x+70*s,y+150*s),(x+70*s,y+235*s)],width=9)


def robot(c,x,y,s=1.,reach=0.):
    base=(x,y);elbow=(x-70*s,y-170*s);wrist=(x+100*s+70*s*reach,y-255*s+60*s*reach)
    c.ellipse((x-100*s,y-20*s,x+100*s,y+30*s),fill=GREY,width=5)
    c.line([base,elbow,wrist],color=INK,width=42*s)
    c.line([base,elbow,wrist],color=PALE,width=29*s)
    for a,b in (base,elbow,wrist):c.ellipse((a-24*s,b-24*s,a+24*s,b+24*s),fill=KRAFT,width=5)
    wx,wy=wrist
    c.line([(wx-20*s,wy),(wx-20*s,wy+55*s),(wx-7*s,wy+65*s)],width=7*s)
    c.line([(wx+20*s,wy),(wx+20*s,wy+55*s),(wx+7*s,wy+65*s)],width=7*s)


def page(c,x,y,s=1.,play=False,check=False):
    c.rect((x-95*s,y-115*s,x+95*s,y+115*s),fill=PALE,radius=8*s)
    if play:
        c.poly([(x-25*s,y-45*s),(x+45*s,y),(x-25*s,y+45*s)],fill=INK)
    else:
        for i in range(3):c.line([(x-58*s,y-55*s+45*s*i),(x+52*s,y-55*s+45*s*i)],color=GREY,width=8*s)
    if check:tick(c,x+72*s,y+68*s,25*s)


def tick(c,x,y,s=28):
    c.line([(x-s,y),(x-s*.25,y+s*.7),(x+s,y-s*.8)],color=INK,width=8)


def twin(c, p=0., two=False):
    c.rect((170,300,820,740),fill=PALE)
    c.rect((1100,300,1750,740),fill=PALE)
    cup(c,430,580,1.1)
    cup(c,1450,545,1.1)
    if two:
        cup(c,640,560,.9,True);cup(c,1220,600,.9,True)
    c.txt('User view',495,810)
    c.txt('Robot view',1425,810)


def render_frame(bid,t,duration,height=1080):
    u=min(1.,max(0.,t/duration));c=Canvas(height)
    c.txt('PROJECT PITCH',132,75,32,anchor='lm')
    c.txt(TITLES[bid],132,149,58,anchor='lm',serif=True)
    footer='Constructed'
    if bid=='B00':
        tabletop(c,960,595,.78);cup(c,960,545,1.12)
        camera(c,370,455,.85);camera(c,1480,455,.85,-1)
        c.line([(475,458),(905,520)],GREY,5)
        c.line([(1375,458),(1020,520)],GREY,5)
        a=lerp((475,458),(905,520),ease(u*2));c.dot(*a,12)
        if u>.3:c.dot(*lerp((1375,458),(1020,520),ease((u-.3)*2)),12)
        if u>.65:c.ring(960,520,82)
        c.txt('Your view',370,810);c.txt('Another view',1480,810)
    elif bid=='B01':
        twin(c)
        c.ring(430,555,82);c.dot(430,555,11)
        if u>.18:
            c.arrow((850,510),lerp((850,510),(1060,510),ease((u-.18)*5)))
        if u>.35:c.ring(1450,535,82)
        if u>.6:tick(c,976,650,36)
        if u>.74:
            # An illustrated gripper, never footage of a robot action.
            gx=1450;gy=405+ease((u-.74)*4)*45
            c.line([(gx-40,gy-50),(gx-40,gy+35),(gx-20,gy+50)],width=9)
            c.line([(gx+40,gy-50),(gx+40,gy+35),(gx+20,gy+50)],width=9)
        labels=['Look','Locate','Confirm','Grasp']
        phase=0 if u<.3 else 1 if u<.6 else 2 if u<.74 else 3
        c.txt(labels[phase],960,875,44)
    elif bid=='B02':
        b=c.image(ROOT/'pantry/raycast_setup.png',(210,235,1710,850))
        # Focus guides are annotations, not measurements or animated source footage.
        x=b[0]+(b[2]-b[0])*(.26 if u<.52 else .72)
        y=b[1]+(b[3]-b[1])*.45
        r=92+10*math.sin(u*math.pi*2)
        c.ring(x,y,r,color=ACCENT)
        footer='Existing setup / illustrative highlight'
    elif bid=='B03':
        twin(c,two=True)
        c.ring(430,555,82)
        c.line([(860,510),(975,510),(1035,450)],GREY,5)
        c.line([(975,510),(1035,585)],GREY,5)
        c.dot(*lerp((860,510),(975,510),ease(u*3)),12)
        if u>.45:
            c.ring(1220,580,74,color=GREY);c.ring(1450,535,82,color=GREY)
        c.txt('Same category',960,875,44)
    elif bid=='B04':
        tabletop(c,960,545,.88);cup(c,740,500,1.05);cup(c,1190,500,1.05,True)
        if u<.36:x=740;state='Hold'
        elif u<.64:x=740+450*ease((u-.36)/.2);state='Switch'
        else:x=965+225*math.cos((u-.64)*math.pi*12);state='Undecided'
        c.ring(x,470,81);c.dot(x,470,12)
        c.line([(430,815),(1490,815)],GREY,5)
        c.line([(430,815),(430+1060*u,815)],INK,8)
        for i in range(13):
            if i/12<u:c.dot(430+i/12*1060,815,7,INK)
        c.txt(state,960,895,44)
    elif bid=='B05':
        c.rect((230,285,780,525));c.rect((230,585,780,825))
        cup(c,500,430,.72);cup(c,565,730,.72)
        c.dot(500,408,13)
        c.arrow((820,425),(1060,510));c.arrow((820,695),(1060,585))
        c.rect((1110,345,1700,755));cup(c,1410,600,1.2)
        c.ring(1410,570,84+4*math.sin(u*math.pi*2))
        c.txt('User view + gaze',500,245,38)
        c.txt('Robot view',500,875,38)
        c.txt('Target mapping',1405,825,40)
        c.dot(*lerp((840,430),(1040,500),ease((u%.45)/.45)),10)
    elif bid=='B06':
        # A drawn portfolio structure, without a fabricated interface or code output.
        box3d(c,390,650,300,160,155)
        c.arrow((610,560),(850,560))
        page(c,1030,540,1.35,play=True)
        page(c,1470,410,.8);page(c,1470,705,.8)
        c.line([(1210,540),(1280,540),(1280,410),(1355,410)],GREY,5)
        c.line([(1280,540),(1280,705),(1355,705)],GREY,5)
        c.dot(*lerp((610,560),(850,560),ease(min(1,u*2))),12)
        if u>.5:tick(c,1110,685,28)
        c.txt('First 60 seconds',1030,795,38);c.txt('Code',1470,245);c.txt('My contribution',1470,875,38)
        footer='Constructed / planned portfolio'
    elif bid=='B07':
        c.line([(960,295),(960,850)],GREY,4)
        robot(c,415,700,.8);page(c,715,535,.95)
        page(c,1250,440,.95,play=True);page(c,1560,680,.95,check=u>.5)
        c.arrow((1245,610),(1435,675),GREY)
        if u>.28:c.dot(*lerp((1245,610),(1435,675),ease((u-.28)*2)),11)
        c.txt('Exists today',560,870,42);c.txt('Course delivery',1405,870,42)
    elif bid=='B08':
        c.image(ROOT/'pantry/dataset_overview_supplied.png',(155,255,1155,865))
        c.arrow((1175,560),(1310,560))
        page(c,1490,505,1.15,play=True)
        c.line([(1375,755),(1680,755)],GREY,5)
        c.dot(1375+305*u,755,12)
        c.txt('Planned replay',1505,850,40)
        footer='Dataset examples / validation planned'
    elif bid=='B09':
        tabletop(c,870,570,1.05)
        cup(c,685,535,.9);cup(c,980,500,.9,True)
        box3d(c,850,650,95,65,70)
        robot(c,1515,750,.9,reach=ease(u))
        c.line([(330,810),(330,330),(1280,330),(1280,810)],GREY,4)
        c.dot(330+950*ease(u),330,11)
        c.txt('Stationary objects',835,895,42)
        footer='Constructed / planned scope'
    elif bid=='B10':
        cup(c,590,530,1.5);cup(c,1300,530,1.5,True)
        gx=590+710*ease((u-.15)/.25)
        c.dot(gx,440,16)
        # Prediction stays on A while the gaze shifts to B: explicit failure illustration.
        c.ring(590,490,130)
        if u>.3:c.arrow((760,400),(1120,400),GREY)
        c.rect((775,670,1150,810),fill=PALE)
        c.line([(865,705),(865,775)],width=17);c.line([(920,705),(920,775)],width=17)
        if u>.68:
            c.line([(1030,715),(1090,775)],width=7);c.line([(1090,715),(1030,775)],width=7)
        c.txt('Confirm or cancel',960,895,42)
    elif bid=='B11':
        xs=[380,955,1530]
        page(c,xs[0],550,1.1)
        page(c,xs[1],550,1.1,check=u>.32)
        page(c,xs[2],550,1.1)
        c.arrow((535,550),(790,550),GREY);c.arrow((1110,550),(1365,550),GREY)
        if u>.68:
            c.line([(1510,470),(1550,470)],INK,11)
            c.line([(1510,520),(1560,520)],INK,11)
        if u>.15:c.dot(*lerp((535,550),(790,550),ease((u-.15)*4)),12)
        if u>.5:c.dot(*lerp((1110,550),(1365,550),ease((u-.5)*3)),12)
        c.txt('Contract',xs[0],810);c.txt('Verify',xs[1],810);c.txt('Revise',xs[2],810)
    elif bid=='B12':
        twin(c,two=True)
        start=(430,555);end=(640,540)
        left=lerp(start,end,ease((u-.2)/.5))
        right=lerp((1450,535),(1220,580),ease((u-.2)/.5))
        c.ring(*left,78);c.ring(*right,78)
        c.arrow((855,520),(1060,520),GREY)
        c.txt('Zitiantao Lin',960,885,42)
    else:raise ValueError(bid)
    if bid in ('B02','B08'):c.txt('Received 24 Oct 2026',960,925,32)
    c.txt(footer,960,980,34)
    return c


def region_inventory(beat):
    # All authored text, including alternate action labels at other times.
    # Native diagrams and incidental text baked into supplied images are not type.
    regions=[];seen=set();dur=beat['actual_duration_s']
    for fraction in (0.,.12,.25,.4,.5,.6,.72,.85,.97):
        for item in render_frame(beat['beat_id'],dur*fraction,dur).texts:
            key=(item['label'],tuple(item['box']))
            if key not in seen:regions.append(item);seen.add(key)
    # Coalesce alternative labels occupying one location into the same bounded
    # inspection box: every region must contain the CURRENT label at midpoint.
    groups=[]
    for r in regions:
        x0,y0,x1,y1=r['box'];found=None
        for g in groups:
            a,b,d,e=g['box']
            if max(y0,b)<min(y1,e) and max(x0,a)<min(x1,d):found=g;break
        if found:
            found['box']=[min(x0,found['box'][0]),min(y0,found['box'][1]),max(x1,found['box'][2]),max(y1,found['box'][3])]
            if r['label'] not in found['label']:found['label']+=' / '+r['label']
        else:groups.append(dict(r))
    return groups


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()


def render_clip(beat, destination, height=1080, fps=24):
    executable=shutil.which('ffmpeg')
    if not executable:raise RuntimeError('ffmpeg is not on PATH')
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    duration=math.ceil(beat['actual_duration_s']*fps-1e-8)/fps
    frames=round(duration*fps);width=round(height*16/9/2)*2
    candidate=dest.with_name(dest.stem+'.candidate.mp4')
    log=dest.with_name(dest.stem+'.ffmpeg.log')
    cmd=[executable,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}',
         '-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18',
         '-pix_fmt','yuv420p','-movflags','+faststart','-frames:v',str(frames),str(candidate)]
    with log.open('wb') as err:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
        try:
            # Animation on twos: 12 drawn poses/sec, 24 fps video. Matches the
            # toolkit show-tell paper-cut cadence and reduces redundant drawing.
            for i in range(0,frames,2):
                image=render_frame(beat['beat_id'],i/fps,duration,height).im
                data=image.tobytes()
                proc.stdin.write(data)
                if i+1<frames:proc.stdin.write(data)
            proc.stdin.close()
            rc=proc.wait()
        except BaseException:
            if proc.poll() is None:proc.kill()
            proc.wait()
            raise
    if rc:raise RuntimeError(f'FFmpeg failed: {log.read_text(errors="replace")}')
    candidate.replace(dest)
    return {'beat_id':beat['beat_id'],'width':width,'height':height,'fps':fps,
            'frames':frames,'duration_s':duration,'sha256':digest(dest),
            'evidence':'constructed animation' if beat['beat_id'] not in ('B02','B08') else 'annotated supplied imagery'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=ROOT)
    ap.add_argument('--height',type=int,default=1080)
    ap.add_argument('--preview',action='store_true')
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--force',action='store_true')
    a=ap.parse_args();p=a.project.resolve()
    sheet=json.loads((p/'beat_sheet.json').read_text(encoding='utf-8-sig'))
    beats=[b for b in sheet['beats'] if not a.only or b['beat_id'] in a.only]
    preview=p/'previews';preview.mkdir(exist_ok=True)
    report=p/'reports';report.mkdir(exist_ok=True)
    inventory={}
    for beat in beats:
        duration=beat.get('actual_duration_s')
        if not isinstance(duration,(int,float)) or duration<=0:raise ValueError('Measured audio durations required')
        inventory[beat['beat_id']]=region_inventory(beat)
        render_frame(beat['beat_id'],duration*.5,duration,a.height).im.save(preview/(beat['beat_id']+'.png'))
    (report/'text-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    if a.preview:
        print(f'Previewed {len(beats)} original scenes; no narration or master generated.');return
    manifest_path=report/'visual-render.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for beat in beats:
        bid=beat['beat_id'];dest=p/'media'/(bid+'.mp4')
        cached=manifest.get(bid,{})
        duration=math.ceil(beat['actual_duration_s']*24-1e-8)/24
        if not a.force and dest.exists() and cached.get('height')==a.height and cached.get('duration_s')==duration and cached.get('sha256')==digest(dest):
            print(f'[draw] {bid}: retained verified cached media',flush=True);continue
        print(f'[draw] {bid}: rendering {duration:.3f}s at {a.height}p',flush=True)
        manifest[bid]=render_clip(beat,dest,a.height)
        manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Visual slots ready. Run the original Brutalist compiler with the actual narration next.')


if __name__=='__main__':main()
